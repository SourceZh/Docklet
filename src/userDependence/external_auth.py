import sys
sys.path.append("..")
from model import db, User
import hashlib
from suds.client import Client
import requests
from userManager import userManager

G_usermgr = userManager()

def auth_external(form):

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
        failed_result =  {'success':'false',  'result': result}
        return failed_result

    import xml.etree.cElementTree as ET
    tree = ET.fromstring(result['Info'])
    username = tree[6].text
    user = User.query.filter_by(username = username).first()
    if (user != None and user.auth_method == 'iaaa'):
        result = {
            "success": 'true',
            "data":{
                "username" : user.username,
                "avatar" : user.avatar,
                "nickname" : user.nickname,
                "description" : user.description,
                "status" : user.status,
                "group" : user.user_group,
                "token" : user.generate_auth_token(),
            }
        }
        return result
    if (user != None and user.auth_method != 'iaaa'):
        result = {'success': 'false', 'reason': 'other kinds of account already exists'}
        return result
    #user == None , register an account for PKU user
    truename = tree[1].text
    department = tree[11].text
    newuser = G_usermgr.newuser();
    newuser.username = username
    newuser.password = "no_password"
    newuser.nickname = truename
    newuser.truename = truename
    newuser.student_number = username
    newuser.status = "init"
    newuser.user_group = "primary"
    newuser.auth_method = "iaaa"
    newuser.department = department
    G_usermgr.register(user = newuser)
    user = User.query.filter_by(username = username).first()
    result = {
        "success": 'true',
        "data":{
            "username" : user.username,
            "avatar" : user.avatar,
            "nickname" : user.nickname,
            "description" : user.description,
            "status" : user.status,
            "group" : user.user_group,
            "token" : user.generate_auth_token(),
        }
    }
    return result
