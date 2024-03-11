from google.cloud import secretmanager
from clients.logger_client import gpg_logger

def create_secret(project_id, secret_id):
    # Initialize Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build parent resource name.
    parent = f"projects/{project_id}"

    # Build parent request and initialize arguments.
    parent_request = {"parent": parent, "secret_id": secret_id, "secret": {"replication": {"automatic": {}}}}
    secret = client.create_secret(request=parent_request)

    return secret

def add_secret(project_id, secret_id, payload):
    # Initialize Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()
    
    # Build parent
    parent = client.secret_path(project_id, secret_id)

    # Add secret version
    request = {"parent": parent, "payload": {"data": payload}}
    response = client.add_secret_version(request=request)

    # Print the new secret version name.
    print(f"Secret version {response.name} added")


def get_secret(project_id, secret_id, version_id):
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

    # Log Message
    gpg_logger.info(f"{secret_id} retrieved from GCP Secret Manager")

    return payload
