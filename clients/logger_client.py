"""
Logging Module 
    - logging.
"""
import logging
import google.cloud.logging
from google.cloud.logging.handlers import CloudLoggingHandler


# Instantiates a Google Cloud Logging Client
client = google.cloud.logging.Client()

# Retrieves a Cloud Logging handler
cloud_handler = CloudLoggingHandler(client)

# Create formatter and set for the handler.
formatter = logging.Formatter("%(asctime)s : %(name)s : %(levelname)s : %(message)s")

cloud_handler.setFormatter(formatter)

# Use Python’s standard logging library to send logs to GCP
gpg_logger = logging.getLogger('gpgdg_cli')

# Set minimum level of logger to info
gpg_logger.setLevel(logging.INFO)

gpg_logger.addHandler(cloud_handler)

