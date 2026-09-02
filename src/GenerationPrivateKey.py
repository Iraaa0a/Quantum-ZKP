from qiskit import (
    QuantumCircuit,
    QuantumRegister,
    ClassicalRegister,
    transpile
)
from qiskit_aer import AerSimulator
import numpy as np


def GenerationPrivateKey(n_qubits=256):

    qc = QuantumCircuit(n_qubits, n_qubits)

    # Hadamard ко всем кубитам
    for i in range(n_qubits):
        qc.h(i)

    # Измерение
    qc.measure(range(n_qubits), range(n_qubits))

    simulator = AerSimulator()

    job = simulator.run(qc, shots=1)

    result = job.result()
    counts = result.get_counts()

    bitstring = list(counts.keys())[0]

    private_key = [int(bit) for bit in bitstring][::-1]

    return private_key
