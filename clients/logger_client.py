"""
Logging Module 
    - logging.
"""
import logging

gpg_logger = logging.getLogger('gpgdg_cli')

handler = logging.StreamHandler()

# Create formatter and set for the handler.
formatter = logging.Formatter("%(asctime)s : %(name)s : %(levelname)s : %(message)s")

handler.setFormatter(formatter)

gpg_logger.addHandler(handler)

gpg_logger.setLevel(logging.INFO)

handler.setFormatter(formatter)