from flask import Flask, jsonify, request
from config.blockchain import Blockchain
from uuid import uuid4


app = Flask(__name__)


#Creamos una dirección para el Nodo en Puerto 5000
node_address = str(uuid4()).replace('-', '') #crea una dirección única aleatoria


#Creamos la blockchain
blockchain = Blockchain()

#Minando un nuevo bloque
@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transactions(sender = node_address, receiver = 'Gerwin', amount = 1)
    block = blockchain.create_block(proof, previous_hash)
    
    response = {"message": "Felicidades, minaste un bloque!",
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']}
    
    return jsonify(response), 200

#Obteniendo Cadena Completa
@app.route('/get_chain', methods=['GET'])
def get_chain():
    reponse = {'chain': blockchain.chain,
               'length': len(blockchain.chain)}
    return jsonify(reponse), 200

#Obteniendo validez de cadena de bloques
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
@app.route("/is_valid", methods=['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message': 'Algunos nodos tenían cadenas diferentes, fueron reemplazadas por la cadena más larga.',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'Todos los nodos ya tienen la cadena más larga',
                    'actual_chain' : blockchain.chain}
    return jsonify(response), 200

#Corriendo el App
#app.run(host='0.0.0.0', port='5000')


