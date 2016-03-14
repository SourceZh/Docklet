import sys, os
sys.path.append("..")
from view.view import normalView
from authenticate.auth import is_authenticated
from dockletreq.dockletrequest import dockletRequest
from flask import redirect, request, render_template, session, make_response
from jupytercookie import cookie_tool

class external_login_callbackView(normalView):
    @classmethod
    def get(self):

        token =  request.args.get('token','0')
        form = {}
        form['token'] = token
        form['ip'] = request.remote_addr
        result = dockletRequest.unauthorizedpost('/external_login/', form)
        ok = result and result.get('success', None)
        if (ok and (ok == "true")):
            # set cookie:docklet-jupyter-cookie for jupyter notebook
            resp = make_response(redirect(request.args.get('next',None) or '/dashboard/'))
            app_key = os.environ['APP_KEY']
            resp.set_cookie('docklet-jupyter-cookie', cookie_tool.generate_cookie(result['data']['username'], app_key))
            # set session for docklet
            session['username'] = result['data']['username']
            session['nickname'] = result['data']['nickname']
            session['description'] = result['data']['description'][0:10]
            session['avatar'] = '/static/avatar/'+ result['data']['avatar']
            session['usergroup'] = result['data']['group']
            session['status'] = result['data']['status']
            session['token'] = result['data']['token']
            return resp
        else:
            return redirect('/login/')

class external_loginView(normalView):
    template_path = "user/iaaa_auth.html"
