"""
GPG Module 
    - generates passphrase to secure private key. 
    - generates private/public key pair.
    - decrypts files encrypted with the public key.
"""

import shutil
import gnupg
import secrets
import string
import tempfile
import subprocess
from clients.logger_client import gpg_logger

def generate_passphrase() -> str:
    # Generate random 32 characters passphrase.
    characters = string.digits + string.ascii_letters + string.punctuation
    passphrase = "".join(secrets.choice(characters) for i in range(32))
    return passphrase

def generate_gpg_key(email: str) -> tuple[str, str, str]:
    # Generates pgp key pair.

    # initialize GPG and specify temp dir as homedir.
    gpg_home = tempfile.mkdtemp()
    gpg = gnupg.GPG(gnupghome=gpg_home)

    # Generate passphrase.
    passphrase = generate_passphrase()

    # Generate key pair.
    input_data = gpg.gen_key_input(name_email=email, name_real="output-file-key", passphrase=passphrase, key_type="EDDSA", key_curve="ed25519", subkey_type="ecdh", subkey_curve="cv25519", expire_date="2y")
    key = gpg.gen_key(input_data)

    # Log key generation.
    # gpg_logger.info(f"GPG KeyPair generated.")
    gpg_logger.log("GPG KeyPair generated.")
    
    # Exports private (secured) and public keys.
    private_key = gpg.export_keys(key.fingerprint, True, passphrase=passphrase)
    public_key = gpg.export_keys(key.fingerprint)

    # deletes temp dir.
    shutil.rmtree(gpg_home)

    # returns keypair and passphrase.
    return private_key, public_key, passphrase

def decrypt_gpg_file(private_key: str, passphrase: str, encrypted_file_path: str) -> gnupg.Crypt:
    # initialize GPG and specify temp dir as home dir.
    gpg_home = tempfile.mkdtemp()
    gpg = gnupg.GPG(gnupghome=gpg_home)

    # Import and trust keys.
    import_result = gpg.import_keys(private_key)
    gpg.trust_keys(import_result.fingerprints, "TRUST_ULTIMATE")

    # Decrypt file and print status.
    with open(encrypted_file_path, "rb") as f:
        plaintext_data = gpg.decrypt_file(f, passphrase=passphrase)
        # gpg_logger.info(f"File decrypted with GPG Private key.")
        gpg_logger.log("File decrypted with GPG Private key.")

    # Clearing cache to ensure the gpg-agent does not cache the correct passphrase.
    # Could lead to a backdoor where a malicious user only has to put in any
    # passphrase to decrypt the data. Check warning under the decryption section 
    # of the documentation - https://gnupg.readthedocs.io/en/latest/#decryption.
    cli_command = "echo RELOADAGENT | gpg-connect-agent"
    subprocess.run(cli_command, shell=True, text=True, stdout=subprocess.DEVNULL)
    # gpg_logger.info(f"Cleared gpg-agent cache to prevent passphrase caching.")
    gpg_logger.log("File decrypted with GPG Private key.")
    
    # delete temp dir.
    shutil.rmtree(gpg_home)

    # returns decrypted data.
    return plaintext_data
