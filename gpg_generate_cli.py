"""
gpg_generate_cli - entry program for keypair generation and storage in secrets manager.
    - Generates private key, public key and passphrase.
    - Exports passphrase protected private key and public key.
    - Calls Cloud KMS to encrypt passphrase. 
    - Stores encrypted passphrase and password protected private key in secrets manager.
    - decrypts output file using private key.
    - Writes the public key to disk. 
"""

from absl import app
from absl import flags
import sys
from clients.logger_client import gpg_logger
from clients.gpg_client import generate_gpg_key
from clients.kms_client import encrypt_passphrase
from clients.secrets_client import create_secret, add_secret_version
from clients.storage_client import write_public_key_to_disk
from google.api_core.exceptions import AlreadyExists, PermissionDenied, DeadlineExceeded

# Assigning FlagValues Object to FLAGS
FLAGS = flags.FLAGS

# Define cli flags.
flags.DEFINE_string("kms_key", None, "The cloud KMS key name of the KEK.")
flags.DEFINE_string("kms_kring", None, "The cloud KMS keyring name of the KEK.")
flags.DEFINE_string("email_id", None, "The email assigned to the GPG key.")
flags.DEFINE_string("privkey_sid", None, "Secret ID of the GPG Private Key in secrets manager.")
flags.DEFINE_string("pass_sid", None, "Secret ID of the encrypted passphrase in secrets manager.")
flags.DEFINE_string("project_id", None, "The GCP project ID.")

def main(argv):

    # Delete unused argument
    del argv 

    # Generate GPG private key, public key and passphrase.
    private_key, public_key, passphrase = generate_gpg_key(FLAGS.email_id)
    
    # Call GCP Cloud KMS to encrypt passphrase.
    encrypted_passphrase = encrypt_passphrase(FLAGS.project_id, FLAGS.kms_kring, FLAGS.kms_key, passphrase)

    # Create encrypted passphrase secret object and version in GCP secret manager if one has not been created.
    try:
        create_secret(FLAGS.project_id, FLAGS.pass_sid)
        add_secret_version(FLAGS.project_id, FLAGS.pass_sid, encrypted_passphrase)

    # If secret already exists, add a newer version.
    except AlreadyExists:
        add_secret_version(FLAGS.project_id, FLAGS.pass_sid, encrypted_passphrase)

    # Create private key secret object and version in GCP secret manager if one has not been created.
    try: 
        create_secret(FLAGS.project_id, FLAGS.privkey_sid)
        private_key = private_key.encode("UTF-8")
        add_secret_version(FLAGS.project_id, FLAGS.privkey_sid, private_key)

    # If secret already exists, add a newer version.
    except AlreadyExists:
        private_key = private_key.encode("UTF-8")
        add_secret_version(FLAGS.project_id, FLAGS.privkey_sid, private_key)

    # Write public key to disk.
    write_public_key_to_disk(public_key)

# Check if script is run directly.
if __name__ == "__main__":

    # Specify mandatory cli flags.
    flags.mark_flags_as_required(["email_id", "project_id", "kms_key", "kms_kring", "privkey_sid", "pass_sid"])
    
    try:
        # Run script
        app.run(main)

    except AlreadyExists as err:
        gpg_logger.error(f"An error occured: the gcp resource already exists: {err}: Exiting...")
        sys.exit(1)
        
     # Catch exceptions.
    except PermissionDenied as err:
        gpg_logger.error(f"not enough permission: {err}: Exiting...")
        sys.exit(1)

    except DeadlineExceeded as err:
        gpg_logger.error(f"communication failure on server side - retry gpg_generate_cli: {err}: Exiting...")
        sys.exit(1)
    
    except Exception as err:
        gpg_logger.error(f"An error occured: {err}: Exiting...")
        sys.exit(1)
