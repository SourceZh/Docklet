import sys, os
sys.path.append("..")
from view.view import normalView
from authenticate.auth import is_authenticated
from dockletreq.dockletrequest import dockletRequest
from flask import redirect, request, render_template, session, make_response
from jupytercookie import cookie_tool

import hashlib
#from suds.client import Client

import sys, inspect
this_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))
src_folder = os.path.realpath(os.path.abspath(os.path.join(this_folder,"../..", "src")))
if src_folder not in sys.path:
    sys.path.insert(0, src_folder)

import env





def refreshInfo():
    result = dockletRequest.post('/login/', data)
    ok = result and result.get('success', None)
    session['username'] = request.form['username']
    session['nickname'] = result['data']['nickname']
    session['description'] = result['data']['description'][0:10]
    session['avatar'] = '/static/avatar/'+ result['data']['avatar']
    session['usergroup'] = result['data']['group']
    session['status'] = result['data']['status']
    session['token'] = result['data']['token']

class loginView(normalView):
    template_path = "login.html"

    @classmethod
    def get(self):
        if is_authenticated():
            #refreshInfo()
            return redirect(request.args.get('next',None) or '/dashboard/')
        if (env.getenv('EXTERNAL_LOGIN') == 'TRUE'):
            url =  env.getenv('EXTERNAL_LOGIN_URL')
            link = env.getenv('EXTERNAL_LOGIN_LINK')
        else:
            link = ''
            url = ''
        return render_template(self.template_path, link = link, url = url)

    @classmethod
    def post(self):
        if (request.form['username']):
            data = {"user": request.form['username'], "key": request.form['password']}
            result = dockletRequest.unauthorizedpost('/login/', data)
            ok = result and result.get('success', None)
            if (ok and (ok == "true")):
                # set cookie:docklet-jupyter-cookie for jupyter notebook
                resp = make_response(redirect(request.args.get('next',None) or '/dashboard/'))
                app_key = os.environ['APP_KEY']
                resp.set_cookie('docklet-jupyter-cookie', cookie_tool.generate_cookie(request.form['username'], app_key))
                # set session for docklet
                session['username'] = request.form['username']
                session['nickname'] = result['data']['nickname']
                session['description'] = result['data']['description'][0:10]
                session['avatar'] = '/static/avatar/'+ result['data']['avatar']
                session['usergroup'] = result['data']['group']
                session['status'] = result['data']['status']
                session['token'] = result['data']['token']
                return resp
            else:
                return redirect('/login/')
        else:
            self.error()

class logoutView(normalView):

    @classmethod
    def get(self):
        resp = make_response(redirect('/login/'))
        session.pop('username', None)
        session.pop('nickname', None)
        session.pop('description', None)
        session.pop('avatar', None)
        session.pop('status', None)
        session.pop('usergroup', None)
        session.pop('token', None)
        resp.set_cookie('docklet-jupyter-cookie', '', expires=0)
        return resp
