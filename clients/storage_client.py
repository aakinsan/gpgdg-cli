"""
Storage Module 
    - writes output file to cloud storage bucket after decryption.
    - writes output file to disk after decryption.
    - writes public key to disk after keypair generation.
"""

import sys
import gnupg
from google.cloud.storage import Blob
from google.cloud import storage
from datetime import datetime
from clients.logger_client import gpg_logger
from google.cloud.exceptions import NotFound

def write_output_file_to_bucket(google_project_id: str, storage_bucket: str, data:str) -> None:
        # Uploads output files to the cloud storage bucket
        # File name format in Cloud Storage will be 'YY-mm-ddTHH:MM:SSZ-outputfile.txt'      
        storage_client = storage.Client(project=google_project_id)

        try:
            output_file_storage_bucket = storage_client.get_bucket(storage_bucket)

        except NotFound as err:
              gpg_logger.error(f"That bucket does not exist: {err}: Exiting...")
              sys.exit(1)

        date_time_format = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        blob_path = f"output_files/{date_time_format}-outputfile.txt"
        blob = Blob(blob_path, output_file_storage_bucket)
        blob.upload_from_string(data)
        gpg_logger.info(f"output file uploaded to {storage_bucket} bucket.")

def write_public_key_to_disk(file_path: str, public_key: str) -> None:
    # Writes public key to disk
    with open(file_path, "w") as f:
        f.write(public_key)
        gpg_logger.info(f"Public Key written to public_key.asc.")

def write_output_file_to_disk(file_path: str, plaintext_data: gnupg.Crypt) -> None:
     # Writes output file to disk
     with open(file_path, "w") as f:
            f.write(plaintext_data.data.decode("UTF-8"))
            gpg_logger.info(f"output file written to {file_path}")