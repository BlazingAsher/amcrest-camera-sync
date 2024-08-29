# Amcrest Camera Sync
Automatically sync the video files on an Amcrest camera's into local storage.

The [Python Amcrest library](https://github.com/tchellomello/python-amcrest) is used under the hood, so any cameras supported by it should work well, but it is tested on an IP4M-1026B.

## Easy Deployment
1. Set any required environment variables, as found in `app/utils/constants.py`.
2. Start the Docker container with a volume/bind mount at the data directory. By default it the subdirectory `/app/data`.

## Notes
- Make sure you set the TZ environment variable to match that of your Amcrest camera if your system timezone doesn't match. Otherwise, the time & date that will be given to your camera will be wrong, and you will get files for the wrong time (or no files at all, if the camera timezone is behind the system/default timezone).

Not affiliated or endorsed by Amcrest in any way.
