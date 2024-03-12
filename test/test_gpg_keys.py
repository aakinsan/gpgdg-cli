import pytest
import shutil
import logging
import tempfile
import gnupg
from clients.gpg_client import generate_gpg_key, decrypt_gpg_file

@pytest.fixture(scope="module")
def email():
    return "user@example.com"

@pytest.fixture(scope="module")
def data():
    # Plaintext secret message
    return "This is a secret message"

@pytest.fixture(scope="module")
def keys(email):
    # suppress logging to gcp logging explorer.
    logging.disable(logging.CRITICAL)
    
    # Generate GPG key pair and passphrase using the generate_gpg_key function
    private_key, public_key, passphrase = generate_gpg_key(email)

    # return keypair and passphrase
    return private_key, public_key, passphrase

@pytest.fixture(scope="module")
def gpg(keys):
    
    # Create temp dir
    gpg_home = tempfile.mkdtemp()

    # initialize new gpg instance
    gpg = gnupg.GPG(gnupghome=gpg_home)

    # Get private key
    private_key, public_key, passphrase = keys
    
    # import private key into new gpg instance
    import_result = gpg.import_keys(private_key)
    gpg.trust_keys(import_result.fingerprints, "TRUST_ULTIMATE")
    
    # Return gpg instance
    yield gpg

    # Delete temp dir
    shutil.rmtree(gpg_home)

def test_keypair_validity(keys):
    # Get GPG keypair and passphrase are generated
    private_key, public_key, passphrase = keys

    # Validate gpg keypair and passphrase are generated
    assert private_key is not None
    assert public_key is not None
    assert passphrase is not None

def test_encrypt_decrypt_data(keys, gpg, data, email):
    
    # Get keypair and passphrase
    private_key, public_key, passphrase = keys

    # Encrypt data with private key using the new gpg instance
    encrypted_data = gpg.encrypt(data, email)

    # decrypt data with new gpg instance
    decrypted_data = gpg.decrypt(str(encrypted_data), passphrase=passphrase)

    # validate data decrypted is the original data message
    assert data == str(decrypted_data)

def test_decrypt_file(keys, gpg, data, email):
    private_key, public_key, passphrase = keys

    # Create temporary plaintext file
    temp_file = tempfile.NamedTemporaryFile()
    temp_file.write(data.encode("UTF-8"))
    temp_file.seek(0)

    # Encrypt file with gpg instance
    encrypted_data = gpg.encrypt_file(temp_file, email)
    assert encrypted_data.ok == True

    # Write encrypted data to a temporary file
    encrypted_temp_file = tempfile.NamedTemporaryFile()
    encrypted_temp_file.write(str(encrypted_data).encode("UTF-8"))
    encrypted_temp_file.seek(0)

    # Call decrypt_gpg_file function to decrypt encrypted file.
    plaintext_data = decrypt_gpg_file(private_key, passphrase, encrypted_temp_file.name)
    assert plaintext_data.ok == True

    # validate decrypted data is the original data on file.
    assert plaintext_data.data.decode("UTF-8") == data

    # Validate the correct passphrases are not cached.
    bad_passphrase = "a bad passphrase"
    bad_plaintext = decrypt_gpg_file(private_key, bad_passphrase, encrypted_temp_file.name)
    assert bad_plaintext.data.decode("UTF-8") != data
    


