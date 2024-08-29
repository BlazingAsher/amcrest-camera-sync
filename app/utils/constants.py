import logging
import os
import sys

logger = logging.getLogger(__name__)

def raise_required_argument(name):
    logger.error(f"The environment variable {name} is required!")
    sys.exit(1)

LISTEN_ADDRESS = os.getenv("LISTEN_ADDRESS", "127.0.0.1")
LISTEN_PORT = int(os.getenv("LISTEN_PORT", "8000"))

DATA_DIR = os.getenv("DATA_DIR") or "data"

CAMERA_HOST = os.getenv("CAMERA_HOST") or raise_required_argument("CAMERA_HOST")
CAMERA_PORT = int(os.getenv("CAMERA_PORT", "80"))
CAMERA_USERNAME = os.getenv("CAMERA_USERNAME") or raise_required_argument("CAMERA_USERNAME")
CAMERA_PASSWORD = os.getenv("CAMERA_PASSWORD") or raise_required_argument("CAMERA_PASSWORD")

# How long to keep files
FILES_KEEP_DAYS = int(os.getenv("FILES_KEEP_DAYS", "14"))

# The hour at which the data cleanup job should run (24-hour time)
DATA_CLEANUP_HOUR = int(os.getenv("DATA_CLEANUP_HOUR", "10"))

# How often we should sync files with the camera
SYNC_INTERVAL_SECONDS = int(os.getenv("SYNC_INTERVAL_SECONDS", "30"))