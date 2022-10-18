from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/ping')
def ping():
    print('pong')
    return jsonify({'message': 'pong'})
    
@app.route('/products', methods=['GET'])
def get_products():
    return jsonify({'products': ['milk', 'eggs', 'bread']})

@app.route('/products', methods=['POST'])
def addProduct():
    new_product = {
        'name': request.json['name'],
        'price': request.json['price'],
        'quantity': request.json['quantity']
    }
    return jsonify({'message': 'product added successfully'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
