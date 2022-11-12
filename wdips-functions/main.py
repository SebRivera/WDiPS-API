import flask

import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate("wdips-creds.json")
firebase_admin.initialize_app(cred)


def sayHelloword(request):
     return flask.jsonify({'title': 'Hello world'}), 201
 
 
 
# SUPERHEROES = db.reference('superheroes')

# def create_hero(request):
#     req = request.json
#     hero = SUPERHEROES.push(req)
#     return flask.jsonify({'id': hero.key}), 201

# def read_hero(id):
#     hero = SUPERHEROES.child(id).get()
#     if not hero:
#         return 'Resource not found', 404
#     return flask.jsonify(hero)

# def update_hero(id, request):
#     hero = SUPERHEROES.child(id).get()
#     if not hero:
#         return 'Resource not found', 404
#     req = request.json
#     SUPERHEROES.child(id).update(req)
#     return flask.jsonify({'success': True})

# def delete_hero(id):
#     hero = SUPERHEROES.child(id).get()
#     if not hero:
#         return 'Resource not found', 404
#     SUPERHEROES.child(id).delete()
#     return flask.jsonify({'success': True})

# def heroes(request):
#     if request.path == '/' or request.path == '':
#         if request.method == 'POST':
#             return create_hero(request)
#         else:
#             return 'Method not supported', 405
#     if request.path.startswith('/'):
#         id = request.path.lstrip('/')
#         if request.method == 'GET':
#             return read_hero(id)
#         elif request.method == 'DELETE':
#             return delete_hero(id)
#         elif request.method == 'PUT':
#             return update_hero(id, request)
#         else:
#             return 'Method not supported', 405
#     return 'URL not found', 404