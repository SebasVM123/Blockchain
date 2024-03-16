from flask import Flask, jsonify
from config.blockchain import Blockchain

app = Flask(__name__)
blockchain = Blockchain()

#Minando un nuevo bloque
@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash)
    
    response = {"message": "Congratulations, you've mined a block!",
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash']}
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
        response = {'message': 'The Blockchain is valid'}
    else:
        response = {'message': 'Oh no... The block isn´t valid '}
    return jsonify(response), 200
        
#Corriendo el App
#app.run(host='0.0.0.0', port='5000')

