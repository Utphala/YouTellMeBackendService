from flask import Flask, request, jsonify, redirect, url_for, session
from flask.templating import render_template
from flask_oauth import OAuth
import MySQLdb
import json
# ClintID: 37779483905-mbehq3u75fg4ldo9jb3t9pg5t1ck83c2.apps.googleusercontent.com
# Secret: DOf9Z2tv3mMkBvOOTyeroC-F

GOOGLE_CLIENT_ID = '37779483905-mbehq3u75fg4ldo9jb3t9pg5t1ck83c2.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = 'DOf9Z2tv3mMkBvOOTyeroC-F'
REDIRECT_URI = '/list_surveys'

app = Flask(__name__, template_folder='templates')

SECRET_KEY = 'development key'
DEBUG = True
 
app = Flask(__name__)
app.debug = DEBUG
app.secret_key = SECRET_KEY
oauth = OAuth()
 
google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          request_token_url=None,
                          request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email',
                                                'response_type': 'code'},
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          access_token_method='POST',
                          access_token_params={'grant_type': 'authorization_code'},
                          consumer_key=GOOGLE_CLIENT_ID,
                          consumer_secret=GOOGLE_CLIENT_SECRET)
 
@app.route('/')
def index():
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login'))
 
    access_token = access_token[0]
    from urllib2 import Request, urlopen, URLError
 
    headers = {'Authorization': 'OAuth '+access_token}
    req = Request('https://www.googleapis.com/oauth2/v1/userinfo',
                  None, headers)
    try:
        res = urlopen(req)
    except URLError, e:
        if e.code == 401:
            # Unauthorized - bad token
            session.pop('access_token', None)
            return redirect(url_for('login'))
        return res.read()
    #print res['email']
    return json.dumps(res)
 
 
@app.route('/login')
def login():
    callback=url_for('authorized', _external=True)
    return google.authorize(callback=callback)
 
 
 
@app.route(REDIRECT_URI)
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    return redirect(url_for('index'))
 
 
@google.tokengetter
def get_access_token():
    return session.get('access_token')


@app.route("/list_surveys",methods=['GET','POST'])
def list_surveys():
    query_to_excute = "SELECT content FROM youTellMeDB.surveys";
    conn=MySQLdb.connect('127.0.0.1','root','root','youTellMeDB')
    pointer= conn.cursor()
    pointer.execute(query_to_excute);
    surveys = pointer.fetchall()
    print surveys
    pointer.close()
    conn.close()
    return jsonify(surveys)

@app.route("/get_survey", methods=["POST"])
def get_survey():
    json_dict = request.get_json()
    title = json_dict['Title']
    data = {"Title": title}
    return jsonify(data)

@app.route("/submit", methods=["POST"])
def submit():
    return


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8081)