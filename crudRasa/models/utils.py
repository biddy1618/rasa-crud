from flask import jsonify
from pymystem3 import Mystem
from string import punctuation
import pickle
import os

mystem = Mystem()

with open("./crudRasa/static/stopwords.pickle", "rb") as file: # Unpickling
    stopwords = pickle.load(file)

def lemmatize(text):
    
    tokens = mystem.lemmatize(text.lower())
    tokens = [token for token in tokens if token not in stopwords\
        if token != " " and token.strip() not in punctuation]

    text = " ".join(tokens)
    
    return text

def result(status, message):
    return jsonify({
        'status': status,
        'message': message,
    })

def makeList(urlParams):
    
    params = urlParams.split(',')
    
    return params