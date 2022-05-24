# Authentication decorator
from functools import wraps
from flask import Flask, request, make_response, jsonify


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        # zajistí, aby byl token jwt předán se záhlavími
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token: # vyhodí chybu, pokud není poskytnut žádný token
            return make_response(jsonify({"message": "A valid token is missing!"}), 401)

         # Vratí informace o uživateli připojenému k tokenu
        return f(*args, **kwargs)
    return decorator