import flask
from main import sayHelloword

app = flask.Flask('functions')
methods = ['GET', 'POST', 'PUT', 'DELETE']

@app.route('/test', methods=methods)
@app.route('/test/<path>', methods=methods)
def catch_all(path=''):
    flask.request.path = '/' + path
    return sayHelloword(flask.request)

if __name__ == '__main__':
    app.run()