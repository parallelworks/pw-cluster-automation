#!/usr/bin/env python3

"""
  This script will automatically connect to the NOAA ParallelWorks gateway to retrieve
  information about the current clusters using the user's API key.

  Critical files that must exist:

    $HOME/.ssh/pw_api.key - this file must contain the API key in the first and only
                            line.  Treat this file as any secure file and place in
                            .ssh directory.  Change permissions to mode 600.
"""

import json
import requests
import sys
import time
import os
from client import Client

# inputs
PW_PLATFORM_HOST = None
if 'PW_PLATFORM_HOST' in os.environ:
    PW_PLATFORM_HOST = os.environ['PW_PLATFORM_HOST']
else:
    print("No PW_PLATFORM_HOST environment variable found. Please set it to the Parallel Works platform host name. e.g. cloud.parallel.works")
    sys.exit(1)

pw_url = "https://" + PW_PLATFORM_HOST
# specify the clusters to start and wait for activation
#clusters = ["gcluster_noaa"]
clusters_to_stop = sys.argv[1].split(',')

# used to run test ssh commands after the clusters start
# ensure your public key is added to the cluster configuration on Parallel Works

# Get user specific files
homedir = os.environ['HOME']
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
my_clusters = c.get_resources()

for cluster_name in clusters_to_stop:

    print("\nChecking cluster status", cluster_name+"...")

    # check if resource exists and is on
    cluster = next(
        (item for item in my_clusters if item["name"] == cluster_name), None)
    if cluster:
        if cluster['status'] == "on":
            # if resource not on, start it
            print("Stopping cluster", cluster['name']+"...")
            print(c.stop_resource(cluster['id']))
        else:
            print(cluster_name, "already stopped...")
    else:
        print("No cluster found.")
        sys.exit(1)

print("\nStopped", len(clusters_to_stop), "clusters...\n")
