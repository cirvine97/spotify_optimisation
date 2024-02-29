import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth

import cred

# Instantiate the Spotipy object
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=cred.client_ID,
                                               client_secret=cred.client_SECRET,
                                               redirect_uri=cred.redirect_url,
                                               scope='playlist-read-private'))

class Playlist:
    """Retrieves and stores metadata of a Spotify playlist.
    """
    def __init__(
            self, 
            playlist_id
        ):
        self.playlist_id = playlist_id
        self.playlist = sp.playlist_tracks(playlist_id)
        self.playlist_metadata_df = self.get_playlist_data()
    
    def get_audio_features(
            self, 
            track_id
        ):
        audio_features = sp.audio_features(track_id)
        return audio_features[0] if audio_features else {}
    
    def get_artist_genres(
            self, 
            artist_id
        ):
        artist_data = sp.artist(artist_id)
        return artist_data['genres']
    
    def get_playlist_data(
            self
        ):
        track_data = []

        for item in self.playlist['items']:
            track = item['track']
            track_id = track['id']
            audio_features = self.get_audio_features(track_id)

            # Get genre info of artists
            artist_ids = []
            for artist in track['artists']:
                artist_ids.append(artist['id'])
            genres = []
            for artist_id in artist_ids:
                genres += self.get_artist_genres(artist_id)
            # Remove duplicates
            genres = set(genres)

            track_info = {
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
                'Time Signature': audio_features.get('time_signature', None),
                'Genres': genres,
                'Top Genre': list(genres)[0] if genres else None
            }

            track_data.append(track_info)

        playlist_df = pd.DataFrame(track_data)

        return playlist_df
    
