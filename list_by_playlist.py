#!/usr/bin/python

import httplib2
import os
import sys
import re

from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
from texttable import Texttable


# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the Google Developers Console at
# https://console.developers.google.com/.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "client_secrets.json"

#put a list of playlists that you want to parse here

playlistList = ['PLYl39p8cOuS-ywJ6n1aaeX_QykaLt4ki0' , 'PLYl39p8cOuS_sLDo3KUl_dr4iel5Boj9A'];


# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the Developers Console
https://console.developers.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

# This OAuth 2.0 access scope allows for read-only access to the authenticated
# user's account, but not other types of account access.
YOUTUBE_READONLY_SCOPE = "https://www.googleapis.com/auth/youtube.readonly"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
  message=MISSING_CLIENT_SECRETS_MESSAGE,
  scope=YOUTUBE_READONLY_SCOPE)

storage = Storage("%s-oauth2.json" % sys.argv[0])
credentials = storage.get()

if credentials is None or credentials.invalid:
  flags = argparser.parse_args()
  credentials = run_flow(flow, storage, flags)

youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
  http=credentials.authorize(httplib2.Http()))

# Retrieve the contentDetails part of the channel resource for the
# authenticated user's channel.
channels_response = youtube.channels().list(
  mine=True,
  part="contentDetails"
).execute()

table = Texttable()

for uploads_list_id in playlistList:
  # From the API response, extract the playlist ID that identifies the list
  # of videos uploaded to the authenticated user's channel.
  #uploads_list_id = channel["contentDetails"]["relatedPlaylists"]["uploads"]
  uploads_list_id = 'PLYl39p8cOuS-ywJ6n1aaeX_QykaLt4ki0' 

  print "Videos in list %s" % uploads_list_id

  # Retrieve the list of videos uploaded to the authenticated user's channel.
  playlistitems_list_request = youtube.playlistItems().list(
    playlistId=uploads_list_id,
    part="snippet",
    maxResults=50
  )

  while playlistitems_list_request:
    playlistitems_list_response = playlistitems_list_request.execute()

    #print playlistitems_list_response
    #Print information about each video.
    for playlist_item in playlistitems_list_response["items"]:
      title = playlist_item["snippet"]["title"]
      video_id = playlist_item["snippet"]["resourceId"]["videoId"]


      video_response = youtube.videos().list(
      id=video_id,
      part='contentDetails, snippet'
      ).execute()
      
      for vidresponse in video_response["items"]:
        duration = vidresponse["contentDetails"]["duration"]
        tags = vidresponse["snippet"]["tags"]

      replacedDuration = re.sub('[PT]', '', duration)
      vidLink = "https://www.youtube.com/watch?v=" + video_id
      #print "%s https://www.youtube.com/watch?v=%s %s" % (title, video_id, replacedDuration)

      table.add_rows([['Title', 'Tags', 'Link', 'Duration'], [title, tags, vidLink, replacedDuration]])



    playlistitems_list_request = youtube.playlistItems().list_next(
      playlistitems_list_request, playlistitems_list_response)

#table width: title = 25, link = 45, duration=10
  table.set_cols_width([25,45,10])
  print table.draw()
  print