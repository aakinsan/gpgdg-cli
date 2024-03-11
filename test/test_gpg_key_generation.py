import os
import re
import pytest
import shutil
import logging
import string
import secrets
import tempfile
import subprocess
import gnupg

from clients.gpg_client import generate_gpg_key, decrypt_file

# Decorator to suppress logging during tests
def disable_logging(f):
    def wrapper(*args):
        logging.disable(logging.CRITICAL)
        result = f(*args)
        logging.disable(logging.NOTSET)
        return result
    return wrapper

@pytest.fixture(scope="module")
def gpg_obj():
    # Create temp dir
    gpg_home = tempfile.mkdtemp()
    gpg = gnupg.GPG(gnupghome=gpg_home)
    yield gpg
    shutil.rmtree(gpg_home)

@pytest.fixture(scope="module")
@disable_logging
def gpg_keys():
    # Generate GPG key pair and passphrase
    email = "test@contoso.com"
    private_key, public_key, passphrase = generate_gpg_key(email)
    return {"private_key": private_key, "public_key": public_key, "passphrase": passphrase}

def test_keypair_validity(gpg_keys):
     # Validate GPG key pair and passphrase are generated
     assert gpg_keys["private_key"] is not None
     assert gpg_keys["public_key"] is not None

def test_passphrase_validity(gpg_keys):
     # validate passphrase is 32 characters and is a mix of alphabets, digits, and special characters
     pattern = r"^(?=.*[a-zA-Z])(?=.*\d)(?=.*[@#$%^&+=]).{32}$"
     # pattern2 = r"^(?=.*[a-zA-Z])(?=.*\d)(?=.*[!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~]).{32}$"
     assert re.match(pattern, gpg_keys["passphrase"])
     assert gpg_keys["passphrase"] is not None

def test_encrypt_decrypt_data(gpg_keys, gpg_obj):
     email = "test@contoso.com"
     data = "This is a secret message"
     
     # import private key into gpg instance
     import_result = gpg_obj.import_keys(gpg_keys["private_key"])
     gpg_obj.trust_keys(import_result.fingerprints, "TRUST_ULTIMATE")
     
     # Encrypt data
     encrypted_data = gpg_obj.encrypt(data, email)

     # decrypt data
     decrypted_data = gpg_obj.decrypt(str(encrypted_data), passphrase=gpg_keys["passphrase"])

     # validate decrypted data is data
     assert data == str(decrypted_data)
