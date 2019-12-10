import json
from flask import Flask, request, redirect, g, render_template, url_for
import requests
from urllib.parse import quote
from app.database import *
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
current_user = ""

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
    global current_user
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

    # Set up the current user for lookup 
    current_user = username
    print("USER: ", username)

    # Initialize the db connection
    init_db()

    # Initialize a document for the current user
    init_user(username)

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

        arr_track_info = []

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

                # Combine the information to reduce string extraction from the database
                track_info = track_name + " by " + track_artist + " lyrics"
                arr_track_info.append(track_info)

            except:
                # If the playlist is empty, then the playlist on the application will be displayed will be empty
                # Will break to avoid storing extraneous information into playlists
                print("[!!!] ERROR READING PLAYLIST CONTENTS")
                break
        
        # Once the current playlist has been completely iterated through, the arrays will then be appended to the playlists array
        # Each playlist element in playlists possess the structure detailed below in the 'Returns' section.
        #playlists.append([[playlist_name, playlist_link, playlist_image], list(zip(arr_track_names, arr_track_artists, arr_track_artist_links))])
        playlists.append([[playlist_name, playlist_link, playlist_image], arr_track_info])


        # Create data structure to store current playlist data in
        db_playlist = list(zip(arr_track_names, arr_track_artists, arr_track_artist_links))

        # Store playlist information on current user into db
        input_playlist(username, playlist_name, playlist_image, arr_track_info)

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
    User must log into Youtube first. This section prompts the user to click a button to initiate the log in process

    Once clicked, the page will redirect the user to login and then redirect the user back to a predetermined URL set in app/youtube.py under function form_url
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
    The user will not see this page redirect

    This function seeks to set up the user client id in order to create playlists

    Function had to be isolated as similarly to the Spotify callback function, any POST request on our server side will render the application useless due to the interference of third party POST requests

    Redirects the user to the home page, viewing his or her playlists
'''
@app.route("/quicksetup")
def settingUpCode():
    global client_ob
    auth_token = request.args['code']
    client_ob, cred = get_auth_client(flow, auth_token)
    # TODO: Need to store cred into mongodb database for persistent user login
    return redirect(url_for('displayHome'))

'''
    The implementation below allows the user to redirect to another webpage using POST requests in HTML
'''
@app.route("/home", methods = ['GET', 'POST'])
def displayHome():
    global current_user
    global client_ob

    # At this point, we are logged into both Spotify and YouTube. We are also connected to a MongoDB to extract information from
    # Here, we will begin to extract the playlist information from MongoDB and then create YouTube playlists from them
    user_dict = get_user(current_user)
    playlist_titles = list(user_dict['playlists'].keys())

    # Store image urls for each playlist
    playlist_images = []

    # Store track information for each playlist
    # This is an array of arrays, each element in the array corresponds with its respective playlist
    playlist_track_info = []

    # Extract the playlist titles and individual tracks from each playlist from the MongoDB and store into arrays
    for indiv_playlist in playlist_titles:
        playlist_images.append(user_dict["playlists"][indiv_playlist][0])
        playlist_track_info.append(user_dict["playlists"][indiv_playlist][1])

    # Zip the titles and the images to pass to HTML through Django
    datapass = zip(playlist_titles, playlist_images)

    # If there is a POST request, read the value sent from the USER to choose the correct playlist to redirect the user to
    if request.method == 'POST':
        playlist_title = request.form['newpage']
        if playlist_title in playlist_titles:
            # Find the tracks under the playlist named 'playlist_title'
            trackinfo = playlist_track_info[playlist_titles.index(playlist_title)]

            '''
            [!!!] Begin Implementation for YouTube Playlist Generation
            '''

            # Create a new playlist
            pl_id = create_playlist(client_ob, playlist_title, "Playlist " + playlist_title + " converted from Spotify to YouTube")

            # Add a short embeddable video at the beginning of each playlist; if the first video is unable to be embedded, then the entire playlist will not be attached
            #insert_to_playlist(client_ob, pl_id, 'jhFDyDgMVUI')

            # Begin adding the tracks to the playlist
            # To begin, first query all songs and add to an array
            y_tracks_ids = []
            # Current playlist tracks all stored in trackinfo
            for vid in trackinfo:
                # Query for max 1 result and add to video array
                result = query(client_ob, vid, 1)
                print("[!!!] RESULT: ", result)
                y_tracks_ids.append(result[0]['id'])

            print("\n[!!!] TRACKS: ", y_tracks_ids)

            # Insert all the videos queried into the playlist
            insert_videos_to_playlist(client_ob, pl_id, y_tracks_ids)

            # Last step is to assemble the Playlist URL and embed the string into HTML
            yurl = "https://www.youtube.com/embed/videoseries?list={}".format(pl_id)

            return render_template("playlist.html", playlist_title=playlist_title, yurl=yurl)
        else:
            print("User return not in Playlist Title, redirecting . . .")
            return render_template("view_playlists.html", username=current_user, datapass=datapass)
        # else:
        #     return render_template("view_playlists.html")
    else:
        return render_template("view_playlists.html", username=current_user, datapass=datapass)
    


if __name__ == "__main__":
    app.run(debug=True, port=PORT)