# YouTube Music browser

YouTube Music's inability to sort your library is incredibly annoying. This script allows you to browse and sort your library by song, artist, and album, and links everything back to YouTube Music.

## Setup
```bash
conda create -n ytmusic python=3.10
conda activate ytmusic
pip install -r requirements.txt
ytmusicapi oauth
```

This will open a browser window for [YTMusicAPI authentication](https://ytmusicapi.readthedocs.io/en/stable/setup/index.html).

## Run
```bash
python ytmusic.py
```

Then navigate to http://localhost:5000 in your browser. You can use a different port, say 5678, with `python ytmusic.py --port 5678`.
