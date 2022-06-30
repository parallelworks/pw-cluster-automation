import os
import time
import sys
import requests
import json

sys.path.append('../..')
from client import Client


# inputs
pw_url = "https://canary.parallel.works"
api_key = os.environ['PW_API_KEY']

c = Client(pw_url, api_key)

cluster = c.create_v2_cluster(
"testfromapi1", "testtest", "tag1,tag2", "pclusterv2")
cluster_id = cluster['_id']

with open('resource.json') as cluster_defintion:
    data = json.load(cluster_defintion)
    try:
        updated_cluster = c.update_v2_cluster(cluster_id, data)
        print(updated_cluster)
    except requests.exceptions.HTTPError as e:
        print(e.response.text)
   
