"""
gpg_decrypt_cli - entry program for file decryption
    - Gets the encrypted passphrase and private key (protected by the passphrase).
    - calls Cloud KMS to decrypt the passphrase.
    - decrypts output file using private key.
    - output file is either written to disk or a cloud storage bucket. 
"""

from absl import app
from absl import flags
import sys
from clients.logger_client import gpg_logger
from clients.gpg_client import decrypt_gpg_file
from clients.kms_client import decrypt_passphrase
from clients.secrets_client import get_secret
from clients.storage_client import write_output_file_to_disk, write_output_file_to_bucket
from google.api_core.exceptions import PermissionDenied, DeadlineExceeded

# Assigning FlagValues Object to FLAGS.
FLAGS = flags.FLAGS

# Validation Function to ensure either a storage bucket or disk location is chosen to store output files.
def validate_storage_location(flags_dict: dict) -> any:
    if flags_dict["bucket"] and flags_dict["output_path"]:
        raise ValueError("Specify either a bucket name or path on disk to store output file")
    elif flags_dict["bucket"] is None and flags_dict["output_path"] is None:
        raise ValueError("Specify either a bucket name or path on disk to store output file")
    else:
        return True

# Define cli flags.
flags.DEFINE_string("kms_key", None, "The cloud KMS key name of the KEK.")
flags.DEFINE_string("kms_kring", None, "The cloud KMS keyring name of the KEK.")
flags.DEFINE_string("privkey_sid", None, "Secret ID of the GPG Private Key in secrets manager.")
flags.DEFINE_string("version", "1", "version number of Secret ID.")
flags.DEFINE_string("pass_sid", None, "Secret ID of the encrypted passphrase in secrets manager.")
flags.DEFINE_string("project_id", None, "The GCP project ID.")
flags.DEFINE_string("input_path", None, "location of encrypted file on disk.")
flags.DEFINE_string("output_path", None, "Location to write decrypted file to on disk.")
flags.DEFINE_string("bucket", None, "Cloud Storage bucket name to upload decrypted blob; files are stored at the path <bucket_name>/output-files")

# Validate Storage Location Flag.
flags.register_multi_flags_validator(['bucket', "output_path"], validate_storage_location)

def main(argv):

    # Delete unused argument.
    del argv

    # Get private key and encrypted passphrase from GCP secret manager.
    private_key = get_secret(FLAGS.project_id, FLAGS.privkey_sid, FLAGS.version)
    encrypted_passphrase = get_secret(FLAGS.project_id, FLAGS.pass_sid, FLAGS.version)

    # Decrypt encrypted passphrase via GCP Cloud KMS.
    passphrase = decrypt_passphrase(FLAGS.project_id, FLAGS.kms_kring, FLAGS.kms_key, encrypted_passphrase)
    passphrase = passphrase.decode("UTF-8")

    # Decrypt gpg encrypted file.
    private_key = private_key.decode("UTF-8")
    plaintext_data = decrypt_gpg_file(private_key, passphrase, FLAGS.input_path)

    # if decryption is successful, write output file data to disk or cloud storage else log a decryption error.
    if plaintext_data.ok:
        if FLAGS.output_path:
            write_output_file_to_disk(FLAGS.output_path, plaintext_data)
        else:
            write_output_file_to_bucket(FLAGS.project_id, FLAGS.bucket, plaintext_data.data.decode("UTF-8"))
    else:
        gpg_logger.error(f"decryption failed: {plaintext_data.stderr}")

# Check if script is run directly.
if __name__ == "__main__":

    # Specify mandatory cli flags.
    flags.mark_flags_as_required(["input_path", "project_id", "kms_key", "kms_kring", "privkey_sid", "pass_sid"])
    
    try:
        # Run script.
        app.run(main)
    
    # Catch exceptions.
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