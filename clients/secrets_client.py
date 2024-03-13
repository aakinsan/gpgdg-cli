"""
Secrets Manager Module 
    - creates and gets secrets (encrypted passphrase & passphrase protected private key)
"""

from google.cloud import secretmanager
from clients.logger_client import gpg_logger

def create_secret(project_id: str, secret_id: str) -> None:
    # Create secret

    # Initialize Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build parent resource name.
    parent = f"projects/{project_id}"

    # Build parent request, initialize arguments and create secret.
    parent_request = {"parent": parent, "secret_id": secret_id, "secret": {"replication": {"automatic": {}}}}
    client.create_secret(request=parent_request)

def add_secret_version(project_id: str, secret_id: str, payload: bytes) -> None:
    # Add secret version to secrets manager.

    # Initialize Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()
    
    # Build path to parent.
    parent = client.secret_path(project_id, secret_id)

    # Add secret version.
    request = {"parent": parent, "payload": {"data": payload}}
    response = client.add_secret_version(request=request)

    # Log Message that secret version has been added.
    # gpg_logger.info(f"{response.name} added")
    gpg_logger.log(f"{response.name} added")


def get_secret(project_id: str, secret_id: str, version_id: str) -> bytes:
    # Get secret (private key or passphrase) from secrets manager.

    # Initialize Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version.
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    # Build Request.
    request = {"name": name}

    # Access the secret version.
    response = client.access_secret_version(request)

    # Get payload.
    payload = response.payload.data

    # Log Message.
    # gpg_logger.info(f"{secret_id} retrieved from GCP Secret Manager")
    gpg_logger.log(f"{secret_id} retrieved from GCP Secret Manager")
    
    # return payload.
    return payload
