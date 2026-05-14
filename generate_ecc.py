import argparse
import hashlib
from Crypto.PublicKey import ECC

class DeterministicPRNG:
    def __init__(self, seed_string):
        self.seed = seed_string.encode()
        self.counter = 0

    def __call__(self, n_bytes):
        result = bytearray()
        while len(result) < n_bytes:
            data_to_hash = self.seed + str(self.counter).encode()
            result.extend(hashlib.sha256(data_to_hash).digest())
            self.counter += 1
        return bytes(result[:n_bytes])

def generate_ecc_keys(seed):
    print("Initializing deterministic ECC key generation...")
    
    prng = DeterministicPRNG(seed)
    key = ECC.generate(curve='P-256', randfunc=prng)

    with open("ecc_private_key.pem", "wt") as f:
        f.write(key.export_key(format='PEM'))

    with open("ecc_public_key.pem", "wt") as f:
        f.write(key.public_key().export_key(format='PEM'))

    print("Key pair generated and saved successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--seed", required=True)
    args = parser.parse_args()
    
    generate_ecc_keys(args.seed)