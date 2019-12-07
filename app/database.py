import json
from pymongo import MongoClient
import subprocess

#global reference to db collection
USERS = None
client = None


def init_db():
  """ initialize db connection and populate USERS with collection reference"""
  global USERS
  global client

  command = 'mongod'
  subprocess.Popen([command])

  client = MongoClient('localhost')
  USERS = client.db.cl
  
  return client

def init_user(user_id):
  """initialize a document for an individual user"""
  user = {
       'user_id'   : user_id,
       'playlists' : {}
       
  }
  USERS.insert_one(user)

def insert_playlist_old(user_id, playlist_data, playlist_name):
  """takes json data for spotify playlist and inserts it into the user_id's document
     playlist_data (string): assuming data in the same format as example2.json (which is not valid json?)
     playlist_name (string): take in name for the playlist because the data does not contain the name
  """
  user = USERS.find_one({'user_id': user_id})
  if (user == None):
    return None

  playlist = []

  songs = eval(playlist_data)

  # grab the interesting data from the spotify data
  for track_data in songs:
    track = track_data['track']
    
    #actual data items we want
    name = track['name']
    track_id = track['id']
    artists = []
    for artist in track['artists']:
      artists += [artist['name']]
  
    playlist += [(name, track_id, artists)]

  old_playlists = user['playlists']
  old_playlists[playlist_name] = playlist
  insert_key(user_id, 'playlists', old_playlists)


def get_playlist(user_id, playlist_name):
  """ returns playlist from particular user, returns None if user or playlist not found"""

  user = USERS.find_one({'user_id' : user_id})
  
  if (user == None):
    return None
 
  playlist = user['playlists'][playlist_name]
  return playlist

def insert_key(user_id, key, value):
   """ insert an arbitrary key:value pair into a user document"""  

   USERS.update_one({'user_id':user_id}, {'$set':{key : value}}, True)


def get_user(user_id):
   """returns dictionary representing a user"""
   return USERS.find_one({'user_id':user_id})

def youtube_query_songs_old(user_id, playlist_name):
  """return a string list of song names appended to artist names"""
  user = USERS.find_one({'user_id' : user_id})

  if (user == None):
    return None

  search_strings = []

  for song in user['playlists'][playlist_name]:
    s = ""
    s = s + song[0] + ' '
    for i in range(len(song[2])):
      s = s + song[2][i] + ' '
    search_strings += [s]

  return search_strings

def input_playlist(user_id, playlist_name, playlist_image, playlist):
  ''' inputs playlist into db entry for user_id
      user_id: string
      playlist_name: string
      playlist_image: string (url)
      playlist: array of [song name, song link, artist name]
  '''
  
  user = USERS.find_one({'user_id': user_id})
  if (user == None):
    return None

  
  old_playlists = user['playlists']
  old_playlists[playlist_name] = playlist_image, playlist
  insert_key(user_id, 'playlists', old_playlists)

def youtube_query_songs(user_id, playlist_name):
  """returns a string list of song names appended to artist names"""
  
  user = USERS.find_one({'user_id' : user_id})

  if (user == None):
    return None

  search_strings = []  
 
  for song in user['playlists'][playlist_name]:
    search_strings += [song[0] + ' ' + song[2]]

  return search_strings