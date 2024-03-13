"""
Cloud KMS Module 
    - calls cloud KMS to encrypt and decrypt the passphrase (generated to secure the private key).
"""

from google.cloud import kms_v1
from clients.logger_client import gpg_logger

def encrypt_passphrase(project_id: str, keyring_name: str, key_name: str, payload: str) -> bytes:
    # Encrypts passphrase.

    # Initialize KMS client.
    client = kms_v1.KeyManagementServiceClient()

    # Build crypto key-path to kms key.
    location="global"
    key_path = client.crypto_key_path(project_id, location, keyring_name, key_name)

    # Encrypt payload (passphrase).
    payload_bytes = payload.encode("UTF-8")
    request = {"name": key_path, "plaintext": payload_bytes}
    response = client.encrypt(request=request)

    # Log message.
    gpg_logger.info(f"Passphrase encrypted with Cloud KMS key.")


    # Return encrypted passphrase.
    return response.ciphertext

def decrypt_passphrase(project_id: str, keyring_name: str, key_name: str, encrypted_payload: bytes) -> bytes:
    # Decrypts passphrase.

    # Initialize KMS client.
    client = kms_v1.KeyManagementServiceClient()

# Build crypto key-path.
    location="global"
    key_path = client.crypto_key_path(project_id, location, keyring_name, key_name)

    # Decrypt payload (passphrase).
    request = {"name": key_path, "ciphertext": encrypted_payload}
    response = client.decrypt(request=request)

    # Log Message.
    gpg_logger.info(f"Passphrase decrypted with Cloud KMS key.")
    
    # Return decrypted passphrase.
    return response.plaintext
