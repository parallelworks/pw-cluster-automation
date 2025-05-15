import argparse
import os
import time
import sys
import requests
import json
import base64
import getopt

from client import Client

# inputs
PW_PLATFORM_HOST = None
if 'PW_PLATFORM_HOST' in os.environ:
    PW_PLATFORM_HOST = os.environ['PW_PLATFORM_HOST']
else:
    print("No PW_PLATFORM_HOST environment variable found. Please set it to the Parallel Works platform host name. e.g. cloud.parallel.works")
    sys.exit(1)

pw_url = "https://" + PW_PLATFORM_HOST

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

# script args
parser = argparse.ArgumentParser()
parser.add_argument("--csp", type=str, help="CSP to create the cluster definition")
parser.add_argument("--name", type=str, help="name of the cluster")
parser.add_argument("--definition", type=str, help="JSON file to create the config from")

args = parser.parse_args()

# validate arguments
csp = args.csp
clusterDef = args.definition
clusterName = args.name
clusterDisplayName = clusterName 

while csp not in ["aws", "azure", "google"] :
  print("--csp invalid or not provided. Must be one of 'aws', 'azure', or 'google'.")
  sys.exit(1)
if clusterDef is None:
  print("--definition not provided. Must provide a valid JSON formatted cluster definition.")
  sys.exit(1)
elif clusterName is None:
  print("--name not provided. Must provide a valid JSON formatted cluster definition.")
  sys.exit(1)

# make sure you can read the file and extract a name
try:
  with open(clusterDef, 'r') as file:
    clusterJSON = json.load(file)
    print("Creating", csp, "cluster", clusterName)
except Exception as e:
  print(e)

# make sure cluster name or display name is not in use 
my_clusters = c.get_v3_clusters()

cluster = next(
  (item for item in my_clusters if item["name"] == clusterName or item["displayName"] == clusterName), None)
if cluster:
  print("cluster", clusterName, "already exists.")
  sys.exit(1)

# create a dict for initial cluster creation
clusterData = {
  "name": clusterName, 
  "displayName": clusterName,
  "tags": "",
  "description": "",
  "type": csp+"-slurm",
  "runTimeAlert": {
    "enabled": False
  }
}

cluster = c.create_v3_cluster(clusterData)

# Update the cluster definition to include configuration JSON.
clusterData["baseInfrastructure"] = ""
clusterData["group"] = ""
clusterData["variables"] = clusterJSON
clusterData["attachedStorages"] = clusterJSON["attachedStorages"]
clusterData["variables"]["attachedStorages"]
 
cluster = c.update_v3_cluster(clusterData, user, clusterName)
