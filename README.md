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
- Utilizes elliptic curves Algos - key-curve ed25519 and cv25519.
- 32 character passphrase made up of letters, numbers and special characters is generated to password-protect the private key.
- This passphrase will remain unknown to anybody. 
- A Key Encryption Key (KEK) that never leaves Cloud KMS will be used to encrypt the passphrase.
- The encrypted passphrase and passphrase-protected private key are stored in GCP secrets manager.
- The public key is written to "public-key.asc" on the folder the tool is run from.
- For decryption, the passphrase & private key are retrieved from secrets manager, the encrypted passphrase is decrypted by the KEK and used alongside the private-key.
- Utilizes service account impersonation for all calls to GCP APIs.

## Installation

### Dependencies
 - A service account with the following roles:
    - Cloud KMS: Cloud KMS CryptoKey Encrypter/Decrypter role.
    - Secret Manager: Secret Manager Admin role.
    - Cloud Storage: Storage Object User role + storage.buckets.get permission (replace permission with with Storage Insights collectore service role).
    - Cloud Logging: Logs Writer role.

- The user running the tool will require the following role:
     - Service Account Token Creator role on the service account with the assigned roles above.

- Install gcloud - Google Cloud CLI.
    - Steps to install can be found here - https://cloud.google.com/sdk/docs/install#deb

- Clone this github repo.

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

- Setup Application Default Credentials (ADC) and impersonate service account using gcloud - https://cloud.google.com/docs/authentication/provide-credentials-adc.

```
$ gcloud auth application-default login --impersonate-service-account <service_account_name>@<project_id>.iam.gserviceaccount.com
```
> **Note:** 
>
> Revoke ADC access & refresh tokens generated after using this tool - https://cloud.google.com/sdk/gcloud/reference/auth/application-default/revoke 

### Usage
 - To generate a keypair and store the encrypted passphrase and passphrase protected private key in Secrets manager.

```
python gpg_generate_cli.py --email_id <email> \
--project_id <gcp project id> \
--kms_keyring <cloud kms key ring name> \
--kms_key <cloud kms key name> \
--private_key_id <private key id in GCP secrets manager> \
--passphrase_id <passphrase id in secrets manager>
```

 - To decrypt the encrypted file and store the plaintext file in a GCP Storage Bucket.

 ```
 python gpg_decrypt_cli.py --project_id <gcp project id> \
 --kms_keyring <cloud kms key ring name>g \
 --kms_key <cloud kms key name> \
 --private_key_id <private key id in GCP secrets manager> \
 --passphrase_id <passphrase id in secrets manager> \
 --encrypted_file_path <path to encrypted file on disk> \
 --bucket_name <gcp cloud storage bucket name>
 ```

- To decrypt the encrypted file and store the plaintext file on disk.

 ```
 python gpg_decrypt_cli.py --project_id <gcp project id> \
 --kms_keyring <cloud kms key ring name>g \
 --kms_key <cloud kms key name> \
 --private_key_id <private key id in GCP secrets manager> \
 --passphrase_id <passphrase id in secrets manager> \
 --encrypted_file_path <path to encrypted file on disk> \
 --decrypted_file_path <path to store decrypted file on disk>
 ```

> **Note:** 
>
> All flags are mandatory. For the decrypt operation, you must either specify a cloud storage bucket or location on disk to store the decrypted file.