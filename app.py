import json
from flask import Flask, request, redirect, g, render_template, url_for
import requests
from urllib.parse import quote
from app import database
from app.youtube import *

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

# Store flow object to use for Youtube
flow = None
client_ob = None

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

    # Store the user's Spotify username
    username = profile_data['display_name']
    print("USER: ", username)

    ######################
    # TODO: MongoDB: Store the following data
        # username
        # playlists
    # Initialize the db connection

   # database.init_db()

    # Initialize a document for the current user
   # database.init_user(username)

    ######################

    playlists = []

    # playlist_data["items"] contains all of user's playlists; their track names, their artists, and all their links
    # The for loop iterates through the list of playlists, working with one playlist at a time
    for playlist in playlist_data["items"]:
        
        # Store the playlist name
        # print("Playlist Name: {} \n".format(playlist['name']))
        playlist_name = playlist['name']
       
        # Store the playlist's link (to the Spotify playlist)
        # print("Playlist Link: {} \n".format(playlist['external_urls']['spotify']))
        playlist_link = playlist['external_urls']['spotify']


        # Attempt to grab the Playlist's image 
        try: 
            # Store the playlist image's URL
            # print("Playlist Image: {} \n".format(playlist['images']))
            playlist_image = playlist['images'][0].get('url')
        except:
            # If no image available, print the response
            print("[!!!] No Playlist Image URL!")

        # Load the playlist data: storing the data structure containing the playlist's entire track data
        track_response = requests.get(playlist['tracks']['href'], headers=authorization_header)
        # print("API response: {} \n".format(track_response))

        # Convert the returned track data for this specific playlist to plain text and access the stored track info
        track_data = json.loads(track_response.text)
        track_data = track_data['items']

        # Three arrays containing individual track information for current accessed playlist
        # Each unique array position corresponds to the same track
        # E.g. 
            #   arr_track_names[0]
            #   arr_track_artists[0]
            #   arr_track_artist_links[0]
            #
            #   Contains information on the track name, the track artist, and the artist link for track 1 on current playlist

        arr_track_names = []
        arr_track_artists = []
        arr_track_artist_links = []

        # The for loop iterates through the track_data, working on one song/track at a time
        # Pulls the track's name, artist, and artist link and appends to the respective arrays declared above
        for items in track_data:
            try:
                # Spotify stores The track name and artist info in a dict; this extracted info is stored in var track_strings 
                track_strings = items['track']['album']['artists'][0]

                # Extract the track name and store into array arr_track_names 
                # print("Track Name: ", items['track']['name'])
                track_name = items['track']['name']
                arr_track_names.append(track_name)

                # Extract the track artist and store into array arr_track_artists
                # print("Track Artist: ", track_strings.get("name"))
                track_artist = track_strings.get("name")
                arr_track_artists.append(track_artist)

                # Extract the track artist link and store into array arr_track_artist_links
                # print("Track Artist URL: ", track_strings.get("external_urls").get("spotify"))
                track_artist_link = track_strings.get("external_urls").get("spotify")
                arr_track_artist_links.append(track_artist_link)

            except:
                # If the playlist is empty, then the playlist on the application will be displayed will be empty
                # Will break to avoid storing extraneous information into playlists
                print("[!!!] ERROR READING PLAYLIST CONTENTS")
                break
        
        # Once the current playlist has been completely iterated through, the arrays will then be appended to the playlists array
        # Each playlist element in playlists possess the structure detailed below in the 'Returns' section.
        playlists.append([[playlist_name, playlist_link, playlist_image], list(zip(arr_track_names, arr_track_artists, arr_track_artist_links))])

        # db_playlist = list(zip(arr_track_names, arr_track_artists, arr_track_artist_links))

    '''
    Stores the following into the MongoDB database:

        username: The username of the user, unique to each Spotify user

        playlists: Contains all the information returned from Spotify on the user playlists
            The structure is the following:
                [ [playlist name, playlist link, playlist image] ,  zipped( [(track name, artist, link)] )
                E.g. You will see the following information structure:
                    [ ['Summer Vibes', 'https://open.spotify.com/artist/thisisanexample', 'https://imagelink'], [...] ]
                    The [...] could be:
                        ('Stronger', 'Kanye West', 'https://open.spotify.com/artist/5K4W6rqBFWDnAN6FQUkS6x'), 
                        ('Rap God', 'Eminem', 'https://open.spotify.com/artist/7dGJo4pcD2V6oG8kP0tJRR')

    Once stored, redirected to Home page
    '''

    #database.input_playlist(username, playlist_name, db_playlist)

    return redirect(url_for("youtubeLogin"))

'''
An attempt to implement server-side logout functionality; Spotify provides a URL to logout 
    which is presently used instead
'''
# @app.route("/logout")
# def logout():
#     print("We're at least in the logout!")
#     if request.method == 'POST':
#         print("Logging out!")
#         if 'Logout' in request.form:
#             return redirect("https://accounts.spotify.com/en/logout", code=302)
#     else:
#         print("Something is wrong here!")

'''
    User must log into Youtube first
'''
@app.route("/youtube_login", methods = ['GET', 'POST'])
def youtubeLogin():
    global flow
    if request.method == 'POST':
        print("Received POST request for Youtube Login!")
        if request.form['youtube'] == 'youtube':
            flow, url = form_url()
            return redirect(url, code=302)
    else:
        return render_template("youtube_login.html")

'''
    The implementation below allows the user to redirect to another webpage using POST requests in HTML
'''
@app.route("/home", methods = ['GET', 'POST'])
def displayHome():
    if request.method == 'POST':
        print("Received POST request!")
        if request.form['newpage'] == 'newpage':
            return render_template("newpage1.html")
    else:
        code = request.args.get('code')
        client_ob, cred = get_auth_client(flow, code)
        print(get_playlist(client_ob))
        # TODO: Store Youtube cred into database, linked to specific user
        # TODO: Check database if user cred works
        return render_template("newpage2.html")
    
if __name__ == "__main__":
    app.run(debug=True, port=PORT)