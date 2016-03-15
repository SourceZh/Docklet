from flask import request

def external_auth_generate_request():

    token =  request.args.get('token','0')
    form = {}
    form['token'] = token
    form['ip'] = request.remote_addr
    return form

html_path = "user/iaaa_auth.html"

external_login_link = 'PKU User?'

external_login_url =  '/external_login/'

external_login_callback_url = '/pkulogin/'
