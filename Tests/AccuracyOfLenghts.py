# Checking accuracy for different key lengths

import matplotlib.pyplot as plt

from src.GenerationPrivateKey import GenerationPrivateKey
from src.GenerationPublicKey import GenerationPublicKey
from src.Proof import Proof

bit_sizes = []
accuracy_values = []

for n_bits in range(1, 1025, 8):

    print(f"Chek for {n_bits} bit")

    # Генерация ключей
    private_key = GenerationPrivateKey(n_bits)

    public_key = GenerationPublicKey(private_key)

    proof_result = Proof(private_key, public_key)

    bit_sizes.append(n_bits)
    accuracy_values.append(proof_result["accuracy"])

plt.figure(figsize=(12, 6))

plt.plot(
    bit_sizes,
    accuracy_values,
    marker='o'
)

plt.xlabel("Количество бит ключа")
plt.ylabel("Accuracy")

plt.title("Зависимость Accuracy от размера ключа")

plt.grid(True)

plt.show()
