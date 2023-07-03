#!/usr/bin/env python3

"""
  This script will start a workflow on a given cluster if the workflow allows running on a cluster.

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

# inputs
PW_PLATFORM_HOST = None
if 'PW_PLATFORM_HOST' in os.environ:
    PW_PLATFORM_HOST = os.environ['PW_PLATFORM_HOST']
else:
    print("No PW_PLATFORM_HOST environment variable found. Please set it to the Parallel Works platform host name. e.g. cloud.parallel.works")
    sys.exit(1)

pw_url = "https://" + PW_PLATFORM_HOST

workflow_name = sys.argv[1]
cluster_to_run_in = None
if len(sys.argv) > 2:
    cluster_to_run_in = sys.argv[2]

# check if arguments were passed, cluster_to_run_in is optional
if len(sys.argv) < 2:
    print("Usage: runWorkflow.py <workflow_name> <cluster_to_run_in>")
    print("Optional argument <cluster_to_run_in> is the name of the cluster to run the workflow in. If not specified, the workflow will run on the user workspace.")
    sys.exit(1)

api_key = None
if 'PW_API_KEY' in os.environ:
    api_key = os.environ['PW_API_KEY']
else:
    try:
        homedir = os.environ['HOME']
        keyfile = homedir + '/.ssh/pw_api.key'
        f = open(keyfile, "r")
        api_key = f.readline().strip()
        f.close()
    except:
        pass

if api_key is None or api_key == "":
    print("No API key found. Please set the environment variable PW_API_KEY or create the file $HOME/.ssh/pw_api.key.")
    sys.exit(1)

c = Client(pw_url, api_key)


print("Starting workflow " + workflow_name)

resource_id = 'user_workspace'
if cluster_to_run_in != None:
    resources = c.get_resource(cluster_to_run_in)
    if len(resources) == 0:
        print("No resources found with name " + cluster_to_run_in)
        sys.exit(1)
    if resources[0]["status"] != "on":
        print("Resource " + cluster_to_run_in + " is currently not on")
        sys.exit(1)
    print(resources)
    resource_id = resources[0]["id"]
    print("Running workflow in cluster " + cluster_to_run_in)
else: 
    print("Running workflow in user workspace")



# WORKFLOW INPUTS GO HERE
inputs = {
    "input1": "value1",

    # Location of the main script to run
    "startCmd" : "main.sh",

    # Define which resource to run (should not be changed)
    "resource_label": {
        "id" : resource_id,
        "type": "computeResource"
    }
}

response = c.run_workflow(workflow_name, inputs)

print(response["message"])