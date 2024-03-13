"""
Logging Module 
    - logging to stdout and Google Logging API.
"""
import logging
import google.cloud.logging
from google.cloud.logging.handlers import CloudLoggingHandler, setup_logging

# Instantiates a Google Cloud Logging Client.
client = google.cloud.logging.Client()

# Setup handler to make GCP logging API calls.
cloud_handler = CloudLoggingHandler(client)

# Setup handler to stream to stdout.
handler = logging.StreamHandler()

# Create log formatter and set for the handlers.
formatter = logging.Formatter("%(asctime)s : %(name)s : %(levelname)s : %(message)s")
cloud_handler.setFormatter(formatter)
handler.setFormatter(formatter)

# Setup logger to create log Records and disable ancestor loggers.
gpg_logger = logging.getLogger('gpgdg_cli')
gpg_logger.propagate = False

# Set minimum logging level to info.
gpg_logger.setLevel(logging.INFO)

# Attach handlers to the logger.
setup_logging(cloud_handler)
gpg_logger.addHandler(handler)