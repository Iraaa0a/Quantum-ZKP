from qiskit import (
    QuantumCircuit,
    QuantumRegister,
    ClassicalRegister,
    transpile
)
from qiskit_aer import AerSimulator
import numpy as np


def Proof(private_key, public_key):

    n_pairs = len(private_key)

    first_line_reference = [
        a ^ b
        for a, b in zip(private_key, public_key)
    ]

    qreg = QuantumRegister(2 * n_pairs, "q")

    creg_first = ClassicalRegister(n_pairs, "m1")
    creg_second = ClassicalRegister(n_pairs, "m2")

    qc_mid = QuantumCircuit(
        qreg,
        creg_first,
        creg_second
    )

    for i in range(n_pairs):

        if private_key[i] == 1:
            qc_mid.x(i + n_pairs)

    for i in range(n_pairs):

        qc_mid.h(i)
        qc_mid.cx(i, i + n_pairs)

    for i in range(n_pairs):

        qc_mid.measure(i, creg_first[i])

    for i in range(n_pairs):

        expected_value = 1 - first_line_reference[i]

        with qc_mid.if_test((creg_first[i], expected_value)):
            qc_mid.x(i + n_pairs)

    for i in range(n_pairs):

        qc_mid.measure(
            i + n_pairs,
            creg_second[i]
        )

    simulator = AerSimulator(method="stabilizer")

    job = simulator.run(
        qc_mid,
        shots=1
    )

    result = job.result()
    counts = result.get_counts()

    bitstring = list(counts.keys())[0]

    parts = bitstring.split(" ")

    second_row_bits = parts[0]
    first_row_bits = parts[1]

    first_measurement = [
        int(bit)
        for bit in first_row_bits
    ][::-1]

    final_key = [
        int(bit)
        for bit in second_row_bits
    ][::-1]

    # Correlation between final_key and public_key

    matches = sum(a == b for a, b in zip(final_key, public_key))
    accuracy = matches / len(public_key)

    hex_final_key = hex(int(''.join(map(str, final_key)), 2))[2:].zfill(64)
    hex_public_key = hex(int(''.join(map(str, public_key)), 2))[2:].zfill(64)

    return {
        "final_key": hex_final_key,
        "public_key": hex_public_key,
        "accuracy": accuracy
    }
