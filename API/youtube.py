import json
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build, Resource
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError

def get_auth_client_fresh(CLIENT_SECRET = 'cred.json'):
    ''' Construct Resource object for interaction with the YouTube service
    
    Args:
        CLIENT_SECRET (Optional(str)): The filename of application client info in Google format

    Returns:
        Tuple(googleapiclient.discovery.Resource, dict): A Resource object with methods for interacting with the YouTube service and tokens of authenticated user.
        None: Specified client secret cannot be found.
    '''
    SCOPES = ['https://www.googleapis.com/auth/youtube'] 
    API_SERVICE_NAME = 'youtube'
    API_VERSION = 'v3'

    try:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES) 
    except FileNotFoundError:
        return None
    # flow = Flow.from_client_secrets_file(CLIENT_SECRET, SCOPES) 
    # flow.redirect_uri = 'http://localhost:5555' # TODO: Change to web app address
    credentials = flow.run_local_server()  # TODO: implement manual flow in web app
    return build(API_SERVICE_NAME, API_VERSION, credentials = credentials), {'token':credentials.token, 'refresh_token':credentials.refresh_token, 'token_uri':credentials.token_uri}

def get_auth_client_returning(info, CLIENT_SECRET='cred.json'):
    ''' Construct Resource object for interaction with the YouTube service using given token and info.
    
    Args:
        info (Mapping[str, str]): The authorized user token in the format outputted by get_auth_client_fresh()
        CLIENT_SECRET (Optional(str)): The filename of application client info in Google format

    Returns:
        Tuple(googleapiclient.discovery.Resource, dict): A Resource object with methods for interacting with the YouTube service and tokens of authenticated user.
        None: If either arguments is in unexpected format / Specified client secret cannot be found.
    '''

    REQUIRED_FROM_CLIENT_SECRET = ['client_id', 'client_secret']
    REQUIRED_FROM_INFO = ['token', 'refresh_token', 'token_uri']
    API_SERVICE_NAME = 'youtube'
    API_VERSION = 'v3'

    # Open client secret and check for required values
    try:
        client_id = None
        client_secret = None
        token = None
        refresh_token = None
        token_uri = None

        with open(CLIENT_SECRET, 'r') as f:
            cs = json.load(f)

            if 'installed' in cs and set(REQUIRED_FROM_CLIENT_SECRET).issubset(cs['installed']):
                client_id = cs['installed']['client_id']
                client_secret = cs['installed']['client_secret']
            else:
                return None

        if set(REQUIRED_FROM_INFO).issubset(info):
            token = info['token']
            refresh_token = info['refresh_token']
            token_uri = info['token_uri']
        else:
            return None

        return build(API_SERVICE_NAME, API_VERSION, credentials = Credentials(token, refresh_token=refresh_token, token_uri=token_uri, client_id=client_id, client_secret=client_secret)), info
    except FileNotFoundError:
        return None

def query(client, query, maxResults, thumbnails=False):
    ''' Make YouTube search on the given keyword and limit result to the given number
    
    Args:
        client (googleapiclient.discovery.Resource): A Resource object with methods         for interacting with the YouTube service.
        query (str): A keyword to make query to YouTube
        MaxResults (int): Expected number of search result

    Returns:
        Sequence(dict): Query result(s)
    '''

    # Check client object type
    if type(client) != Resource:
        return None

    response = client.search().list(part='snippet',maxResults=maxResults,q=query,type='video').execute()
    videos = []

    for i in range(len(response['items'])):
        videos.append({'title':response['items'][i]['snippet']['title'],\
            'description':response['items'][i]['snippet']['description'],\
            #  'channelTitle':response['items'][i]['snippet']['channelTitle'],\
             'id':response['items'][i]['id']['videoId']})
        if thumbnails:
            videos[i]['thumbnails'] = response['items'][i]['snippet']['thumbnails']

    return videos


def create_playlist(client, title, description=''):
    ''' Create playlist using the given information. User MUST have YouTube account.

    Args:
        client (googleapiclient.discovery.Resource): A Resource object with methods for interacting with the YouTube service.
        title (str): A playlist title
        description Optional(str): A description for a playlist

    Returns:
        dict: Response from the service after successfully created a playlist
    '''

    # Check client object type
    if type(client) != Resource:
        return None

    return client.playlists().insert(part='snippet', body={'snippet':{'title':title, 'description':description, 'defaultLanguage':'EN', 'privacyStatus':'private'}}).execute()

def get_playlist(client, thumbnails=False):
    ''' Get all playlists on the account 

    Args:
        client (googleapiclient.discovery.Resource): A Resource object with methods for interacting with the YouTube service.

    Returns:
        Sequence(dict): Playlists on the account
        None: Error occurred / Parameter(s) is/are invalid
    '''

    # Check client object type
    if type(client) != Resource:
        return None

    response = client.playlists().list(part='snippet',mine=True).execute()
    playlists = []

    for i in range(len(response['items'])):
        playlists.append({'title':response['items'][i]['snippet']['title'],\
            'description':response['items'][i]['snippet']['description'],\
            #  'channelTitle':response['items'][i]['snippet']['channelTitle'],\
             'id':response['items'][i]['id']})
        if thumbnails:
            playlists[i]['thumbnails'] = response['items'][i]['snippet']['thumbnails']
    
    return playlists

def get_playlist_item(client, playlist_id, thumbnails=False):
    ''' Get all items in the specified playlist on the account 

    Args:
        client (googleapiclient.discovery.Resource): A Resource object with methods for interacting with the YouTube service.
        playlist_id (str): Playlist id of the user

    Returns:
        Sequence(dict): Items in the specified playlist. Empty if no item is in the specified playlist
        None: Error occurred / Parameter(s) is/are invalid
    '''

    # Check client object type
    if type(client) != Resource:
        return None

    try:
        response = client.playlistItems().list(part='snippet', playlistId=playlist_id).execute()
    except HttpError:
        return None

    items = []

    for i in range(len(response['items'])):
        items.append({'title':response['items'][i]['snippet']['title'],\
            'description':response['items'][i]['snippet']['description'],\
            #  'channelTitle':response['items'][i]['snippet']['channelTitle'],\
             'id':response['items'][i]['snippet']['resourceId']['videoId']})
        if thumbnails:
            items[i]['thumbnails'] = response['items'][i]['snippet']['thumbnails']
    
    return items

def insert_to_playlist(client, playlist_id, video_id):
    ''' Insert a video into a playlist using the given information.

    Args:
        client (googleapiclient.discovery.Resource): A Resource object with methods for interacting with the YouTube service.
        playlist_id (str): User playlist id
        video_id (str): Video id

    Returns:
        dict: Response from the service after successfully created a playlist
        None: Parameter(s) is/are invalid
    '''

    # Check client object type
    if type(client) != Resource:
        return None

    try:
        return client.playlistItems().insert(part='snippet', body={'snippet':{'playlistId': playlist_id, 'resourceId':{'videoId':video_id, 'kind':'youtube#video'}}}).execute()
    except HttpError:
        return None