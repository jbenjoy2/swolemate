from flask import Flask, render_template, request, redirect, session
from google.oauth2 import id_token
from google.auth.transport import requests


app = Flask(__name__)

CLIENT_ID = '68392004616-tj0jco6efikrqfn9p52b604oc8hn9vql.apps.googleusercontent.com'


@app.route('/')
def main_route():
    return render_template('swolemate2.html')


@app.route('/home')
def logged_in_test():
    return render_template('logged_in_test.html')


@app.route('/login', methods=['POST'])
def verify_token():
    token = list(request.form.keys())[0]
    # print(token)
    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(
            token, requests.Request(), CLIENT_ID)

    # Or, if multiple clients access the backend server:
    # idinfo = id_token.verify_oauth2_token(token, requests.Request())
    # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
    #     raise ValueError('Could not verify audience.')

    # If auth request is from a G Suite domain:
    # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
    #     raise ValueError('Wrong hosted domain.')

    # ID token is valid. Get the user's Google Account ID from the decoded token.
        userid = idinfo['sub']
        print(userid)
        return redirect('/home')

    except ValueError:
        # Invalid token
        return redirect('/')
