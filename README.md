# twitch-scripts
Abusing the Twitch API.

## Setup
Install Python packages.
```
pip install -r requirements.txt
```

Download [ffmpeg](https://www.ffmpeg.org/download.html) and add its location to `PATH`.

## OAuth
Twitch requires an OAuth token for Helix API access. Run `python auth.py` and follow the instructions to generate a token.

## Usage
- `python download.py -v <id>` to download videos (even sub-only ones)
- `python watch.py -u <user>` to watch users for new videos
