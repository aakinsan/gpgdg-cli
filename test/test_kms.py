import pytest
import logging
from clients.kms_client import encrypt_passphrase, decrypt_passphrase

@pytest.fixture
def mock_kms_encrypt(mocker):
    return mocker.patch('google.cloud.kms_v1.KeyManagementServiceClient.encrypt')

@pytest.fixture
def mock_kms_decrypt(mocker):
    return mocker.patch('google.cloud.kms_v1.KeyManagementServiceClient.decrypt')

def test_encrypt_passphrase(mock_kms_encrypt):
    logging.disable(logging.CRITICAL)
    mock_kms_encrypt.return_value.ciphertext = b'encrypted_data'
    ciphertext = encrypt_passphrase("my_project_id", "my_keyring", "my_key_name", "my_passphrase")
    assert ciphertext == b'encrypted_data'

def test_decrypt_data(mock_kms_decrypt):
    mock_kms_decrypt.return_value.plaintext = b'secret_data'
    plaintext = decrypt_passphrase("my_project_id", "my_keyring", "my_key_name", "my_passphrase")
    assert plaintext == b'secret_data'

