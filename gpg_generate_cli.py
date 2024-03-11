from absl import app
from absl import flags
import sys
from clients.logger_client import gpg_logger
from clients.gpg_client import generate_gpg_key
from clients.kms_client import encrypt_passphrase
from clients.secrets_client import create_secret, add_secret
from clients.storage_client import write_public_key_to_disk
from google.api_core.exceptions import AlreadyExists, PermissionDenied, DeadlineExceeded

# Assigning FlagValues Object to FLAGS
FLAGS = flags.FLAGS

# Define flags
flags.DEFINE_string("kms_key", None, "The cloud KMS key name of the KEK.")
flags.DEFINE_string("kms_keyring", None, "The cloud KMS keyring name of the KEK.")
flags.DEFINE_string("email_id", None, "The email assigned to the GPG key.")
flags.DEFINE_string("private_key_id", None, "Secret ID of the GPG Private Key in secrets manager.")
flags.DEFINE_string("passphrase_id", None, "Secret ID of the encrypted passphrase in secrets manager.")
flags.DEFINE_string("project_id", None, "The GCP project ID.")

def main(argv):

    # Delete unused argument
    del argv 

    # Generate GPG private key, public key and passphrase
    private_key, public_key, passphrase = generate_gpg_key(FLAGS.email_id)
    
    # Encrypt passphrase with GCP cloud KMS key.
    encrypted_passphrase = encrypt_passphrase(FLAGS.project_id, FLAGS.kms_keyring, FLAGS.kms_key, passphrase)

    # Create encrypted passphrase secret object in GCP secret manager.
    create_secret(FLAGS.project_id, FLAGS.passphrase_id)

    # Add encrypted passphrase secret version to GCP secret manager
    add_secret(FLAGS.project_id, FLAGS.passphrase_id, encrypted_passphrase)

    # Create private key secret object to GCP secret manager.
    create_secret(FLAGS.project_id, FLAGS.private_key_id)

    # Add private key secret version to GCP secret manager
    private_key = private_key.encode("UTF-8")
    add_secret(FLAGS.project_id, FLAGS.private_key_id, private_key)

    # Create Public Key File
    write_public_key_to_disk(public_key)

if __name__ == "__main__":

    # Mark required flags
    flags.mark_flags_as_required(["email_id", "project_id", "kms_key", "kms_keyring", "private_key_id", "passphrase_id"])
    
    try:
        app.run(main)

    except AlreadyExists as err:
        gpg_logger.error(f"An error occured: the gcp resource already exists: {err}: Exiting...")
        sys.exit(1)
    
    except PermissionDenied as err:
        gpg_logger.error(f"not enough permission: {err}: Exiting...")
        sys.exit(1)

    except DeadlineExceeded as err:
        gpg_logger.error(f"communication failure on server side - retry gpg_generate_cli: {err}: Exiting...")
        sys.exit(1)
    
    except Exception as err:
        gpg_logger.error(f"An error occured: {err}: Exiting...")
        sys.exit(1)
