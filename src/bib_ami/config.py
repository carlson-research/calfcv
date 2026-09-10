import os

# Base configurations with environment variable overrides
DEFAULT_API_URL = "http://" + "127.0.0.1:8000/v1"
DEFAULT_WEB_URL = "https://" + "bib-ami.com"

API_URL = os.getenv("BIB_AMI_API_URL", DEFAULT_API_URL).rstrip("/")
WEB_URL = os.getenv("BIB_AMI_WEB_URL", DEFAULT_WEB_URL)
API_KEY = os.getenv("BIB_AMI_API_KEY")
