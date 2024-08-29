# Amcrest Camera Sync
Automatically sync the video files on an Amcrest camera's into local storage.

The [Python Amcrest library](https://github.com/tchellomello/python-amcrest) is used under the hood, so any cameras supported by it should work well, but it is tested on an IP4M-1026B.

## Easy Deployment
1. Set any required environment variables, as found in `app/utils/constants.py`.
2. Start the Docker container with a volume/bind mount at the data directory. By default it the subdirectory `/app/data`.

Not affiliated or endorsed by Amcrest in any way.