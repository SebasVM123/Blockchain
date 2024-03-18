from flask import Flask, jsonify, request
from config.blockchain import Blockchain
from uuid import uuid4
#import socket
from flask_cors import CORS, cross_origin
import requests
app = Flask(__name__)

CORS(app)
#Creamos una dirección para el Nodo en Puerto 5000
node_address = str(uuid4()).replace('-', '') #crea una dirección única aleatoria
#local_address = socket.gethostbyname(socket.gethostname())

#Creamos la blockchain
blockchain = Blockchain()

#Minando un nuevo bloque
@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    #blockchain.add_transactions(sender = node_address, receiver = 'Gerwin', amount = 10)
    block = blockchain.create_block(proof, previous_hash)
    
    response = {"message": "Felicidades, minaste un bloque!",
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']}
    
    return jsonify(response), 200

#Obteniendo Cadena Completa
@cross_origin()
@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
               'length': len(blockchain.chain)}
    return jsonify(response), 200

#Obteniendo validez de cadena de bloques
@cross_origin()
@app.route("/is_valid", methods=['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'La cadena de bloques es valida'}
    else:
        response = {'message': 'Oh no... la cadena no es valida '}
    return jsonify(response), 200

@app.route("/add_transaction", methods=['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all (key in json for key in transaction_keys):
        return "Faltan algunos elementos de la transacción", 400
    
    index = blockchain.add_transactions(json['sender'], json['receiver'], json['amount'])
    response = {'message':f'La transacción fue añadida al bloque: {index}'}
    
    return jsonify(response), 201

#Descentralizar el Blockchain
@cross_origin()
@app.route("/connect_node", methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No node", 401
    for node in nodes:
        blockchain.add_node(node)
    response = {'message':'Todos los nodos están conectados, la red contiene los siguientes nodos: ',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201

#Reemplazar cadenas por la más larga
@cross_origin()
@app.route("/replace_chain", methods=['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message': 'Algunos nodos tenían cadenas diferentes, fueron reemplazadas por la cadena más larga.',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'Todos los nodos ya tienen la cadena más larga',
                    'actual_chain' : blockchain.chain}
    return jsonify(response), 200

'''@cross_origin()
@app.route('/broadcast_transaction', methods=['POST'])
def broadcast_transaction_route():
    transaction = request.get_json()
    blockchain.broadcast_transaction(transaction)
    return jsonify({'message': 'Transacción difundida correctamente'}), 201'''

@cross_origin()
@app.route('/get_wallets', methods=['GET'])
def get_wallets():
    return jsonify({'wallets': blockchain.wallets}), 200

@cross_origin()
@app.route('/generate_wallet', methods=['GET'])
def generate_wallet_route():
    wallet_address = blockchain.generate_wallet()
    return jsonify({'wallet_address': wallet_address}), 200

@cross_origin()
@app.route('/get_balance/<address>', methods=['GET'])
def get_balance_route(address):
    balance = blockchain.get_balance(address)
    return jsonify(balance), 200

@cross_origin()
@app.route('/send_coins', methods=['POST'])
def send_coins_route():
    data = request.get_json()
    receiver = data['receiver']
    amount = data['amount']

    result = blockchain.send_coins(blockchain.my_wallet, receiver, amount)
    return jsonify(result), 200

#Corriendo el App
#app.run(host='0.0.0.0', port='5000')


