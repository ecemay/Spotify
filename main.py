from billboard_to_spotify import BillboardToSpotifyt
import os
USER_ID = os.environ["USER_ID"]
CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
REDIRECT_URI= 'https://example.com'

## enter a date for reaching top 100 song of this date
date = input("Enter a date as YYYY-MM-DD:\n")

billboard_playlist = BillboardToSpotifyt(user_id=USER_ID,date=date, client_secret=CLIENT_SECRET,client_id=CLIENT_ID,redirect_uri=REDIRECT_URI)

## To reach token you should call the function of request_user_authorization. This process has two step. 1. Go to link
#anc confirm authorization. 2. paste the code in the url code= part.As a result of this two-step process,
# the authorization process is completed and the token is accessed.
billboard_playlist.request_user_authorization()

## create a private spotify playlist named by the entered date by calling the function creation_playlist
billboard_playlist.creating_playlist()
## add songs to playlist
billboard_playlist.adding_playlist()
