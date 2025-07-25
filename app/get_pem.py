import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import dotenv


dotenv.load_dotenv()

# Load PEM from file
with open(os.environ['PEM_LOCATION'], "rb") as f:
    pem_bytes = f.read()

# Deserialize private key
private_key = serialization.load_pem_private_key(
    pem_bytes,
    password=None,
    backend=default_backend()
)

# Extract private key as hex string (32 bytes)
privkey_bytes = private_key.private_numbers().private_value.to_bytes(32, 'big')
privkey_hex = privkey_bytes.hex()

print("Private key hex:", privkey_hex)
