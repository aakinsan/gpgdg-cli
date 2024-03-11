import google.cloud.logging

import logging

# Instantiates a Google Cloud Logging Client
client = google.cloud.logging.Client()

# Retrieves a Cloud Logging handler
client.setup_logging()

# Use Python’s standard logging library to send logs to GCP
gpg_logger = logging.getLogger('gpg')

# Set minimum level of logger to info
gpg_logger.setLevel(logging.INFO)