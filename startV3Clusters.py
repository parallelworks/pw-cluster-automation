#!/usr/bin/env python3

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
my_clusters = c.get_v3_clusters()
for cluster_name in clusters_to_start:

    try:
        cluster_name = cluster_name.split('/')
        cluster_namespace = cluster_name[0]
        cluster_name = cluster_name[1]
    except IndexError:
        print("No namespace provided for", cluster_name[0]+".", "Default to current user", user)
        cluster_name = cluster_name[0]
        cluster_namespace = user

    print("\nChecking cluster status", cluster_name, "in namespace", cluster_namespace+"...")

    started = []

    # check if resource exists and is on
    # find cluster_name in my_clusters
    cluster = next(
        (item for item in my_clusters if item["name"] == cluster_name and item["namespace"] == cluster_namespace), None)
    if cluster:
        if cluster['status'] == "off":
            # if resource not on, start it
            print("Starting cluster", cluster['name']+"...")
            time.sleep(0.2)
            print(c.start_v3_cluster(cluster_namespace, cluster_name))
        else:
            print(cluster_name, "already running...")
            ip = cluster['controllerIp']
            entry = ' '.join([cluster['name'], ip])
            print(entry)
            cluster_hosts.append(entry)
            started.append(cluster['name'])
    else:
        print("No cluster found.")
        sys.exit(1)

print("\nWaiting for", len(clusters_to_start), "cluster(s) to start...")

laststate = {}
clusterRunning = []

while True:

    current_state = c.get_v3_clusters()

    for cluster in current_state:

        for cluster_name in clusters_to_start:
            try:
                cluster_name = cluster_name.split('/')
                cluster_namespace = cluster_name[0]
                cluster_name = cluster_name[1]
            except IndexError:
                cluster_name = cluster_name[0]
                cluster_namespace = user

            if cluster['name'] == cluster_name and cluster['namespace'] == cluster_namespace and cluster['status'] == 'on':
    
                if cluster['name'] not in started:
    
                    state = cluster['currentSessionStatus']
    
                    if cluster['name'] not in laststate:
                        print(cluster['name'], state)
                        laststate[cluster['name']] = state
    
                    elif laststate[cluster['name']] != state:
                        print(cluster['name'], state)
                        laststate[cluster['name']] = state
    
                    if state == "running":
                        started.append(cluster['name'])
                        print("Cluster", cluster['name'], "is now ready. Controller IP:", cluster['controllerIp']) 
                        ip = cluster['controllerIp'] 
                        entry = ' '.join([cluster['name'], ip])
                        cluster_hosts.append(entry)

    if len(started) == len(clusters_to_start):
        #print('\nStarted all clusters... writing hosts file')
        print('\nStarted all clusters!')
        break

    time.sleep(5)

### test host file updates ###
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
