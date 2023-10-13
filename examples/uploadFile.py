#!/usr/bin/env python

import json 
import requests
import sys 
import time

from client import Client

# inputs
pw_url = "https://noaa.parallel.works"
api_key = "xxx" # your api key goes here 

jsonfile = "test_upload.json"

# create a new Parallel Works client
c = Client(pw_url,api_key)

# upload the input dataset from the desktop
print("")
print("Uploading JSON File...")
upload_dir = "/pw/storage"
upload = c.upload_dataset(jsonfile,upload_dir)
print(upload)
