"""
Logging Module 
    - Streams logs.
"""

import google.cloud.logging
import logging

# Instantiates a Google Cloud Logging Client
client = google.cloud.logging.Client()

# Retrieves a Cloud Logging handler
client.setup_logging()

# Use Python’s standard logging library to send logs to GCP
gpg_logger = logging.getLogger("gpg_logger")

# Set minimum level of logger to info.
gpg_logger.setLevel(logging.INFO)

# Create Log handler.
gpg_handler = logging.StreamHandler()

# Create formatter.
gpg_format = logging.Formatter("%(asctime)s : %(name)s : %(levelname)s : %(message)s")

# Add formatter to handler.
gpg_handler.setFormatter(gpg_format)

# Add handler to logger.
gpg_logger.addHandler(gpg_handler)