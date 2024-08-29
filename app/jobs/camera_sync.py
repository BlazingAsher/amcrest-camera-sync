import os.path
import re
import logging

from datetime import datetime, timedelta

from amcrest import AmcrestCamera
from prometheus_client import Histogram, Counter

from app.utils.constants import DATA_DIR, CAMERA_HOST, CAMERA_PORT, CAMERA_USERNAME, CAMERA_PASSWORD

FILE_INFO_REGEX = r'(\d{4}-\d{2}-\d{2})/.*?/(\d{2}\.\d{2}\.\d{2})-(\d{2}\.\d{2}\.\d{2})'

logger = logging.getLogger(__name__)
sync_duration_histogram = Histogram('sync_job_duration_seconds', 'Duration of sync jobs in seconds', buckets=[1, 5, 10, 15, 20, 25, 30, 35])
written_bytes_counter = Counter('sync_job_written_bytes', 'Total number of bytes written by the camera sync job')
sync_file_failures_counter = Counter('sync_job_file_failures', 'Total number of failed file transfers by the camera sync job')
sync_written_files_counter = Counter('sync_job_written_files', 'Total number of files written by the camera sync job')

def parse_http_response(iterator):
    result = []
    current_item = {}
    buffer = ""

    # Function to process each line and update the result
    def process_line(line):
        nonlocal result

        if line.startswith("found="):
            found_count = int(line.split('=')[1].strip())
            result = [{} for _ in range(found_count)]
            return

        # Parse each line
        key, value = line.split('=', 1)
        value = value.strip()

        # Detect the item index and nested keys
        parts = key.split('.')
        item_index = int(parts[0].split('[')[1].split(']')[0])
        nested_keys = parts[1:]

        # Initialize the current dictionary pointer to the specific item in result
        current_dict = result[item_index]

        # Create nested dictionaries dynamically
        for i, part in enumerate(nested_keys):
            if '[' in part and ']' in part:
                array_key = part.split('[')[0]
                array_index = int(part.split('[')[1].split(']')[0])

                if array_key not in current_dict:
                    current_dict[array_key] = []

                # Extend the list if the index exceeds current size
                while len(current_dict[array_key]) <= array_index:
                    current_dict[array_key].append({})

                # Move to the correct dictionary in the array
                if i == len(nested_keys) - 1:
                    current_dict[array_key][array_index] = value
                else:
                    current_dict = current_dict[array_key][array_index]
            else:
                # Regular dictionary key
                if i == len(nested_keys) - 1:
                    current_dict[part] = value
                else:
                    if part not in current_dict:
                        current_dict[part] = {}
                    current_dict = current_dict[part]

    # Iterate through each chunk in the iterator
    for chunk in iterator:
        buffer += chunk  # Append the current chunk to the buffer

        # Continue processing lines as long as we find a line terminator
        while '\r\n' in buffer:
            line, buffer = buffer.split('\r\n', 1)  # Split at the first line terminator
            process_line(line)

    # Process any remaining content in the buffer
    if buffer:
        process_line(buffer)

    return result

def sync_files():
    start = datetime.now()

    camera = AmcrestCamera(CAMERA_HOST, CAMERA_PORT, CAMERA_USERNAME, CAMERA_PASSWORD).camera

    now = datetime.now()
    five_mins_ago = now - timedelta(minutes=5)

    logger.info("Getting file list.")

    files_response = camera.find_files(five_mins_ago, now, types=["mp4"])

    files = parse_http_response(files_response)

    logger.info(f"Found {len(files)} files.")

    for file in files:
        file_path = file["FilePath"]

        try:
            # Using regex to find the matches
            matches = re.search(FILE_INFO_REGEX, file_path)

            # Extracting the date, start time, and end time
            date = matches.group(1) if matches else None
            start_time = matches.group(2) if matches else None
            end_time = matches.group(3) if matches else None

            if date is None or start_time is None or end_time is None:
                logger.warning(f"Unable to parse the file {file_path}!")
                continue

            year, month, day = date.split('-')
            hour = start_time.split('.')[0]

            directory_path_split = os.path.join(DATA_DIR, year, month, day, hour)

            destination_file = os.path.join(directory_path_split, os.path.basename(file_path))

            if os.path.exists(destination_file):
                continue
            else:
                logger.info(f"Retrieving {file_path}")
                os.makedirs(directory_path_split, exist_ok=True)

                with open(destination_file, 'wb') as f:
                    output_bytes = camera.download_file(file_path)
                    f.write(output_bytes)
                    written_bytes_counter.inc(len(output_bytes))
                    sync_written_files_counter.inc(1)
        except Exception:
            logger.error(f"Encountered an issue retrieving {file_path}", exc_info=True)
            sync_file_failures_counter.inc(1)

    duration = datetime.now() - start
    logger.info(f"Sync finished in {duration}.")

    sync_duration_histogram.observe(duration.total_seconds())

def run():
    sync_files()