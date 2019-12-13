# APIs

## Youtube

### Functionalities

- [x] Create playlist
- [x] List all playlists
- [x] List all items in a playlist
- [x] Add an item to a playlist

### Integration

1) Open URL for authorization from `form_url()` and let user follow the flow (TODO: change `flow.redirect_uri` in `form_url()` to match the main app)

2) Create new endpoint in Flask to handle callback and get authorization code from Google server

3) Pass Flow object from `form_url()` and code from step 2 into `get_auth_client()`

4) Use client returned by `get_auth_client()` for future interaction with YouTube service and store `cred` returned by `get_auth_client()`, so returning user does not have to do authorization again.

### Interfaces

- `form_url()`: Form an authorization URL for the user

```python
>>> flow, url = form_url()
>>> type(flow)
<class 'google_auth_oauthlib.flow.Flow'>
>>> url
'https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=1033796560404-5bukd8lde4d560i50tn0295ouogsfelt.apps.googleusercontent.com&redirect_uri=http%3A%2F%2Flocalhost%3A5555&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fyoutube&state=2cE50TrfI89Z31OLvoIQjdZEGFTkNC&access_type=offline'
```

- `get_auth_client()`: Construct Resource object for interaction with the YouTube service

```python
>>> client, cred = get_auth_client(flow, 'CODE_FROM_CALLBACK')
>>> client
<googleapiclient.discovery.Resource object at 0x1033fd450>
>>> cred_tokens.keys() # User tokens to be stored for future usage
dict_keys(['token', 'refresh_token', 'token_uri'])

```

<!-- - `get_auth_client_fresh`: Get new user authentication to Youtube account to interact with playlist

```python
>>> client, cred_tokens = get_auth_client_fresh()
# OAuth flow to get user authentication
.
.
.
>>> client
<googleapiclient.discovery.Resource object at 0x1033fd450>
>>> cred_tokens.keys() # User token to be stored for future usage
dict_keys(['token', 'refresh_token', 'token_uri'])
``` -->

- `get_auth_client_returning()`: Retrieve previous user authentication to Youtube account to interact with playlist

```python
>>> import json
>>> with open('cred_auth.json', 'r') as c:
...     info = json.load(c)
...
>>> info.keys() # Loaded user tokens
dict_keys(['token', 'refresh_token', 'token_uri'])
>>> client, cred_tokens = get_auth_client_returning(info)
>>> client
<googleapiclient.discovery.Resource object at 0x103517950>
>>> cred_tokens.keys() # Has same content as info variable
dict_keys(['token', 'refresh_token', 'token_uri'])
```

- `query()`: Make Youtube query and return videos that match the specified keyword. Can set `thumbnails=True` to get video thumbnails.

```python
>>> query(client, 'Bad Guy - Billie Eilish', maxResults=3)
>>> result = query(client, 'Bad Guy - Billie Eilish', maxResults=3)
>>> len(result)
3
>>> result[0].keys()
dict_keys(['title', 'description', 'id'])
>>> result[0]
{'title': 'Billie Eilish - bad guy', 'description': 'Listen to "bad guy" from the debut album "WHEN WE ALL FALL ASLEEP, WHERE DO WE GO?", out now: http://smarturl.it/BILLIEALBUM Follow Billie Eilish: ...', 'id': 'DyDfgMOUjCI'}
```

- `create_playlist()`: Create a playlist on the user account with the specified name

```python
>>> result = create_playlist(client, 'Chilly Winter', 'Good songs to listen in the winter')
>>> result.keys() # API response containing information about the newly created playlist
dict_keys(['kind', 'etag', 'id', 'snippet'])
result['snippet'].keys()
dict_keys(['publishedAt', 'channelId', 'title', 'description', 'thumbnails', 'channelTitle', 'defaultLanguage', 'localized'])
```

- `get_playlist()`: List playlist(s) on the user account. Can set `thumbnails=True` to get playlist thumbnails.

```python
>>> result = get_playlist(client)
>>> len(result)
1
>>> result[0].keys()
dict_keys(['title', 'description', 'id'])
>>> result[0]
{'title': 'Chilly Winter', 'description': 'Good songs to listen in the winter', 'id': 'PLAYLIST_ID'}
```

- `insert_to_playlist()`: Insert an item one at a time into the specified playlist id on the user account

```python
>>> result = insert_to_playlist(client, 'PLAYLIST_ID', 'VIDEO_ID')
>>> result.keys() # API response
dict_keys(['kind', 'etag', 'id', 'snippet'])
```

- `get_playlist_item()`: List item(s) in the specified playlist id on the user account. Can set `thumbnails=True` to get video thumbnails.

```python
>>> result = get_playlist_item(client, 'PLAYLIST_ID')
>>> len(result)
1 # Number of item(s) in the playlist
>>> result[0].keys() # First video information
dict_keys(['title', 'description', 'id'])
```