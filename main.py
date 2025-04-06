import os
import json
import datetime
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from os import path
from dotenv import load_dotenv
from utils import send_discord_alert  # ✅ Make sure this is added

load_dotenv()

# Initialize Spotify API using environment variables
CACHE = path.join(path.dirname(__file__), ".spotify_cache")

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope='user-library-read playlist-modify-private playlist-modify-public',
    cache_path=CACHE
))

ADDED_TRACKS_FILE = "added_tracks.json"
LOG_FILE = "log.txt"
PLAYLIST_ID = "3pLcslz4KhEN8QEmFCkUq6"


def get_liked_tracks():
    tracks = []
    results = sp.current_user_saved_tracks(limit=50)
    tracks.extend(results['items'])
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks


def add_tracks_to_playlist(playlist_id, track_ids):
    for i in range(0, len(track_ids), 100):
        sp.playlist_add_items(playlist_id, track_ids[i:i + 100])


def load_added_tracks():
    if os.path.exists(ADDED_TRACKS_FILE):
        with open(ADDED_TRACKS_FILE, "r") as f:
            return set(json.load(f))

    log_message("📥 No saved track list found. Fetching existing tracks from playlist to avoid duplicates.")
    existing_track_ids = set()
    results = sp.playlist_items(PLAYLIST_ID, limit=100)
    while results:
        for item in results['items']:
            if item and item['track']:
                existing_track_ids.add(item['track']['id'])
        if results['next']:
            results = sp.next(results)
        else:
            break
    save_added_tracks(existing_track_ids)
    return existing_track_ids


def save_added_tracks(track_ids):
    with open(ADDED_TRACKS_FILE, "w") as f:
        json.dump(list(track_ids), f)


def log_message(message):
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"{timestamp} {message}\n")
    print(message)


def main():
    log_message("🔐 Auth complete. Checking liked songs...")

    liked_tracks = get_liked_tracks()
    liked_tracks.sort(key=lambda x: x['added_at'])  # sort by date liked

    all_track_ids = [
        track['track']['id'] for track in liked_tracks if track['track']
    ]
    already_added = load_added_tracks()
    new_tracks = [track for track in liked_tracks if track['track']['id'] not in already_added]

    if not new_tracks:
        log_message("✅ No new liked songs found.")
        send_discord_alert("✅ No new liked songs found.")
        return "✅ No new liked songs found.", []

    new_track_ids = [track['track']['id'] for track in new_tracks]
    add_tracks_to_playlist(PLAYLIST_ID, new_track_ids)
    save_added_tracks(already_added.union(new_track_ids))

    track_summaries = [f"{track['track']['name']} by {track['track']['artists'][0]['name']}" for track in new_tracks]
    track_summary_text = "\n".join(track_summaries)

    log_message(f"➕ Added {len(new_tracks)} new songs to playlist:\n{track_summary_text}")
    send_discord_alert(f"✅ Added {len(new_tracks)} new songs to playlist:\n" + track_summary_text)

    return f"✅ Added {len(new_tracks)} new songs to playlist!", track_summaries


if __name__ == "__main__":
    main()
