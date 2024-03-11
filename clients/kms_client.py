from google.cloud import kms_v1
from clients.logger_client import gpg_logger

def encrypt_passphrase(project_id, keyring_name, key_name, payload):
    # Initialize KMS client
    client = kms_v1.KeyManagementServiceClient()

    # Build crypto key path
    location="global"
    key_path = client.crypto_key_path(project_id, location, keyring_name, key_name)

    # Encrypt payload.
    payload_bytes = payload.encode("UTF-8")
    request = {"name": key_path, "plaintext": payload_bytes}
    response = client.encrypt(request=request)

    # Log message
    gpg_logger.info(f"Passphrase encrypted with Cloud KMS key.")

    return response.ciphertext

def decrypt_passphrase(project_id, keyring_name, key_name, encrypted_payload):
    # Initialize KMS client.
    client = kms_v1.KeyManagementServiceClient()

# Build crypto key path
    location="global"
    key_path = client.crypto_key_path(project_id, location, keyring_name, key_name)

    # Decrypt payload.
    request = {"name": key_path, "ciphertext": encrypted_payload}
    response = client.decrypt(request=request)

    # Log Message
    gpg_logger.info(f"Passphrase decrypted with Cloud KMS key.")
    
    return response.plaintext
