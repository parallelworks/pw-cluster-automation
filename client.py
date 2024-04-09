import requests
import json
import pprint as pp
import base64


class Client():

    def __init__(self, url, key):
        self.url = url
        self.api = url+'/api'
        self.key = key
        self.session = requests.Session()
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + base64.b64encode(bytes(self.key, 'utf-8')).decode('utf-8')
        }

    def get_resources(self):
        req = self.session.get(self.api + "/resources", headers = self.headers)
        req.raise_for_status()
        data = json.loads(req.text)
        return data

    def get_resource(self, name):
        req = self.session.get(self.api + "/resources", headers = self.headers)
        req.raise_for_status()
        data = json.loads(req.text)
        
        resource = [x for x in data if x['name'].lower() == name.lower()]

        return resource

    def delete_resource(self, id: str):
        req = self.session.delete(
            self.api + "/v2/resources/{}".format(id),
            headers = self.headers
        )
        req.raise_for_status()
        return req.text

    def create_v2_cluster(self, name: str, description: str, tags: str, type: str):
        if type != 'pclusterv2' and type != 'gclusterv2' and type != 'azclusterv2':
            raise Exception("Invalid cluster type")
        url = self.api + "/v2/resources"
        payload = {
            'name': name,
            'description': description,
            'tags': tags,
            'type': type,
            'params': {
                "jobsPerNode": ""
            }
        }

        req = self.session.post(url, data=(payload), headers = self.headers)
        req.raise_for_status()
        data = json.loads(req.text)
        return data

    def update_v2_cluster(self, id: str, cluster_definition):
        if id is None or id == "":
            raise Exception("Invalid cluster id")
        url = self.api + "/v2/resources/{}".format(id)
        req = self.session.put(url, json = cluster_definition, headers = self.headers)
        req.raise_for_status()
        data = json.loads(req.text)
        return data

    def start_resource(self, id: str):
        req = self.session.get(
            self.api + "/resources/start",
            params = {'id': id},
            headers = self.headers
        )
        req.raise_for_status()
        return req.text

    def stop_resource(self, id):
        req = self.session.get(
            self.api + "/resources/stop",
            params = {'id': id},
            headers = self.headers   
        )
        req.raise_for_status()
        return req.text

    def update_resource(self, name, params):
        # FIXME: Update headers
        update = "&name={}".format(name)
        for key, value in params.items():
            update = "{}&{}={}".format(update, key, value)
        req = self.session.post(
            self.api + "/resources/set?key=" + self.key + update)
        req.raise_for_status()
        return req.text

    def get_identity(self):
        url = self.api + "/v2/auth/session"
        req = self.session.get(url, headers = self.headers)
        req.raise_for_status()
        data = json.loads(req.text)
        return data
        
    def run_workflow(self, name, inputs):
        url = self.api + "/v2/workflows/" + name + "/start"
        payload = {
            'variables': inputs
        }
        req = self.session.post(url, json=payload,  headers = self.headers)
        req.raise_for_status()
        data = json.loads(req.text)
        return data

    def get_latest_job_status(self, workflow_name):
        url = self.api + "/v2/workflows/" + workflow_name + "/getJob"
        req = self.session.get(url, headers = self.headers)
        req.raise_for_status()
        data = json.loads(req.text)
        return data

    def get_storages(self):
        req = self.session.get(self.api + "/v2/storage",  headers = self.headers)
        #req = self.session.get(self.api + "/v2/storage?key={}&namespace={}".format(self.key, namespace))
        req.raise_for_status()
        data = json.loads(req.text)
        return data

    #def start_storage(self, id: str):
    #    req = self.session.post(
    #        self.api + "/v2/storage/{}/provision?key={}".format(id, self.key))
    #    req.raise_for_status()
    #    return req.text

    #def stop_storage(self, id):
    #    req = self.session.delete(
    #        self.api + "/resources/stop?key=" + self.key + "&id=" + id)
    #    req.raise_for_status()
    #    return req.text

    def get_bucket_cred(self, id: str):
        url = self.api + "/v2/vault/getBucketToken"
        payload = {
            'bucketID': id
        }
        req = self.session.post(url, json=payload, headers = self.headers)
        req.raise_for_status()
        data = json.loads(req.text)
        return data 
