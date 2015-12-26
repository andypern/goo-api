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
# * implement a 'list only' so that we can see what matches
# * implement logging so we can keep the GUID somewhere in case we need it
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
        print("results: %s" %(returnedResults))
        for item in items:
            try:
                if "jhong" in item['lastModifyingUser']['emailAddress']:
                    
                    revs = service.revisions().list(fileId=item['id']).execute()
                    print ("working on : %s" %(item['title']))
                    #Items with only 1 revision may have been 'cleaned' but not renamed, do something with them
                    if len(revs['items']) == 1:
                        if not 'vvv' in revs['items'][0]['originalFilename']:
                            print("replacing with original filename: %s" %(revs['items'][0]['originalFilename']))
                            try:
                                #first, pull all file metadata
                                objFile = service.files().get(fileId=item['id']).execute()
                                oldFileName = revs['items'][0]['originalFilename']
                                oldFileModDate = revs['items'][0]['modifiedDate']
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
                   
                 #items with 2 or more revisions require that we count the revision, delete most current, and replace with previous. Except
                 # when more than one revision is 'bad', in which case we have to walk backwards until we find a good one.  We don't want to go all the way back in case there are
                 # multiple 'good' versions.
                 # also, we have to find the 'originalFilename' differently, because it may still be the 'bad' one, so we'll have to use from rev's.
                if len(revs['items']) >= 2:
                    #set a 'fixed' flag so we can break out of the loop after we've fixed
                    fixedFlag = 0
                    #note: we can't walk through it in array order, we have to walk in backwards order
                    arrayIndex = len(revs['items']) - 1
                   
                    sys.exit
                    while (arrayIndex >=0):
                        #go through each rev, look for bad ones and delete
                        if 'vvv' in revs['items'][arrayIndex]['originalFilename']:
                            try:
                                revId = revs['items'][arrayIndex]['id']
                                print("deleting revision " + revs['items'][arrayIndex]['originalFilename'])
                                service.revisions().delete(
                                    fileId=item['id'], revisionId=revId).execute()
                                arrayIndex -= 1
                            except errors.HttpError, error:
                                print('http error %s' %(error))
                        else:
                            if fixedFlag == 0:
                            #means we didn't find vvv, so we can use this revision
                            #now, rename the 'vvv' file to original name, which we can get from the current rev
                                try:
                                    #first, pull all file metadata
                                    objFile = service.files().get(fileId=item['id']).execute()
                                    #set the attributes we want to change
                                    objFile['title'] = revs['items'][arrayIndex]['originalFilename']
                                    objFile['modifiedDate'] = revs['items'][arrayIndex]['modifiedDate']
                                    print("renaming to %s" %(objFile['title']))
                                    #execute the change, note we need to set the 'setModifiedDate' flag
                                    updated_file = service.files().update(
                                        fileId=item['id'],
                                        body=objFile,
                                        modifiedDateBehavior='fromBody',
                                        setModifiedDate='true').execute()
                                    #since we were able to rename, set fixedFlag so this doesn't happen again
                                    fixedFlag = 1
                                    arrayIndex -= 1
                                    print("renaming done")
                                    break
                                    
                                except errors.HttpError, error:
                                    print('An error occurred: %s' % error)
                                    pass


            except KeyError:
                print ("key error..skip")
                print("file ID was; %s" %(item['id']))
            except UnicodeEncodeError:
                print ("unicode error, skip")
            #print (item['title'])

if returnedResults > 100:
    cleanup()
