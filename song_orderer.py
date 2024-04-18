import pandas as pd
import re
import spotipy
from spotipy.oauth2 import SpotifyOAuth

import cred

# Instantiate the Spotipy object
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=cred.client_ID,
                                               client_secret=cred.client_SECRET,
                                               redirect_uri=cred.redirect_url,
                                               scope='playlist-modify-public'))

class Playlist:
    """Retrieves and stores metadata of a Spotify playlist.
    """
    def __init__(
            self, 
            playlist_url
        ):
        self.playlist_id = self.get_playlist_id(playlist_url)
        self.playlist = sp.playlist_tracks(self.playlist_id)
        self.playlist_metadata_df = self.get_playlist_data()


    def get_playlist_id(
            self,
            playlist_url
        ):
        pattern = r'playlist/([a-zA-Z0-9]+)'
        match = re.search(pattern, playlist_url)
        if match:
            playlist_id = match.group(1)
            return playlist_id
        else:
            raise ValueError("Playlist ID not found in the URL.")


    def get_audio_features_batch(
            self, 
            track_ids
        ):
        audio_features_batch = []

        # Split track IDs into batches of 100 (maximum limit per request)
        for i in range(0, len(track_ids), 100):
            track_ids_batch = track_ids[i:i+100]
            audio_features_batch += sp.audio_features(track_ids_batch)

        return audio_features_batch

    
    def get_playlist_data(self):
        track_data = []

        # API will only return 100 songs at a time, need to paginate
        offset = 0
        limit = 100

        while True:
            results = sp.playlist_tracks(self.playlist_id, offset=offset, limit=limit)
            tracks = results['items']

            track_ids = [item['track']['id'] for item in tracks]
            audio_features_batch = self.get_audio_features_batch(track_ids)

            for i, item in enumerate(tracks):
                track = item['track']
                track_id = track['id']
                audio_features = audio_features_batch[i]

                track_info = {
                    'Track ID': track_id,
                    'Track Name': track['name'],
                    'Artist Name': track['artists'][0]['name'],  # Assuming only one artist per track
                    'Album Name': track['album']['name'],
                    'Release Date': track['album']['release_date'],
                    'Duration (ms)': track['duration_ms'],
                    'Popularity': track['popularity'],
                    'Acousticness': audio_features.get('acousticness', None),
                    'Danceability': audio_features.get('danceability', None),
                    'Energy': audio_features.get('energy', None),
                    'Instrumentalness': audio_features.get('instrumentalness', None),
                    'Liveness': audio_features.get('liveness', None),
                    'Loudness': audio_features.get('loudness', None),
                    'Speechiness': audio_features.get('speechiness', None),
                    'Valence': audio_features.get('valence', None),
                    'Tempo': audio_features.get('tempo', None),
                    'Key': audio_features.get('key', None),
                    'Mode': audio_features.get('mode', None),
                    'Time Signature': audio_features.get('time_signature', None)
                }

                track_data.append(track_info)

            if len(tracks) < limit:
                break

            offset += limit

        playlist_df = pd.DataFrame(track_data)

        return playlist_df
        
        
    def update_playlist(self, track_ids):
        sp.playlist_replace_items(self.playlist_id, items=track_ids)
