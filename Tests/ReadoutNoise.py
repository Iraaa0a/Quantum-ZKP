from qiskit import (
    QuantumCircuit,
    QuantumRegister,
    ClassicalRegister
)

from qiskit_aer import AerSimulator

from qiskit_aer.noise import (
    NoiseModel,
    ReadoutError
)

import matplotlib.pyplot as plt
import numpy as np

import matplotlib.pyplot as plt

from src.GenerationPrivateKey import GenerationPrivateKey
from src.GenerationPublicKey import GenerationPublicKey
from src.Proof import Proof


def CreateReadoutNoise(p=0.02):

    error_matrix = [
        [1 - p, p],
        [p, 1 - p]
    ]

    readout_error = ReadoutError(error_matrix)

    noise_model = NoiseModel()

    noise_model.add_all_qubit_readout_error(
        readout_error
    )

    return noise_model


def GenerationPrivateKey(n_qubits=8):

    qc = QuantumCircuit(
        n_qubits,
        n_qubits
    )

    # Hadamard
    for i in range(n_qubits):
        qc.h(i)

    # Измерение
    qc.measure(
        range(n_qubits),
        range(n_qubits)
    )

    simulator = AerSimulator(
        method="stabilizer"
    )

    job = simulator.run(
        qc,
        shots=1
    )

    result = job.result()
    counts = result.get_counts()

    bitstring = list(
        counts.keys()
    )[0]

    private_key = [
        int(bit)
        for bit in bitstring
    ][::-1]

    return private_key


def GenerationPublicKey(private_key):

    n_pairs = len(private_key)

    qc_public = QuantumCircuit(
        2 * n_pairs,
        n_pairs
    )

    # Инициализация
    for i in range(n_pairs):

        if private_key[i] == 1:
            qc_public.x(i + n_pairs)

    # Белловские пары
    for i in range(n_pairs):

        qc_public.h(i)
        qc_public.cx(i, i + n_pairs)

    # Измерение
    for i in range(n_pairs):

        qc_public.measure(
            i + n_pairs,
            i
        )

    simulator = AerSimulator(
        method="stabilizer"
    )

    job = simulator.run(
        qc_public,
        shots=1
    )

    result = job.result()
    counts = result.get_counts()

    bitstring = list(
        counts.keys()
    )[0]

    public_key = [
        int(bit)
        for bit in bitstring
    ][::-1]

    return public_key


# The noise is only here

def Proof(
    private_key,
    public_key,
    noise_model=None
):

    n_pairs = len(private_key)

    first_line_reference = [

        a ^ b

        for a, b in zip(
            private_key,
            public_key
        )
    ]

    qreg = QuantumRegister(
        2 * n_pairs,
        "q"
    )

    creg_first = ClassicalRegister(
        n_pairs,
        "m1"
    )

    creg_second = ClassicalRegister(
        n_pairs,
        "m2"
    )

    qc_mid = QuantumCircuit(
        qreg,
        creg_first,
        creg_second
    )

    # Инициализация
    for i in range(n_pairs):

        if private_key[i] == 1:
            qc_mid.x(i + n_pairs)

    # Белловские пары
    for i in range(n_pairs):

        qc_mid.h(i)
        qc_mid.cx(i, i + n_pairs)

    # Первое измерение
    for i in range(n_pairs):

        qc_mid.measure(
            i,
            creg_first[i]
        )

    # Условные операции
    for i in range(n_pairs):

        expected_value = (
            1 -
            first_line_reference[i]
        )

        with qc_mid.if_test(
            (creg_first[i], expected_value)
        ):
            qc_mid.x(i + n_pairs)

    # Финальное измерение
    for i in range(n_pairs):

        qc_mid.measure(
            i + n_pairs,
            creg_second[i]
        )

    # STATEVECTOR
    simulator = AerSimulator(
        method="statevector"
    )

    job = simulator.run(
        qc_mid,
        shots=1,
        noise_model=noise_model
    )

    result = job.result()
    counts = result.get_counts()

    bitstring = list(
        counts.keys()
    )[0]

    parts = bitstring.split(" ")

    second_row_bits = parts[0]

    final_key = [
        int(bit)
        for bit in second_row_bits
    ][::-1]

    # Accuracy
    matches = sum(

        a == b

        for a, b in zip(
            final_key,
            public_key
        )
    )

    accuracy = (
        matches /
        len(public_key)
    )

    return accuracy


# Accuracy vs number of qubits

qubit_sizes = range(1, 12, 1)

# noise
noise_probability = 0.10

# noise model
noise_model = CreateReadoutNoise(
    noise_probability
)

# количество запусков
n_runs = 100

# результаты
mean_accuracies = []

print("\n========== TEST 1 ==========")

for n_bits in qubit_sizes:

    print(f"Qubits: {n_bits}")

    accuracies = []

    for _ in range(n_runs):

        # БЕЗ ШУМА
        private_key = GenerationPrivateKey(
            n_bits
        )

        public_key = GenerationPublicKey(
            private_key
        )

        # ШУМ ТОЛЬКО В PROOF
        accuracy = Proof(
            private_key,
            public_key,
            noise_model
        )

        accuracies.append(
            accuracy
        )

    mean_accuracy = np.mean(
        accuracies
    )

    mean_accuracies.append(
        mean_accuracy
    )

    print(
        f"Mean accuracy: "
        f"{mean_accuracy:.4f}"
    )


# Graph 1

plt.figure(figsize=(12, 6))

plt.plot(
    list(qubit_sizes),
    mean_accuracies,
    marker='o',
    linewidth=3,
    markersize=8
)

plt.xlabel(
    "Количество кубитов",
    fontsize=14
)

plt.ylabel(
    "Accuracy",
    fontsize=14
)

plt.title(
    "Accuracy vs Qubits",
    fontsize=16
)

plt.grid(
    True,
    linestyle='--',
    alpha=0.6
)

plt.ylim(0, 1.05)

plt.tight_layout()

plt.show()


# Graph 2
# Accuracy vs Noise Probability

n_bits = 11

noise_probs = np.linspace(
    0.0,
    0.30,
    10
)

noise_accuracies = []

print("\n========== TEST 2 ==========")

for p in noise_probs:

    print(f"Noise probability: {p:.2f}")

    noise_model = CreateReadoutNoise(p)

    accuracies = []

    for _ in range(n_runs):

        private_key = GenerationPrivateKey(
            n_bits
        )

        public_key = GenerationPublicKey(
            private_key
        )

        accuracy = Proof(
            private_key,
            public_key,
            noise_model
        )

        accuracies.append(
            accuracy
        )

    mean_accuracy = np.mean(
        accuracies
    )

    noise_accuracies.append(
        mean_accuracy
    )

    print(
        f"Mean accuracy: "
        f"{mean_accuracy:.4f}"
    )


# Graph 2

plt.figure(figsize=(12, 6))

plt.plot(
    noise_probs,
    noise_accuracies,
    marker='o',
    linewidth=3,
    markersize=8
)

plt.xlabel(
    "Probabity of readout noise",
    fontsize=14
)

plt.ylabel(
    "Accuracy",
    fontsize=14
)

plt.title(
    "Accuracy vs Noise Probability",
    fontsize=16
)

plt.grid(
    True,
    linestyle='--',
    alpha=0.6
)

plt.ylim(0, 1.05)

plt.tight_layout()

plt.show()
