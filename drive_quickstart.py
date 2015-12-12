from __future__ import print_function
import httplib2
import os
import sys

from apiclient import discovery
from apiclient import errors
import oauth2client
from oauth2client import client
from oauth2client import tools

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive API Python Quickstart'

###################
#
#
#TODO:
# * implement variables for query/filter/etc
# * inspect main() for error handling
# * make more modular
#
####################


#
#some specific variables
#

userName = "jhong"

fileFilter = "vvv"

filterQuery = "modifiedDate>='2015-12-09T12:00:00' and title contains 'vvv'"

returnedResults = 1000
#
#end variables
#

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def cleanup():

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v2', http=http)

    results = service.files().list(q="modifiedDate>='2015-12-09T12:00:00' and title contains 'vvv'", maxResults=1000).execute()
    items = results.get('items', [])
    if not items:
        print('No files found.')
    else:
        returnedResults = len(items)
        for item in items:
            try:
                if "jhong" in item['lastModifyingUser']['emailAddress']:
                    
                    revs = service.revisions().list(fileId=item['id']).execute()
                    #only do things to files that have 2 rev's..those w/ more may require tender care..
                    if len(revs['items']) == 2:
                        #that means we have a backup, usually the [0] index is the older one, but lets make sure
                        if 'vvv' in revs['items'][1]['originalFilename']:
                            try:
                                revId = revs['items'][1]['id']
                                oldFileName = revs['items'][0]['originalFilename']
                                oldFileModDate = revs['items'][0]['modifiedDate']
                                print("deleting revision " + revs['items'][1]['originalFilename'])
                                service.revisions().delete(
                                    fileId=item['id'], revisionId=revId).execute()
                            except errors.HttpError, error:
                                print('http error %s' %(error))

                            #now, rename the 'vvv' file to original name, which we can get from the other rev
                            try:
                                #first, pull all file metadata
                                objFile = service.files().get(fileId=item['id']).execute()
                                #set the attributes we want to change
                                objFile['title'] = oldFileName
                                objFile['modifiedDate'] = oldFileModDate

                                #execute the change, note we need to set the 'setModifiedDate' flag
                                updated_file = service.files().update(
                                    fileId=item['id'],
                                    body=objFile,
                                    modifiedDateBehavior='fromBody',
                                    setModifiedDate='true').execute()
                                
                            except errors.HttpError, error:
                                print('An error occurred: %s' % error)

            except KeyError:
                print ("key error..skip")
            except UnicodeEncodeError:
                print ("unicode error, skip")
            #print (item['title'])

if returnedResults == 1000:
    cleanup()
