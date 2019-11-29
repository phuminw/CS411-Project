# APIs

## Youtube

### Interfaces

- get_auth_client_fresh(): Get new user authentication to Youtube account to interact with playlist
- get_auth_client_returning(): Retrieve previous user authentication to Youtube account to interact with playlist
- query(): Make Youtube query and return videos that match the specified keyword
- create_playlist(): Create a playlist on the user account with the specified name
- get_playlist(): List playlist(s) on the user account
- get_playlist_item(): List item(s) in the specified playlist id on the user account
- insert_to_playlist(): Insert an item one at a time into the specified playlist id on the user account
