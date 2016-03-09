import requests
import json
from flask import abort
from flask import session

endpoint = "http://0.0.0.0:9000"

class dockletRequest():

    @classmethod
    def post(self, url = '/', data = {}):
        #try:
        data = dict(data)
        data['token'] = session['token']
        print("Docklet Request: data = %s, url = %s"%(data, url))
        result = requests.post(endpoint + url, data = data).json()
        if (result.get('success', None) == "false" and result.get('reason', None) == "Unauthorized Action"):
            abort(401)
        print(result)
        return result
        #except:
            #abort(500)

    @classmethod
    def unauthorizedpost(self, url = '/', data = None):
        data = dict(data)
        print("Docklet Request: data = %s, url = %s" % (data, url))
        result = requests.post(endpoint + url, data = data).json()
        print(result)
        return result
