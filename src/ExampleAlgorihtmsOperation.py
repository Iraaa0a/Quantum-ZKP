import GenerationPrivateKey as GenerationPrivateKey
import GenerationPublicKey as GenerationPublicKey
import Proof as Proof

private_key = GenerationPrivateKey.GenerationPrivateKey(256)

public_key = GenerationPublicKey.GenerationPublicKey(private_key)

proof_result = Proof.Proof(private_key, public_key)

print("Public key:")
print(proof_result["public_key"])

print("\nFinal key:")
print(proof_result["final_key"])

print("\nAccuracy:")
print(proof_result["accuracy"])
