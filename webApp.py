from flask import Flask, request, jsonify, redirect, url_for, session, Response
from flask.templating import render_template
import requests
from flask_oauth import OAuth
import MySQLdb
import json
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key="secret"

@app.route('/')
def index():
    if not session.get('logged_in'):
        return Response(status=500)
    else:
        return "Welcome to YouTellMe Service!"

@app.route('/register',methods=["POST"])
def signup():
    request_dict = request.get_json()
    username=request_dict['user_name']
    passwd=request_dict['password']
    name=request_dict['fname']
    role = "user"

    conn=MySQLdb.connect('127.0.0.1','root','root','youTellMeDB')
    cursor= conn.cursor()
    cursor.execute("""INSERT IGNORE INTO youTellMeDB.Users VALUES(%s, %s, %s, %s)""",(username, role, name, generate_password_hash(passwd)))
    conn.commit()
    cursor.close()
    conn.close()
    return Response(status=200)

@app.route('/login/<username>/<passwd>',methods=['GET','POST'])
def login(username,passwd):
    conn=MySQLdb.connect('127.0.0.1','root','root','youTellMeDB')
    cursor= conn.cursor()
    cursor.execute("SELECT id,passwordHash FROM youTellMeDB.Users WHERE id=%s",[username]);
    resultSet = cursor.fetchone()
    validUser = resultSet[0]
    hashPasswd = resultSet[1]
    cursor.close()
    conn.close()

    if validUser and check_password_hash(hashPasswd,passwd):
        session['user'] = username
        session['logged_in'] = True

        return Response(status=200)
    else:
        return Response(status=401)

@app.route("/list_surveys",methods=['GET','POST'])
def list_surveys():
    surveyList = []
    query_to_excute = "SELECT id,title FROM youTellMeDB.surveys";
    conn=MySQLdb.connect('127.0.0.1','root','root','youTellMeDB')
    cursor= conn.cursor()
    cursor.execute(query_to_excute);
    resultSet = cursor.fetchall()

    for res in resultSet:
        surveyListDict = {}
        surveyListDict['id'] = str(res[0])
        surveyListDict['title'] = res[1]
        surveyList.append(surveyListDict)

    cursor.close()
    conn.close()
    return jsonify(surveyList)

@app.route("/get_survey/<sid>", methods=["GET", "POST"])
def get_survey(sid):
    query_to_excute = "SELECT content FROM youTellMeDB.surveys WHERE id=%s";
    conn=MySQLdb.connect('127.0.0.1','root','root','youTellMeDB')
    cursor= conn.cursor()
    cursor.execute(query_to_excute,sid);
    survey = cursor.fetchone()
    cursor.close()
    conn.close()
    return Response(response=survey,
                    status=200,
                    mimetype="application/json")

@app.route("/submit_survey", methods=["POST"])
def submit():
    #currentUser =  session.get('user')
    request_dict = request.get_json()
    sid = request_dict['surveyID']
    content = request_dict['responses']
    currentUser = "utphala.p@gmail.com"

    conn=MySQLdb.connect('127.0.0.1','root','root','youTellMeDB')
    cursor= conn.cursor()
    cursor.execute("""INSERT IGNORE INTO youTellMeDB.responses(user_id, survey_id, responses) VALUES( %s, %s, %s);""",(currentUser, int(sid), str(content)))
    conn.commit()
    cursor.close()
    conn.close()

    return Response(status=200)

@app.route('/logout')
def logout():
    session.clear()
    session['logged_in'] = False
    return Response(status=200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
