"""
Logging Module 
    - logging.
"""

import logging
import google.cloud.logging


# Instantiates a Google Cloud Logging Client
client = google.cloud.logging.Client()

# Create Log handler.
cloud_handler = client.get_default_handler()

# Create formatter and set for the handler.
formatter = logging.Formatter("%(asctime)s : %(name)s : %(levelname)s : %(message)s")
cloud_handler.setFormatter(formatter)

# Use Python’s standard logging library to send logs to GCP
gpg_logger = logging.getLogger("gpg_logger")

# Set minimum level of logger to info.
gpg_logger.setLevel(logging.INFO)

# Add handler to logger.
gpg_logger.addHandler(cloud_handler)

