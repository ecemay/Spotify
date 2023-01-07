import json
import requests
import base64

import requests
from bs4 import BeautifulSoup


class BillboardToSpotifyt:
    def __init__(self, user_id, client_id, client_secret, redirect_uri, date):

        self.url ="https://www.billboard.com/charts/hot-100/"
        self.user_id = user_id

        self.date = date
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.endpoint = 'https://accounts.spotify.com/authorize'
        self.scope = 'playlist-modify-private playlist-read-private'
        self.token_endpoint  ='https://accounts.spotify.com/api/token'
        self.access_token =""

    def request_user_authorization(self):
        """ Two-step function returns access_code to use in the next steps.Go to link in the terminal, accept authorization
        and copy the code (you should find in the "code=" part) in url.Then paste the code in terminal"""
        params = {
              'response_type': 'code',
              'client_id': self.client_id,
              'scope': self.scope,
              'redirect_uri': self.redirect_uri,
        }

        self.r = requests.get(self.endpoint, params=params)

        print(self.r.url)
        auth = base64.b64encode(f'{self.client_id}:{self.client_secret}'.encode('ascii')).decode('ascii')
        code = input("paste code here: ")
        headers = {
              'Authorization': f'Basic {auth}',
              'Content-Type':'application/x-www-form-urlencoded'
          }

        data = {
            'grant_type': 'authorization_code',
            'code' : code,
            'redirect_uri': self.redirect_uri
          }

        r = requests.post(self.token_endpoint, headers=headers, data=data)
        self.access_token= f"Bearer {r.json()['access_token']}"
        return self.access_token

########################## Picking hot 100 song for a certain date from Billboard#######################################
    def billboard_top_100(self):
        """ takes top 100 songs for a certain date from the Billboard website and format songs list for using spotify api. Returns formatted song list """
        url = self.url+ self.date
        respond  =requests.get(url)
        #print(respond.status_code)
        website_html = respond.text
        soup = BeautifulSoup(website_html, "html.parser")
        song_names_spans = soup.find_all("h3" , class_="c-title a-no-trucate a-font-primary-bold-s u-letter-spacing-0021 lrv-u-font-size-18@tablet lrv-u-font-size-16 u-line-height-125 u-line-height-normal@mobile-max a-truncate-ellipsis u-max-width-330 u-max-width-230@tablet-only", id="title-of-a-story")
        song_names = [song.getText() for song in song_names_spans]
        formatted_songs= [songs.replace('\t','').replace('\n','').replace(' ','%20') for songs in song_names]
        return formatted_songs

    def creating_playlist(self):
        """creates a private Spotify playlist"""

        self.playlist_endpoint = f"https://api.spotify.com/v1/users/{self.user_id}/playlists"

        headers = { "Authorization":self.access_token,
                    "Content-Type": "application/json",
                    'scope':'playlist-modify-private'
                    }
        data ={"name": f" {self.date} - Billboard Top 100",
               "description": "created using Python",
               "public":False
               }
        response = requests.post(self.playlist_endpoint, headers=headers, json=data)
        # print(response.status_code)
        return response.json()

# ########################################## Finding songs uris###########################################################
    def song_uris(self):
        """reachs uri parameters of songs and return a uris array ready for use in the next steps"""
        uris_array = []
        self.songuris_endpoint = 'https://api.spotify.com/v1/search?'
        headers = {"Content-Type": "application/json", "Authorization": self.access_token}
        formatted_songs = self.billboard_top_100()
        for i in formatted_songs:
            try:
                params = {"q":i,
                          "type":"track"
                         }
                response = requests.get(self.songuris_endpoint, params=params, headers = headers)
                response = response.json()
                uris = response["tracks"]['items'][0]['uri']

            except IndexError:
                continue
            finally:
                # print(uris)
                uris_array.append(uris)
        uris_array = uris_array[0:99]
        # uris_array = ','.join(uris_array)
        return uris_array

# ############################GET PLAYLIST ID############################################################################
    def get_playlist_id(self):
        """returns an endpoint to use in the next function which is to add all songs to the playlist"""
        self.base_url = f'https://api.spotify.com/v1/users/{self.user_id}/playlists'
        params = {"limit":20,
                  "offset":0,
                  "scope": "playlist-read-private"}

        headers_playlist = {"Content-Type": "application/json",
                            "Authorization": self.access_token}
        response_playlist = requests.get(self.base_url, params=params, headers = headers_playlist)

        response_playlist = response_playlist.json()
        endpoint =  response_playlist['items'][0]['tracks']['href']
        return endpoint


# ######################################## Adding songs to list ##########################################################
    def adding_playlist(self):
        """adds songs from Billboard website to Spotify playlist just created"""
        ENDPOINT = self.get_playlist_id()
        uri = self.song_uris()
        # print(uri)
        body = {"uris":uri,"position":0
                }
        headers = {"Content-Type": "application/json", "Authorization": self.access_token}
        response = requests.post(ENDPOINT, headers = headers, json=body)
        print(response.status_code)
        return response.json()
