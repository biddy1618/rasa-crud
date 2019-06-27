from flask import jsonify

def result(status, message):
    return jsonify({
        'status': status,
        'message': message,
    })