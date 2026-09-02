from qiskit import (
    QuantumCircuit,
    QuantumRegister,
    ClassicalRegister,
    transpile
)
from qiskit_aer import AerSimulator
import numpy as np


def GenerationPublicKey(private_key):

    n_pairs = len(private_key)

    qc_public = QuantumCircuit(2 * n_pairs, n_pairs)

    for i in range(n_pairs):

        if private_key[i] == 1:
            qc_public.x(i + n_pairs)

    for i in range(n_pairs):

        qc_public.h(i)
        qc_public.cx(i, i + n_pairs)

    for i in range(n_pairs):

        qc_public.measure(i + n_pairs, i)

    simulator = AerSimulator(method="stabilizer")

    job = simulator.run(qc_public, shots=1)

    result = job.result()
    counts = result.get_counts()

    bitstring = list(counts.keys())[0]

    public_key = [int(bit) for bit in bitstring][::-1]

    return public_key
