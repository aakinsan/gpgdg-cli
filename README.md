![image](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)
![image](https://img.shields.io/badge/Google_Cloud-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)

# GPG Key Generator and Decryptor

## Introduction
The project aims to address the following security concerns:
- Storage of private key used for decryption of sensitive data on employee corporate laptops.
- Prevents unauthorized individuals from potentially gaining access to the keys when the laptop is stolen or compromised (e.g. malware, social engineeering etc.).
- Prevents a situation where an organization suffers because the few employees with access to the keys are away due to illness, are terminated etc.
- Storing sensitive cryptograhic material may violate compliance and regulatory requirements.
- Limited control and visibility over the security state/profile of the employee's laptop.

## Features
- Utilizes elliptic curves Algorithms: key-curve ed25519 and cv25519.
- 32 character passphrase made up of letters, numbers and special characters is generated to password-protect the private key.
- This passphrase will remain unknown to anybody. 
- A Key Encryption Key (KEK) that never leaves Cloud KMS will be used to encrypt the passphrase.
- The encrypted passphrase and passphrase-protected private key are stored in GCP secrets manager.
- The public key required for encryption is written to disk.
- For decryption operation, the passphrase & private key are retrieved from secrets manager, the encrypted passphrase is decrypted by the KMS KEK and used alongside the private-key.
- Utilizes service account impersonation for all calls to GCP APIs so there is no requirement to download Service Account Private Keys.

## Installation
> [!NOTE]  
>
> This tool has only been deployed and tested on Linux Ubuntu/Debian OS.

### Dependencies
 - A service account with the following roles:
    - Cloud KMS: Cloud KMS CryptoKey Encrypter/Decrypter role.
    - Secret Manager: Secret Manager Admin role.
    - Cloud Storage: Storage Object User role + Storage Insights collector service role.
    - Cloud Logging: Logs Writer role.

- The user running the tool will require the following role:
    - Service Account Token Creator role on the service account with the assigned roles above.

- GCP Resources:
    Ensure the APIs are enabled.
    - Cloud KMS Symmetric encrypt/decrypt key.
    - Cloud Storage bucket. 
    - Cloud Logging.
    - Secrets Manager.

- Install gcloud - Google Cloud CLI.
    - Steps to install can be found here - https://cloud.google.com/sdk/docs/install#deb

- Clone this github repo.
```
$ git clone https://github.com/aakinsan/gpgdg-cli.git
$ cd gpgdg-cli/
```

- Setup python virtual environment. 
```
$ sudo apt install python3.10-venv
$ python3 -m venv venv
$ source venv/bin/activate
```

- Install required packages.

```
pip install -r requirements.txt
```

- Set project, enable Application Default Credentials (ADC) and impersonate service account using gcloud (https://cloud.google.com/docs/authentication/provide-credentials-adc) and login using the user account that has been assigned the service account token creator role. 

```
$ gcloud auth application-default login --impersonate-service-account <service_account_name>@<project_id>.iam.gserviceaccount.com
$ gcloud config set project <gcp_project_id>
```
> [!NOTE]  
>
> Revoke ADC access & refresh tokens generated after using this tool - https://cloud.google.com/sdk/gcloud/reference/auth/application-default/revoke 

### Usage
 - To generate a keypair and store the encrypted passphrase and passphrase protected private key in Secrets manager.

```Ruby
python gpg_generate_cli.py --email_id "email" \
    --project_id "gcp_project_id" \
    --kms_key "cloud_kms_key_name" \
    --privkey_sid "private-key_secret-id_in_GCP_secrets_manager" \
    --pass_sid "passphrase_secret-id_in_secrets_manager" \
    --output_path "path_to_write_public-key_to_on_disk"
```

 - To decrypt the encrypted file and store the plaintext blob in a GCP Storage Bucket.

 ```Ruby
 python gpg_decrypt_cli.py --project_id "gcp_project_id" \
    --kms_keyring "cloud_kms_keyring_name"\
    --kms_key "cloud_kms_key_name" \
    --privkey_sid "private-key_secret-id_in_GCP_secrets_manager" \
    --pass_sid "passphrase_secret-id_in_secrets_manager" \
    --input_path "path_to_encrypted_file_on_disk" \
    --version "secret_version_number" \
    --bucket "gcp_cloud_storage_bucket_name"
 ```

- To decrypt the encrypted file and store the plaintext file on disk.

 ```Ruby
 python gpg_decrypt_cli.py --project_id "gcp_project_id" \
    --kms_keyring "cloud_kms_keyring_name"\
    --kms_key "cloud_kms_key_name" \
    --privkey_sid "private-key_secret-id_in_GCP_secrets_manager" \
    --pass_sid "passphrase_secret-id_in_secrets_manager" \
    --input_path "path_to_encrypted_file_on_disk" \
    --version "secret_version_number" \
    --output_path "path_to_write_decrypted_file_to_on_disk"
```

> [!NOTE]  
>
> All flags are mandatory with the exception of `--output_path`, `--bucket` and `--version` for decrypt operations. 
> You must specify either a bucket name or output path to store the decrypted file.
> `--version` number is optional and defaults to the version 1 secret if not specified.