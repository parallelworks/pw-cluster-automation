#!/usr/bin/env python3

"""
  This script will automatically connect to the ParallelWorks gateway to retrieve
  information about storage resources using the user's API key.

  It will then generate short-term credentials for the buckets provided

  Critical files that must exist:

    $HOME/.ssh/pw_api.key - this file must contain the API key in the first and only
                            line.  Treat this file as any secure file and place in
                            .ssh directory.  Change permissions to mode 600.
"""

import subprocess
import json
import requests
import sys
import time
import os
from client import Client
import re

def is_mongo_id(string):
    pattern = re.compile(r'^[0-9a-fA-F]{24}$')
    return bool(pattern.match(string))

# inputs
PW_PLATFORM_HOST = None
if 'PW_PLATFORM_HOST' in os.environ:
    PW_PLATFORM_HOST = os.environ['PW_PLATFORM_HOST']
else:
    print("No PW_PLATFORM_HOST environment variable found. Please set it to the Parallel Works platform host name. e.g. cloud.parallel.works")
    sys.exit(1)

pw_url = "https://" + PW_PLATFORM_HOST

# specify the clusters to start and wait for activation
buckets_to_access = sys.argv[1].split(',')

print('\nGenerating credentials for buckets:', buckets_to_access)

# Get user specific files
homedir = os.environ['HOME']
# The .hosts file will get re-written every time
keyfile = homedir + '/.ssh/pw_api.key'

# get my personal API key
# with the environment variable PW_API_KEY taking precedence
# over the file $HOME/.ssh/pw_api.key
api_key = None
if 'PW_API_KEY' in os.environ:
    api_key = os.environ['PW_API_KEY']
else:
    try:
        f = open(keyfile, "r")
        api_key = f.readline().strip()
        f.close()
    except:
        pass

if api_key is None or api_key == "":
    print("No API key found. Please set the environment variable PW_API_KEY or create the file $HOME/.ssh/pw_api.key.")
    sys.exit(1)

# create a new Parallel Works client
c = Client(pw_url, api_key)

# get the account username
session = c.get_identity()

user = session['username']
print("\nRunning as user", user+'...')
my_buckets = c.get_storages()
for bucket_name in buckets_to_access:

    try:
        bucket_name = bucket_name.split('/')
        bucket_namespace = bucket_name[0]
        bucket_name = bucket_name[1]
    except IndexError:
        print("No namespace provided for", bucket_name[0]+".", "Default to current user", user)
        bucket_name = bucket_name[0]
        bucket_namespace = user

    print("\nLooking for bucket", bucket_name, "in namespace", bucket_namespace+"...")

    # check if resource exists
    # find bucket_name in my_storages and map to ID
    # this logic currently only lets you get creds for buckets you own
    
    # check if bucket_name is mongo id or name of the bucket
    if is_mongo_id(bucket_name):
        bucket = next(
            (item for item in my_buckets if item["id"] == bucket_name and item["namespace"] == bucket_namespace), None)
    else:
        bucket = next(
            (item for item in my_buckets if item["name"] == bucket_name and item["namespace"] == bucket_namespace), None)
    if "bucket" not in bucket['type']:
        print("Storage provided is not a bucket.")
    elif bucket['provisioned'] != True:
        print("Bucket provided is not currently provisioned.")
    elif bucket:
        print("Identified bucket", bucket['name'], "as", bucket['id'])

        # generate short-term bucket credentials
        print(c.get_bucket_cred(bucket['id']))
    else:
        print("No bucket found.")
