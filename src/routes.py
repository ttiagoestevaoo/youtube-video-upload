from fastapi import APIRouter, UploadFile,Form, File
from src.core.models import VideoUpload

router = APIRouter(
    prefix="/videos", tags=["Videos"]
)

import datetime
import shutil

#!/usr/bin/python

import httplib2
import os
import random
import sys
import time

from apiclient import discovery, http, errors
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
import google.oauth2.credentials


# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the Google API Console at
# https://console.cloud.google.com/.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "client_secrets.json"

# This OAuth 2.0 access scope allows an application to upload files to the
# authenticated user's YouTube channel, but doesn't allow other types of access.
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the API Console
https://console.cloud.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")


def get_authenticated_service(accessToken):
  credentials = google.oauth2.credentials.Credentials(accessToken)

  return discovery.build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    credentials=credentials)


def resumable_upload(insert_request):
  response = None
  error = None
  retry = 0
  while response is None:
    try:
      print ("Uploading file...")
      status, response = insert_request.next_chunk()
      if response is not None:
        if 'id' in response:
          return "Video enviado"
        else:
          raise Exception("Não foi possível enviar o vídeo")
    except errors.HttpError as e:
      if e.resp.status in RETRIABLE_STATUS_CODES:
        error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
                                                             e.content)
      else:
        raise
    except RETRIABLE_EXCEPTIONS as e:
      error = "A retriable error occurred: %s" % e

    if error is not None:
      print (error)
      retry += 1
      if retry > MAX_RETRIES:
        exit("No longer attempting to retry.")

      max_sleep = 2 ** retry
      sleep_seconds = random.random() * max_sleep
      print ("Sleeping %f seconds and then retrying...") % sleep_seconds
      time.sleep(sleep_seconds)



@router.post("/", status_code=201, response_model=VideoUpload)
async def upload_video(
  access_token: str,
  media: UploadFile,
  title: str = Form(), 
  description: str = Form(),
):
  youtube = get_authenticated_service(access_token)

  file_location = f"./src/tmp-files/{datetime.datetime.now().isoformat()}"
  with open(file_location, "wb+") as file_object:
    shutil.copyfileobj(media.file, file_object)   
  
  body=dict(
    snippet=dict(
      title=title,
      description=description,
    ),
  )

  insert_request = youtube.videos().insert(
    part=",".join(body.keys()),
    body=body,
    media_body=http.MediaFileUpload(file_location, chunksize=-1, resumable=True)
  )
  os.remove(file_location)
  resumable_upload(insert_request)

