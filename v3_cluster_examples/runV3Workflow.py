#!/usr/bin/env python3

"""
  This script will start a workflow on a given cluster if the workflow allows running on a cluster.

  Critical files that must exist:

    $HOME/.ssh/pw_api.key - this file must contain the API key in the first and only
                            line.  Treat this file as any secure file and place in
                            .ssh directory.  Change permissions to mode 600.
"""

import argparse
import subprocess
import json
import requests
import sys
import time
import os
from client import Client

# inputs

# Check required arguments
# try using argparse for this
  # workflow_name
  # workflow_input
  # service_host (cluster_name)
parser = argparse.ArgumentParser()
parser.add_argument("--workflowName", type=str, help="Workflow name")
parser.add_argument("--workflowInput", type=str, help="Workflow parameters input file")
parser.add_argument("--serviceHost", type=str, help="Target cluster to execute workflow")

args = parser.parse_args()

# Confirm PW_PLATFORM_HOST
PW_PLATFORM_HOST = None
if 'PW_PLATFORM_HOST' in os.environ:
    PW_PLATFORM_HOST = os.environ['PW_PLATFORM_HOST']
else:
    print("No PW_PLATFORM_HOST environment variable found. Please set it to the Parallel Works platform host name. e.g. cloud.parallel.works")
    sys.exit(1)

pw_url = "https://" + PW_PLATFORM_HOST

# AUTHENTICATION
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

# CREATE SESSION
c = Client(pw_url, api_key)
session = c.get_identity()
user = session['username']
print("\nRunning as user", user+'...')

# validate arguments
try:
  workflow_name = args.workflowName
  print("\nExecuting workflow", workflow_name+'...')
except (NameError, TypeError):
  print("No workflow provided for execution.")
  sys.exit(1)

try:
  workflow_input = args.workflowInput
  print("\nExecuting workflow from input file", workflow_input+'...')
except (NameError, TypeError):
  print("No workflow input provided.")
  print("This script currently requires providing an input template to execute.")
  sys.exit(1)

try:
  service_host = args.serviceHost
  service_host = service_host.split('/')
  service_host_namespace = service_host[0]
  service_host = service_host[1]
except IndexError:
    service_host = service_host[0]
    service_host_namespace = user  
except (AttributeError, NameError, TypeError):
  print("No valid service host provided.")
  print("Attempting to read service host from input form...")
  try:
    with open(workflow_input, 'r') as file:
      data = json.load(file)
      resource_data = data['pwrl_host']['resource']
      service_host = resource_data['name']
      service_host_namespace = resource_data['namespace']
      if len(service_host_namespace) == 0:
        service_host_namespace = user  
  except (NameError, TypeError): 
    print("Error: Service host could not be determined from input file")
    sys.exit(1)
  except (FileNotFoundError):
    print("Error: Workflow input file could not be read")
    sys.exit(1)

print("\nExecuting workflow on service host:", service_host)
print("in namespace:", service_host_namespace+'...')

# check that cluster can be found and is turned on
# if the cluster is running, render the workflow json input to execute
try:
  cluster = c.get_v3_cluster(service_host_namespace,service_host)
  print("Checking status of cluster", service_host)
except (requests.exceptions.HTTPError):
  print("Cluster", service_host, "not found", "in namespace", service_host_namespace)
  sys.exit(1)

if cluster['currentSessionStatus'] == "running":
  print("Cluster", service_host_namespace+"/"+service_host, "is running,")
  print("Collecting necessary variables to launch workflow...")
  try:
    resourceData = {
      "type": "computeResource", 
      "id": cluster['id'],
      "provider": cluster['type'],
      "ip": cluster['controllerIp'],
      "namespace": cluster['namespace'],
      "name": cluster['name']
    }
  except:
    print("There was an error collecting resource data. Exit")
    sys.exit(1)

  try:
    with open(workflow_input, 'r') as file:
      workflowData = json.load(file)
      workflowData['pwrl_host']['resource'] = resourceData
  except Exception as e:
    print(e)

elif cluster['status'] == "off":
  print("Cluster", service_host_namespace+"/"+service_host, "is currently off.")
  print("Please turn the cluster on before submitting a workflow.")
  sys.exit(1)
elif cluster['currentSessionStatus'] == "provisioning":
  print("Cluster", service_host_namespace+"/"+service_host, "is currently provisioning.")
  print("Please try again after the cluster is active.")
  sys.exit(1)
else:
  print("Unable to determine cluster status. Exit")
  sys.exit(1)

# submit the workflow
print("Executing workflow with input JSON:")
print(workflowData)

try:
  response = c.run_workflow(workflow_name, workflowData)
  print(response['message'])
except Exception as e:
  print(e)
