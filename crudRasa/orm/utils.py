from flask import jsonify
import requests
from requests.auth import HTTPBasicAuth


from pymystem3 import Mystem
from string import punctuation
import pickle
import os

from app import app

mystem = Mystem()


with open("./crudRasa/static/stopwords.pickle", "rb") as file: # Unpickling
    stopwords = pickle.load(file)

def lemmatize(text):
    
    tokens = mystem.lemmatize(text.lower())
    tokens = [token for token in tokens if token not in stopwords\
        if token != " " and token.strip() not in punctuation]

    text = " ".join(tokens)
    
    return text

def result(status, message=None):
    return jsonify({
        'status': status,
        'message': message,
    })

def makeList(urlParams):
    if urlParams is None:
        params = []
    else:
        params = urlParams.split(',')
    
    return params


def checkAuth(token):
    token = token.split()[-1]
    r = requests.post(
        app.config['AUTH_URL'],
        data={'token': token},
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        auth=HTTPBasicAuth(app.config['AUTH_CLIENT_ID'], app.config['AUTH_SECRET'])
    )
        
    return True if r.status_code == 200 else False