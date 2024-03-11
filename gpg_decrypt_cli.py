from absl import app
from absl import flags
import sys
from clients.logger_client import gpg_logger
from clients.gpg_client import decrypt_file
from clients.kms_client import decrypt_passphrase
from clients.secrets_client import get_secret
from clients.storage_client import write_output_file_to_disk, write_output_file_to_bucket
from google.api_core.exceptions import PermissionDenied, DeadlineExceeded

# Assigning FlagValues Object to FLAGS
FLAGS = flags.FLAGS

# Validation Function to ensure either a storage bucket or disk location is chosen to store output files
def validate_storage_location(flags_dict):
    if flags_dict["bucket_name"] and flags_dict["decrypt_file_path"]:
        raise ValueError("Specify either a bucket name or path on disk to store output file")
    elif flags_dict["bucket_name"] is None and flags_dict["decrypt_file_path"] is None:
        raise ValueError("Specify either a bucket name or path on disk to store output file")
    else:
        return True

# Define flags
flags.DEFINE_string("kms_key", None, "The cloud KMS key name of the KEK.")
flags.DEFINE_string("kms_keyring", None, "The cloud KMS keyring name of the KEK.")
flags.DEFINE_string("private_key_id", None, "Secret ID of the GPG Private Key in secrets manager.")
flags.DEFINE_string("passphrase_id", None, "Secret ID of the encrypted passphrase in secrets manager.")
flags.DEFINE_string("project_id", None, "The GCP project ID.")
flags.DEFINE_string("encrypted_file_path", None, "Path to GPG encrypted file location on disk.")
flags.DEFINE_string("decrypt_file_path", None, "Path to write GPG decrypted file on disk.")
flags.DEFINE_string("bucket_name", None, "Path to write GPG decrypted blob to cloud storage bucket.")

# Validate Storage Location Flag
flags.register_multi_flags_validator(['bucket_name', "decrypt_file_path"], validate_storage_location)

def main(argv):

    # Delete unused argument
    del argv

    # Get (version "1") private key and encrypted passphrase from GCP secret manager.
    private_key = get_secret(FLAGS.project_id, FLAGS.private_key_id, "1")
    encrypted_passphrase = get_secret(FLAGS.project_id, FLAGS.passphrase_id, "1")

    # Decrypt encrypted passphrase via GCP Cloud KMS.
    passphrase = decrypt_passphrase(FLAGS.project_id, FLAGS.kms_keyring, FLAGS.kms_key, encrypted_passphrase)
    passphrase = passphrase.decode("UTF-8")

    # Decrypt GPG Encrypted File.
    private_key = private_key.decode("UTF-8")
    plaintext_data = decrypt_file(private_key, passphrase, FLAGS.encrypted_file_path)

    # Write output file data to disk or cloud storage if decryption is successful else log error.
    if plaintext_data.ok:
        if FLAGS.decrypt_file_path:
            write_output_file_to_disk(FLAGS.decrypt_file_path, plaintext_data.data.decode("UTF-8"))
        else:
            write_output_file_to_bucket(FLAGS.project_id, FLAGS.bucket_name, plaintext_data.data.decode("UTF-8"))
    else:
        gpg_logger.error(f"decryption failed: {plaintext_data.stderr}")

if __name__ == "__main__":
    # Mark required flags
    flags.mark_flags_as_required(["encrypted_file_path", "project_id", "kms_key", "kms_keyring", "private_key_id", "passphrase_id"])
    try:
        app.run(main)
    
    except PermissionDenied as err:
        gpg_logger.error(f"not enough permission: {err}: Exiting...")
        sys.exit(1)

    except DeadlineExceeded as err:
        gpg_logger.error(f"communication failure on server side - retry gpg_decrypt_cli: {err}: Exiting...")
        sys.exit(1)

    except FileNotFoundError as err:
        gpg_logger.error(f"encrypted file not found: {err}: Exiting...")
        sys.exit(1)
    
    except Exception as err:
        gpg_logger.error(f"An error occured: {err}: Exiting...")
        sys.exit(1)