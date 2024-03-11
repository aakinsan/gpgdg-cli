import os
import shutil
import gnupg
import secrets
import string
import tempfile
import subprocess
from clients.logger_client import gpg_logger

def generate_passphrase():
    # Generate Random 32 characters Passphrase
    characters = string.digits + string.ascii_letters + string.punctuation
    passphrase = "".join(secrets.choice(characters) for i in range(32))
    return passphrase

def generate_gpg_key(email):
    # initialize GPG and specify temp dir as home dir
    gpg_home = tempfile.mkdtemp()
    gpg_logger.info(f"Generated temp dir for gpg key pair")
    gpg = gnupg.GPG(gnupghome=gpg_home)

    # Generate Passphrase
    passphrase = generate_passphrase()

    # Generate key
    input_data = gpg.gen_key_input(name_email=email, name_real="output-file-key", passphrase=passphrase, key_type="EDDSA", key_curve="ed25519", subkey_type="ecdh", subkey_curve="cv25519", expire_date="2y")
    key = gpg.gen_key(input_data)

    # Log Key Generation
    gpg_logger.info(f"GPG KeyPair generated.")
    
    # Export private & public keys
    private_key = gpg.export_keys(key.fingerprint, secret=True, passphrase=passphrase)
    public_key = gpg.export_keys(key.fingerprint)

    # delete temp dir
    shutil.rmtree(gpg_home)
    gpg_logger.info(f"Deleted temp dir for gpg key pair")

    return private_key, public_key, passphrase

def decrypt_file(private_key, passphrase, encrypted_file_path):
    # initialize GPG and specify temp dir as home dir
    gpg_home = tempfile.mkdtemp()
    gpg = gnupg.GPG(gnupghome=gpg_home)

    # Import and trust keys
    import_result = gpg.import_keys(private_key)
    gpg.trust_keys(import_result.fingerprints, "TRUST_ULTIMATE")

    # Decrypt file and print status.
    with open(encrypted_file_path, "rb") as f:
        plaintext_data = gpg.decrypt_file(f, passphrase=passphrase)
        gpg_logger.info(f"File decrypted with GPG Private key.")

    # Clearing cache to ensure the gpg-agent does not cache the passphrase.
    # Could lead to a backdoor where a malicious user only has to put in any
    # passphrase to decrypt the data. Check warning under the decryption section 
    # of the documentation - https://gnupg.readthedocs.io/en/latest/#decryption
    cli_command = "echo RELOADAGENT | gpg-connect-agent"
    subprocess.run(cli_command, shell=True, text=True)
    gpg_logger.info(f"Cleared gpg-agent cache to prevent passphrase caching.")
    
    # delete temp dir
    shutil.rmtree(gpg_home)

    return plaintext_data
