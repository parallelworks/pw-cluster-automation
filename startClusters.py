#!/usr/bin/env python3

"""
  This script will automatically connect to the NOAA ParallelWorks gateway to retrieve
  information about the current clusters using the user's API key.

  Critical files that must exist:

    $HOME/.ssh/pw_api.key - this file must contain the API key in the first and only
                            line.  Treat this file as any secure file and place in
                            .ssh directory.  Change permissions to mode 600.

  New files created:
    $HOME/.hosts - this is a new file created every time the script is run.
                   Do not modify this file externally as any change will be
                   lost.  If no active clusters exists, the file will be created
                   with one commented line.  For the hosts to be recognized,
                   the HOSTALIASES environment variable must point to this
                   file (i.e. export HOSTALIASES=$HOME/.hosts).
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

# specify the clusters to start and wait for activation
#clusters = ["gcluster_noaa"]
clusters_to_start = sys.argv[1].split(',')

print('\nStarting clusters:', clusters_to_start)

# used to run test ssh commands after the clusters start
# ensure your public key is added to the cluster configuration on Parallel Works

# Get user specific files
homedir = os.environ['HOME']
# The .hosts file will get re-written every time
hostsfile = homedir + '/.hosts'
keyfile = homedir + '/.ssh/pw_api.key'

# Prepare a header to go into the user's .hosts file
cluster_hosts = [f'# Generated Automatically ' + os.path.basename(__file__)]

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
for cluster_name in clusters_to_start:

    print("\nChecking cluster status", cluster_name+"...")

    # check if resource exists and is on
    # find cluster_name in my_clusters
    cluster = next(
        (item for item in my_clusters if item["name"] == cluster_name), None)
    if cluster:
        if cluster['status'] == "off":
            # if resource not on, start it
            print("Starting cluster", cluster['name']+"...")
            time.sleep(0.2)
            print(c.start_resource(cluster['id']))
        else:
            print(cluster_name, "already running...")
    else:
        print("No cluster found.")
        sys.exit(1)

print("\nWaiting for", len(clusters_to_start), "cluster(s) to start...")

laststate = {}
started = []

while True:

    current_state = c.get_resources()

    for cluster in current_state:

        # print(cluster['name'],cluster['status'])

        if cluster['name'] in clusters_to_start and cluster['status'] == 'on':

            if cluster['name'] not in started:

                state = cluster['state']

                if cluster['name'] not in laststate:
                    print(cluster['name'], state)
                    laststate[cluster['name']] = state

                elif laststate[cluster['name']] != state:
                    print(cluster['name'], state)
                    laststate[cluster['name']] = state

                # if state == 'ok':
                #     break
                # elif (state == 'deleted' or state == 'error'):
                #     raise Exception('Simulation had an error. Please try again')

                if 'masterNode' in cluster['state']:
                    if cluster['state']['masterNode'] != None:
                        ip = cluster['state']['masterNode']
                        entry = ' '.join([cluster['name'], ip])
                        print(entry)
                        cluster_hosts.append(entry)
                        started.append(cluster['name'])

    if len(started) == len(clusters_to_start):
        print('\nStarted all clusters... writing hosts file')
        break

    time.sleep(5)

# Generate the user's local .hosts file
with open(hostsfile, 'w+') as f:
    f.writelines("%s\n" % l for l in cluster_hosts)
    print('SUCCESS - the', hostsfile, 'was updated.')
    f.close()

# run example ssh command on each started cluster

print("\nRunning test ssh commands on the clusters...")

testcmd = "sinfo"

for ei, entry in enumerate(cluster_hosts):

    if ei > 0:  # skip the host header

        name = entry.split()[0]
        ip = entry.split()[1]

        cmd = "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null %s@%s %s" % (
            user, ip, testcmd)

        print("")
        print(name+':', '"'+cmd+'"')

        out = subprocess.check_output(
            cmd,
            stderr=subprocess.STDOUT,
            shell=True).decode(sys.stdout.encoding)

        print(out)
