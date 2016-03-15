import hashlib
from suds.client import Client
import requests

import xml.etree.cElementTree as ET

def external_auth_receive_request(form):
    url = "https://iaaa.pku.edu.cn/iaaaWS/TokenValidation?WSDL"
    remoteaddr = form.getvalue("ip")
    appid = "iwork"
    token = form.getvalue("token")
    key = "2CF3E3B1A57A13BFE0530100007FB96E"
    msg = remoteaddr + appid + token + key
    m = hashlib.md5()
    m.update(msg.encode("utf8"))
    msg = m.hexdigest()
    client = Client(url)
    result = dict(client.service.validate(remoteaddr, appid, token, msg))
    if (result['Status'] != 0):
        return {'success': 'False'}
    else:
        tree = ET.fromstring(result['Info'])
        username = tree[6].text
        truename = tree[1].text
        auth_result = {
            'success' : 'True',
            'username' : username,
            'password' : 'password',
            'avatar' : "default.png",
            'nickname' : truename,
            'description' : '',
            'status' : 'init',
            'e_mail': '',
            'student_number' : username,
            'department' : tree[11].text,
            'truename' : truename,
            'tel' : '',
            'user_group' : 'primary',
            'auth_method' : 'iaaa',
        }
        return auth_result
