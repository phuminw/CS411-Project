import json
from flask import Flask, request, redirect, g, render_template
import requests
from urllib.parse import quote

import configparser

# Authentication Steps, paramaters, and responses are defined at https://developer.spotify.com/web-api/authorization-guide/
# Visit this url to see all the steps, parameters, and expected response.

app = Flask(__name__)

config = configparser.ConfigParser()
config.read("config.cfg")

#  Client Keys
CLIENT_ID = config.get('DEFAULT', 'client_id')
CLIENT_SECRET = config.get('DEFAULT', 'client_secret')

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

# Server-side Parameters
CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 5000
REDIRECT_URI = "{}:{}/callback/q".format(CLIENT_SIDE_URL, PORT)
SCOPE = "playlist-modify-public playlist-modify-private"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()

auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    # "state": STATE,
    # "show_dialog": SHOW_DIALOG_str,
    "client_id": CLIENT_ID
}

@app.route("/")
def index():
    # Auth Step 1: Authorization
    url_args = "&".join(["{}={}".format(key, quote(val)) for key, val in auth_query_parameters.items()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    return redirect(auth_url)


@app.route("/callback/q")
def callback():
    # Auth Step 4: Requests refresh and access tokens
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload)

    # Auth Step 5: Tokens are Returned to Application
    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]

    # Auth Step 6: Use the access token to access Spotify API
    authorization_header = {"Authorization": "Bearer {}".format(access_token)}

    # Get profile data
    user_profile_api_endpoint = "{}/me".format(SPOTIFY_API_URL)
    profile_response = requests.get(user_profile_api_endpoint, headers=authorization_header)
    profile_data = json.loads(profile_response.text)

    # Get user playlist data
    playlist_api_endpoint = "{}/playlists".format(profile_data["href"])
    playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
    playlist_data = json.loads(playlists_response.text)

    # Combine profile and playlist data to display
    display_arr = [profile_data] + playlist_data["items"]

    print("[~~~] Displaying profile data!")
    username = profile_data['display_name']
    print("USER: ", username)

    playlists = []

    for playlist in playlist_data["items"]:
        # print("[!!!] New Playlist Data!")

        # print(playlist)

        # print("Playlist Name: {} \n".format(playlist['name']))
        playlist_name = playlist['name']
        
        # print("Playlist Link: {} \n".format(playlist['external_urls']['spotify']))
        playlist_link = playlist['external_urls']['spotify']

        try: 
            # print("Playlist Image: {} \n".format(playlist['images']))
            playlist_image = playlist['images'][0].get('url')
        except:
            print("[!!!] No Playlist URL!")

        track_response = requests.get(playlist['tracks']['href'], headers=authorization_header)

        # print("API response: {} \n".format(track_response))

        track_data = json.loads(track_response.text)
        track_data = track_data['items']

        # arr_track_addededbys = []
        arr_track_names = []
        arr_track_artists = []
        arr_track_artist_links = []

        for items in track_data:
            # print("Track added by: ", items['added_by']['external_urls']['spotify'])
            # track_addedby = items['added_by']['external_urls']['spotify']
            # arr_track_addededbys.append(track_addedby)
            
            try:
                # The track name and artist is stored in a dict, var track_strings 
                track_strings = items['track']['album']['artists'][0]
                #print("Track Name: ", items['track']['name'])
                track_name = items['track']['name']
                arr_track_names.append(track_name)

                # print("Track Artist: ", track_strings.get("name"))
                track_artist = track_strings.get("name")
                arr_track_artists.append(track_artist)

                #print("Track Artist URL: ", track_strings.get("external_urls").get("spotify"))
                track_artist_link = track_strings.get("external_urls").get("spotify")
                arr_track_artist_links.append(track_artist_link)

            except:
                # If the playlist is empty, then the playlist on the application will be displayed but empty as well
                print("[!!!] ERROR READING PLAYLIST CONTENTS")
                break
            
        playlists.append([[playlist_name, playlist_link, playlist_image], zip(arr_track_names, arr_track_artists, arr_track_artist_links)])

    '''
    Returns:

        username: The username of the user, unique to each Spotify user

        playlists: Contains all the information returned from Spotify on the user playlists
            The structure is the following:
                [ [playlist name, playlist link, playlist image] ,  zipped( [(track name, artist, link)] )
                E.g. You will see the following information structure:
                    [ ['Summer Vibes', 'https://open.spotify.com/artist/thisisanexample', 'https://imagelink'], [...] ]
                    The [...] could be:
                        ('Stronger', 'Kanye West', 'https://open.spotify.com/artist/5K4W6rqBFWDnAN6FQUkS6x')
                        ('Rap God', 'Eminem', 'https://open.spotify.com/artist/7dGJo4pcD2V6oG8kP0tJRR')
    '''

    return render_template("home.html", username=username, playlists=playlists)

# @app.route("/logout")
# def logout():
#     print("We're at least in the logout!")
#     if request.method == 'POST':
#         print("Logging out!")
#         if 'Logout' in request.form:
#             return redirect("https://accounts.spotify.com/en/logout", code=302)
#     else:
#         print("Something is wrong here!")

if __name__ == "__main__":
    app.run(debug=True, port=PORT)