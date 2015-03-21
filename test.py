import datetime

from flask import request, redirect, url_for, render_template, flash,jsonify
from flask import send_file

from flask_peewee.utils import get_object_or_404, object_list

from app import app
from models import *

#this will be add some png
@app.route('/png/<apikey>/<token>/')
def png(apikey , token):
    originurl = request.query_string

    args = request.args
    url = args.get('url')
    viewport = args.get('viewport')
    if (viewport == None or viewport == ''):
        viewport = "1480x1480"
    width = int(viewport.split('x')[0])
    thumbnail_max_width = args.get('thumbnail_max_width')
    if (thumbnail_max_width == None or thumbnail_max_width == '' or int(thumbnail_max_width) > width):
        thumbnail_max_width = str(width)
    fullpage = args.get('fullpage')
    if (fullpage == None or fullpage == ''):
        fullpage = "0"
    longurl = "url=" + url + "&viewport=" + viewport + "&thumbnail_max_width=" + thumbnail_max_width + "&fullpage=" + fullpage
    try:
        user = User.get(User.apikey == apikey)
    except User.DoesNotExist:
        user = None
    if (user is not None):
        if (auth(user, token, originurl)):
            try:
                obj = Png.get(Png.originurl == originurl)
            except Png.DoesNotExist:
                obj = None
            if (obj is None):
                if (user.weixin == '' and user.pcount >= 300):
                    return "please share link2img and get 1000 free record"
                elif (user.weixin == 'weiXinShareTimeLine' and user.pcount >= 1300):
                    return "please connect with us, you had been used 1300 records"
                else:
                    obj = Png.create(originurl=originurl)
                    obj.interurl = longurl
                    obj.fetch_png()
                    if (obj.png != ""):
                        obj.pcount = 1
                        obj.save()
                        user.pcount = user.pcount + 1
                        user.save()
                        return send_file(obj.png, mimetype='image/png')
                    else:
                        return "create img error"
            else:
                obj.pcount = obj.pcount + 1
                obj.save()
                return send_file(obj.png, mimetype='image/png')
        else:
            return "Unauthorized"
    else:
        return "Unauthorized"

#this will be add some json
@app.route('/json/<apikey>/<token>/')
def json(apikey, token, url):
    url = request.args.get('url')
    try:
        user = User.get(User.apikey == apikey)
    except User.DoesNotExist:
        user = None
    if (user is not None):
        if (auth(user, token, url)):
            try:
                obj = Json.get(Json.url == url)
            except Json.DoesNotExist:
                obj = None
            if (obj is None):
                obj = Json.create(url=url)
                obj.fetch_json()
                obj.jcount = 1
                obj.save()
                user.jcount = user.jcount + 1
                user.save()
                return obj.json
            else:
                obj.jcount = obj.jcount + 1
                obj.save()
                return obj.json
        else:
            return "Unauthorized"
    else:
        return "Unauthorized"

@app.route('/png/count/<apikey>')
def countp(apikey):
    try:
        user = User.get(User.apikey == apikey)
    except User.DoesNotExist:
        user = None
    if (user is not None):
        return "{'count': " + bytes(user.pcount) + "}"
    else:
        return "{'error': 'no user'}"

@app.route('/json/count/<apikey>')
def countj(apikey):
    try:
        user = User.get(User.apikey == apikey)
    except User.DoesNotExist:
        user = None
    if (user is not None):
        return "{'count': " + bytes(user.jcount) + "}"
    else:
        return "{'error': 'no user'}"
#
def auth(user, token, url):
    hashresult = hashlib.md5(user.password+url).hexdigest()
    print url, hashresult
    if (token == hashresult and user.disable == 0):
        return True
    return False
