# Spotify Artist Counter

This script is designed to list all artists and their respective song count across all user-created playlists.

## Requirements

This script requires the following packages to be installed on the system:
```text
openpyxl -> For writing *.xslx files
spotipy -> For access to the Spotify API
```
These packages can be installed using `pip install -r requirements.txt`.

## Spotify Setup

To use this app, credentials to the Spotify API are required. To get access to the Spotify API credentials follow these steps:

1. Go to the [Spotify for Developers dashboard](https://developer.spotify.com/dashboard).
2. Create a new application under any name.
3. Enter the **Redirect URI** as `https://localhost:8888/callback` or choose your own
(**Warning: The Redirect URI provided in the developer portal must match with the one written in the script!**).
4. Tick the Web API checkbox.
5. Read and tick the Spotify ToS agreement and save the app.
6. Open the created application and go to settings.
7. Click _View client secret_.
8. Copy the provided _Client ID_ and _Client Secret_ to the respective entries in the script file.

## Usage

### First Run

Upon running the script for the first time, the user will be redirected to the Spotify authorization website.
If upon authorization the user is not redirected as intended and/or the script does not run, copy the URL of the redirect page into the terminal.

### File Generation

The generated file will be placed in the script's working directory under the name `artists.xlsx`.

The contents of the file are as follows:

| Artist                          | Tracks                                                           | Unique Track Count       | Total Track Count                                       |
|---------------------------------|------------------------------------------------------------------|--------------------------|---------------------------------------------------------|
| Each artist's <br/>name per row | Track titles separated<br/>in double quotes separated by a comma | Unique track title count | Total track count across<br/>all user-created playlists |

Note: _Liked Songs_ are included among playlist results.