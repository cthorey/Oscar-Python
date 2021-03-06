import json
import urllib
from urllib.parse import urlencode
from urllib.request import Request
from urllib.request import urlopen

__all__ = ['Oscar', 'ClientException']


class ClientException(Exception):
    pass


class Oscar:
    API_VERSION = '1'
    #DOMAIN_URL = 'http://localhost:8080'
    DOMAIN_URL = 'https://' + API_VERSION + '-dot-sensout-oscar.appspot.com'

    def __init__(self, access_token):
        self.access_token = access_token
        self.trial_ids = {}
        self.trial_keys = {}

    def call(self, url, params):
        # prepare request
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json',
                   'Authorization': 'Bearer ' + self.access_token}
        url = url + '?' + urlencode(params)
        req = Request(self.DOMAIN_URL + url, None, headers)
        try:
            resp = urlopen(req)
            content = resp.read().decode('utf-8')
            result = json.loads(content)
            if result:
                if 'redirect' in result:
                    raise ClientException(
                        "Your are not authenticated. You should try updating your access token.")
                else:
                    return result
            else:
                raise ClientException(
                    "Did not manage to parse API response: " + content)
        except Exception as e:
            print("Error when calling API:")
            raise e

    def get_job_hash(self, job):
        return str(hash(json.dumps(job)))

    def get_job_id(self, job):
        return self.trial_ids[self.get_job_hash(job)]

    def suggest(self, experiment):
        result = self.call('/suggest', {
                           'experiment': json.dumps(experiment)
                           })
        # result is non nil or error has been raised
        if 'job' in result and 'trial_key' in result and 'trial_id' in result:
            hash = self.get_job_hash(result['job'])
            self.trial_ids[hash] = result['trial_id']
            self.trial_keys[hash] = result['trial_key']
            return result['job']
        else:
            raise ClientException(
                "No job returned. Check your parameters and quotas " + json.dumps(result))

    def update(self, job, result):
        return self.call('/update', {
                         'trial_key': self.trial_keys[self.get_job_hash(job)],
                         'result': json.dumps(result)
                         })
