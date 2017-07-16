from flask import Flask, request, jsonify, redirect, url_for, session, Response
from flask.templating import render_template
from flask_oauth import OAuth
import MySQLdb
import json
# ClintID: 37779483905-mbehq3u75fg4ldo9jb3t9pg5t1ck83c2.apps.googleusercontent.com
# Secret: DOf9Z2tv3mMkBvOOTyeroC-F

GOOGLE_CLIENT_ID = '37779483905-mbehq3u75fg4ldo9jb3t9pg5t1ck83c2.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = 'DOf9Z2tv3mMkBvOOTyeroC-F'
REDIRECT_URI = '/authorize'

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

@app.route("/")
def index():
    return "Hello World!"

@app.route('/disabled')
def disabledIndex():
    # access_token = session.get('access_token')
    # if access_token is None:
    #     return redirect(url_for('login'))
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
    # Save user data
    data = json.load(res)
    loadUser(data)
    return res.read()


@app.route('/login')
def login():
    callback=url_for('authorized', _external=True)
    return google.authorize(callback=callback)



@app.route(REDIRECT_URI)
# @google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    return redirect(url_for('list_surveys'))


# @google.tokengetter
def get_access_token():
    return session.get('access_token')

def loadUser(data):
    conn=MySQLdb.connect('127.0.0.1','root','root','youTellMeDB')
    cursor= conn.cursor()
    cursor.execute("INSERT IGNORE INTO youTellMeDB.Users (id, role, name) VALUES (%s, %s, %s)", (data['email'], 'user', data['name']));
    conn.commit()
    cursor.close()
    conn.close()

@app.route("/list_surveys",methods=['GET','POST'])
# @google.authorized_handler
def list_surveys(resp):
    query_to_excute = "SELECT content FROM youTellMeDB.surveys";
    conn=MySQLdb.connect('127.0.0.1','root','root','youTellMeDB')
    cursor= conn.cursor()
    cursor.execute(query_to_excute);
    surveys = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(surveys)

@app.route("/get_survey/<sid>", methods=["GET", "POST"])
def get_survey(sid):
    query_to_excute = "SELECT content FROM youTellMeDB.surveys WHERE id=%s";
    conn=MySQLdb.connect('127.0.0.1','root','root','youTellMeDB')
    cursor= conn.cursor()
    cursor.execute(query_to_excute,sid);
    survey = cursor.fetchone()
    return Response(response=survey,
                    status=200,
                    mimetype="application/json")

@app.route("/submit_survey", methods=["POST"])
def submit():
    return


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
