import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse


class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions = [] #Se agregan las transacciones
        self.create_block(proof = 1, previous_hash = '0')
        self.nodes = set() #Se agregan los nodos como set ya que pueden estar dispersos en cualquier parte
                           #Se usan en el protocolo de consenso (Todos los nodos aceptan y mantienen la misma cadena de bloques)
        
    def add_node(self, address):
        """
        Descripción: añade el nodo a nuestra red de nodos
        """
        parsed_url = urlparse(address) #Analiza el url
        self.nodes.add(parsed_url.netloc)
        
    def replace_chain(self):
        """
        Descripción: se establece el protocolo de consenso donde se analizan las cadenas de la red y se escoge la más larga"""
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
            
            if longest_chain:
                self.chain = longest_chain
                return True
            return False
        
    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1, 
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash' : previous_hash, 
                 'transactions': self.transactions}
        
        self.transactions = []
        self.chain.append(block)
        return block
    
    def add_transactions(self, sender, receiver, amount):
        """
        Descripción: añade la transacción a la lista de transacciones
        """
        self.transactions.append({'sender': sender,
                                  'receiver': receiver,
                                  'amount': amount})
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1
    
    def get_previous_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            
            previous_block = block
            block_index += 1
        return True
    

#Cración de la API
app = Flask(__name__)


#Creamos una dirección para el Nodo en Puerto 5001
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
    block = blockchain.create_block(proof, previous_hash)
    blockchain.add_transactions(sender = node_address, receiver = 'Pablo ', amount = 1)
    
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
        response = {'message': 'La de bloques es valida'}
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

@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No node", 401
    for node in nodes:
        blockchain.add_node(node)
    response = {'message':'Todos los nodos están conectados, la red contiene los siguientes nodos',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201

#Reemplazar cadenas por la más larga
@app.route("/replace_chain", methods=['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message': 'Algunos nodos tenían cadenas diferentes, fueron reemplazada por la cadena más larga.',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'Todos los nodos ya tienen la cadena más larga',
                    'actual_chain' : blockchain.chain}
    return jsonify(response), 200

#Corriendo el App
app.run(host='0.0.0.0', port='5002')