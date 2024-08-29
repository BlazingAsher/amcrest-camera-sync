import os
import logging

from datetime import datetime, timedelta

from prometheus_client import Histogram

from app.utils.constants import DATA_DIR, FILES_KEEP_DAYS

cleanup_duration_histogram = Histogram('cleanup_job_duration_seconds', 'Duration of cleanup jobs in seconds', buckets=[1, 2, 4, 8, 16, 32, 64, 128])
logger = logging.getLogger(__name__)

def is_older_than_date(dir_path, cutoff_date):
    try:
        # Extract the YYYY/MM/DD/HH from the directory path
        year, month, day, hour = map(int, dir_path.split(os.sep)[-4:])
        dir_date = datetime(year, month, day, hour)

        # Compare the directory date with the cutoff date
        return dir_date < cutoff_date
    except ValueError:
        # If the directory name format is incorrect, skip it
        return False

def delete_empty_directories(base_directory):
    # Traverse the directory tree from the bottom up
    for root, dirs, files in os.walk(base_directory, topdown=False):
        if root == base_directory:
            continue

        # If a directory has no files or directories, remove it
        if not dirs and not files:
            try:
                os.rmdir(root)
                logger.debug(f"Deleted empty directory: {root}")
            except OSError as e:
                logger.warning(f"Error deleting directory {root}", exc_info=True)


def cleanup_old_files():
    logger.info("Starting data directory cleanup.")
    start_time = datetime.now()
    # Calculate the cutoff date for 14 days ago
    cutoff_date = datetime.now() - timedelta(days=FILES_KEEP_DAYS)

    # Walk through the directory structure
    for root, dirs, files in os.walk(DATA_DIR, topdown=False):
        # Check if the current directory is older than 14 days
        if len(root.split(os.sep)) >= 4 and is_older_than_date(root, cutoff_date):
            # Delete all files inside this directory
            for file in files:
                file_path = os.path.join(root, file)
                os.remove(file_path)
                logger.debug(f"Deleted file: {file_path}")


    delete_empty_directories(DATA_DIR)

    duration = datetime.now() - start_time
    logger.info(f"Finished cleanup in {duration}.")
    cleanup_duration_histogram.observe(duration.total_seconds())  # Record duration

def run():
    cleanup_old_files()

# cleanup_old_files()