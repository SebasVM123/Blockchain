import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
import uuid
from urllib.parse import urlparse

class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions = [] #Se agregan las transacciones
        self.wallets = {}
        self.create_block(proof = 1, previous_hash = '0')
        self.nodes = set() #Se agregan los nodos como set ya que pueden estar dispersos en cualquier parte
                           #Se usan en el protocolo de consenso (Todos los nodos aceptan y mantienen la misma cadena de bloques)
        #self.wallet = 100 #Se agrega el wallet inicial
        
    # Método para generar una nueva dirección (wallet)
    def generate_wallet(self):
        self.my_wallet = str(uuid.uuid4())
        self.wallets[self.my_wallet] = 100
        return self.my_wallet
    
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
        self.update_chain_wallet(self.chain)
        #self.update_wallets(block['transactions'])
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
    
    # Método para enviar monedas de una dirección a otra
    def send_coins(self, sender, receiver, amount):
        if sender not in self.wallets or self.wallets[sender] < amount:
            return {'error': 'Fondos insuficientes'}

        '''self.wallets[sender] -= amount
        if receiver not in self.wallets:
            self.wallets[receiver] = amount
        else:
            self.wallets[receiver] += amount'''

        transaction = {'sender': sender, 'receiver': receiver, 'amount': amount}
        self.add_transactions(transaction['sender'], transaction['receiver'], transaction['amount'])
        self.broadcast_transaction(transaction)
        return {'message': 'Transacción exitosa'}
    
    # Método para sincronizar el registro de saldos con otros nodos
    '''def sync_wallets(self):
        for node in self.nodes:
            url = f'http://{node}/get_wallets'
            try:
                response = requests.get(url)
                response.raise_for_status()
                remote_wallets = response.json()['wallets']
                self.wallets.update(remote_wallets)
            except requests.exceptions.RequestException as e:
                print(f"Error al sincronizar el registro de saldos con {node}: {e}")'''

    # Método para actualizar el registro de saldos con las transacciones de un bloque
    def update_wallets(self, transactions):
        for transaction in transactions:
            sender = transaction['sender']
            receiver = transaction['receiver']
            amount = transaction['amount']

            if sender not in self.wallets:
                self.wallets[sender] = 100
            self.wallets[sender] -= amount

            if receiver not in self.wallets:
                self.wallets[receiver] = 100 + amount
                print(self.wallets[receiver])
            else:
                self.wallets[receiver] += amount

    def update_chain_wallet(self, chain):
        for key in self.wallets.keys():
            self.wallets[key] = 100
        for block in chain:
            self.update_wallets(block['transactions'])

    # Método para verificar el saldo de una dirección
    def get_balance(self, address):
        if address not in self.wallets:
            return {'error': 'Dirección no encontrada'}
        return {'balance': self.wallets[address]}

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

    # Método para difundir la transacción a todos los nodos de la red
    def broadcast_transaction(self, transaction):
        for node in self.nodes:
            url = f'http://{node}/add_transaction'
            try:
                response = requests.post(url, json=transaction)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error al difundir la transacción a {node}: {e}")
