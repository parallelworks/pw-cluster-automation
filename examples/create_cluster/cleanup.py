
import os
import time
import sys
import requests
import json

# fmt: off
sys.path.append('../..')
from client import Client
# fmt: on

# inputs
pw_url = "https://beta.parallel.works"
api_key = os.environ['PW_API_KEY']

c = Client(pw_url, api_key)

resources = c.get_resources()

name = "testfromapi"

for resource in resources:
    if resource['name'] == name:
        print("Deleting resource: " + name)
        deleted = c.delete_resource(resource['id'])
        print(deleted)
        break
