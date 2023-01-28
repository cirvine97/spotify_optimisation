import pandas as pd
import numpy as np
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import regex
# Import label encoder
from sklearn.preprocessing import LabelEncoder
# Import credentials for spotify
import cred

class Playlist:
    def __init__(
        self,
        playlist_path: str,    
    ) -> None:
        self.path = playlist_path
        self.playlist = pd.read_csv(self.path, on_bad_lines='skip')
        
    def generate_features(
        self
    ) -> None:
        # Encode and normalise album date field
        self.playlist = self.playlist.sort_values(
            by=['Album Date'], 
            ascending=False
        )
        self.playlist['album_date_encoded'] = LabelEncoder().fit_transform(self.playlist['Album Date'])
        self.playlist['album_date_encoded'] = (self.playlist['album_date_encoded'] / 
                                               self.playlist['album_date_encoded'].max() * 100)
        
        # Generate intuition parameter based on how early song was added to playlist
        self.playlist['Intuition'] = self.playlist['#'] / self.playlist['#'].max() * 100
        self.playlist['Intuition'] = self.playlist['Intuition'].map(lambda x: 100 - x)
        
        # Cleaning
        self.playlist['Loudness'] = self.playlist['Loudness'].apply(lambda x: regex.sub(r'[-]|[db]', '', x))
        # self.playlist['Loudness'] = self.playlist['Loudness'].astype(int)
        # self.playlist['Loudness'] = self.playlist['Loudness']/self.playlist['Loudness'].max() * 100
        # self.playlist['Loudness'] = self.playlist['Loudness'].map(lambda x: 100 - x)
        
        # self.playlist['Time'] = self.playlist['Time'].apply(
        #     lambda x: int(x.split(':')[0]) * 60 + int(x.split(':')[1])
        #                                                     )