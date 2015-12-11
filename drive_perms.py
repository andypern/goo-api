import httplib2
import os
import sys
import re
from tabulate import tabulate

from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
from texttable import Texttable

from apiclient import errors
# ...



CLIENT_SECRET = 'client_secret.json'
SCOPES = 'https://www.googleapis.com/auth/drive.readonly.metadata'

store = file.Storage("%s-oauth2.json" % sys.argv[0])
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets(CLIENT_SECRET, SCOPES)
    creds = tools.run(flow, store)
DRIVE = build('drive', 'v2', http=creds.authorize(Http()))

files = DRIVE.files().list().execute().get('items', [])
for f in files:
    print f['title'], f['mimeType']





def retrieve_permissions(service, file_id):
  """Retrieve a list of permissions.

  Args:
    service: Drive API service instance.
    file_id: ID of the file to retrieve permissions for.
  Returns:
    List of permissions.
  """
  try:
    permissions = service.permissions().list(fileId=file_id).execute()
    return permissions.get('items', [])
  except errors.HttpError, error:
    print 'An error occurred: %s' % error
  return None

file_id = '13XqWEVsgSS-_6UdBHtbicxNUCOI4CHBsYciXBoF9LQ4'

service='drive'
retrieve_permissions(service, file_id)
