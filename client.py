import requests
import json
import pprint as pp


class Client():

    def __init__(self, url, key):
        self.url = url
        self.api = url+'/api'
        self.key = key
        self.session = requests.Session()
        self.headers = {
            'Content-Type': 'application/json'
        }

    def get_resources(self):
        req = self.session.get(self.api + "/resources?key=" + self.key)
        req.raise_for_status()
        data = json.loads(req.text)
        return data

    def delete_resource(self, id: str):
        req = self.session.delete(
            self.api + "/v2/resources/{}?key={}".format(id, self.key))
        req.raise_for_status()
        return req.text

    def create_v2_cluster(self, name: str, description: str, tags: str, type: str):
        if type != 'pclusterv2' and type != 'gclusterv2' and type != 'azclusterv2':
            raise Exception("Invalid cluster type")
        url = self.api + "/v2/resources?key=" + self.key
        payload = {
            'name': name,
            'description': description,
            'tags': tags,
            'type': type,
            'params': {
                "jobsPerNode": ""
            }
        }

        req = self.session.post(url, data=(payload))
        req.raise_for_status()
        data = json.loads(req.text)
        return data

    def update_v2_cluster(self, id: str, cluster_definition):
        if id is None or id == "":
            raise Exception("Invalid cluster id")
        url = self.api + "/v2/resources/{}?key={}".format(id, self.key)
        req = self.session.put(url, json=cluster_definition)
        req.raise_for_status()
        data = json.loads(req.text)
        return data

    def start_resource(self, id: str):
        req = self.session.get(
            self.api + "/resources/start?key=" + self.key + "&id=" + id)
        req.raise_for_status()
        return req.text

    def stop_resource(self, id):
        req = self.session.get(
            self.api + "/resources/stop?key=" + self.key + "&id=" + id)
        req.raise_for_status()
        return req.text

    def update_resource(self, name, params):
        update = "&name={}".format(name)
        for key, value in params.items():
            update = "{}&{}={}".format(update, key, value)
        req = self.session.post(
            self.api + "/resources/set?key=" + self.key + update)
        req.raise_for_status()
        return req.text

    def get_identity(self):
        url = self.api + "/api/v2/auth/session?key=" + self.key
        req = self.session.get(url)
        req.raise_for_status()
        data = json.loads(req.text)
        return data
