__version__ = "1.0.0"

import math
import os.path
import re
import sys
import time

import spotipy
from openpyxl import Workbook
from spotipy.oauth2 import SpotifyOAuth

# Must be filled-in by user
SPOTIPY_CLIENT_ID = "Client-ID"
# Must be filled-in by user
SPOTIPY_CLIENT_SECRET = "Client-Secret"
# Can be changed by user but *must match* the URI in the developer portal
SPOTIPY_REDIRECT_URI = "https://localhost:8888/callback"

scope = ["user-library-read", "user-read-email", "playlist-read-private"]
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope=scope,
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
    )
)

try:
    user = sp.current_user()["id"]
except spotipy.oauth2.SpotifyOauthError:
    print(
        "ERROR: Invalid Client.\nMake sure you filled in the correct Client ID and Client Secret in the script."
    )
    sys.exit(1)


def print_err(response):
    print(
        "Unknown error ({}): {}".format(
            response["error"]["status"], response["error"]["message"]
        )
    )


def is_rate_exceeded(response):
    timeout = 30
    if response["error"]["status"] == 429:
        print("Exceeded rate limit, retrying in {} seconds.".format(timeout))
        time.sleep(timeout)
        return True
    return False


artist_data = {}
track_data = []

# Get tracks within _Liked Songs_

offset = 0
limit = 50
while True:
    time.sleep(0.1)
    results = sp.current_user_saved_tracks(limit=limit, offset=offset)
    if "error" in results:
        if is_rate_exceeded(results):
            continue
        print_err(results)
        break
    print(
        "Reading user tracks (part {} of {})".format(
            math.ceil(offset / limit + 1), math.ceil(results["total"] / limit)
        )
    )
    offset += limit
    track_data += results["items"]
    if offset >= results["total"]:
        break

# Get all user-created playlists

playlist_ids = []
offset = 0
limit = 50
while True:
    time.sleep(0.1)
    results = sp.user_playlists(user, limit, offset)
    if "error" in results:
        if is_rate_exceeded(results):
            continue
        print_err(results)
        break
    print(
        "Reading user playlists (part {} of {})".format(
            math.ceil(offset / limit + 1), math.ceil(results["total"] / limit)
        )
    )
    offset += limit
    for item in results["items"]:
        owner = item["owner"]["id"]
        if owner == user:
            try:
                playlist_ids += [re.findall(r"(\w+$)", item["uri"])[0]]
            except IndexError:
                print("Cannot parse playlist id {}".format(item["uri"]))
    if offset >= results["total"]:
        break

# Get tracks from all user-created playlists

for playlist in playlist_ids:
    offset = 0
    limit = 100
    while True:
        time.sleep(0.1)
        results = sp.playlist_items(
            playlist,
            fields="total,items(track(name,artists(name)))",
            limit=limit,
            offset=offset,
        )
        if "error" in results:
            if is_rate_exceeded(results):
                continue
            print_err(results)
            break
        print(
            "Reading playlist {} tracks (part {} of {})".format(
                playlist,
                math.ceil(offset / limit + 1),
                math.ceil(results["total"] / limit),
            )
        )
        offset += limit
        track_data += results["items"]
        if offset >= results["total"]:
            break

# Parse track data for each artist

artist_ = "null"
song_name_ = "null"
for i, track in enumerate(track_data):
    for _artist_data in track["track"]["artists"]:
        try:
            artist_ = _artist_data["name"]
            # If artist is not available (e.g. from a local track) attempt to extract artist from track name
            if artist_ == "":
                artist_ = str(track["track"]["name"]).split("-")[0].strip(" ")
            if artist_ == "":
                print(
                    "Artist for track {} not found. Skipping.".format(
                        track["track"]["name"]
                    )
                )
                continue
            if artist_ not in artist_data:
                artist_data[artist_] = {
                    "song_names": [],
                    "unique_count": 0,
                    "total_count": 0,
                }
            song_name_ = track["track"]["name"]
            if song_name_ == "":
                song_name_ = str(track["track"]["name"]).split("-")[-1].strip(" ")
            # print(
            #     "Processing stage {} of {}: {} - {}.".format(
            #         i + 1, len(track_data), artist_, song_name_
            #     )
            # )
            artist_data[artist_]["total_count"] += 1
            if song_name_ not in artist_data[artist_]["song_names"]:
                artist_data[artist_]["song_names"] += [song_name_]
                artist_data[artist_]["unique_count"] += 1
        except Exception as e:
            print(
                "Exception occured: {}.\n Track '{} - {}'".format(
                    e, artist_, song_name_
                )
            )

# Write artist data into XLSX format

wb = Workbook()
ws = wb.active

# Table header
ws.append(["Artists", "Tracks", "Unique Track Count", "Total Track Count"])

# Table data
for artist in artist_data:
    ws.append(
        [
            artist,
            '"' + '", "'.join(artist_data[artist]["song_names"]) + '"',
            artist_data[artist]["unique_count"],
            artist_data[artist]["total_count"],
        ]
    )

basename = "artists.xlsx"

count = 0
while True:
    filename = (
        "{0} ({2}){1}".format(*os.path.splitext(basename), count)
        if count > 0
        else basename
    )
    if os.path.isfile(filename):
        count += 1
        continue
    try:
        wb.save(filename)
        break
    except PermissionError:
        count += 1

print("File saved to: {}".format(os.path.abspath(filename)))
