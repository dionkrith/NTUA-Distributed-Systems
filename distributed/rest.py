import requests
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import sys
import block
from node import node
import wallet
import transaction
import socket
from Crypto.PublicKey import RSA

### JUST A BASIC EXAMPLE OF A REST API WITH FLASK
import json


bootstrap = False
app = Flask(__name__)
CORS(app)

#find the local ip of the vm
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)

if(len(sys.argv) > 2):
	node = node(False,local_ip,5001)
else:
	if(local_ip == '192.168.1.1'):
		bootstrap = True
		node = node(True,local_ip,5000)
	else:
		node = node(False,local_ip,5000)
#.......................................................................................



# get all transactions in the blockchain

@app.route('/broadcast/transaction',methods=['POST'])
def broadcast_transaction():
	data = json.loads(request.data)
	if (node.validate_transaction(data)):
		response = {"message": "Transaction Broadcasted and Validated Succesfully"}
		return  response, 200
	else:
		response = {"message": "Transation was Broadcasted but didn't Validated Succesfully"}
		return response , 200

@app.route('/add/node', methods=['POST'])
def add():
	if(bootstrap):
		data = json.loads(request.data)
		public_key_str = data["public_key"]
		public_key = RSA.import_key(public_key_str)
		port = data["port"]
		ip = data["ip"]
		node.register_node_to_ring(ip,public_key,port)
		response = {"message": "Node Added", "id":node.current_id_count}
	else:
		response = {"message": "I am not Bootstrap"}

	return response , 200 

@app.route('/broadcast/ring', methods=['POST'])
def broadcast_ring():
	data = json.loads(request.data)	
	for i in range(0,len(data["value"])):
		data["value"][i]["public_key"] = RSA.import_key(data["value"][i]["public_key"])
	node.update_ring(data["value"],data["utxo"] , data["blockchain"])
	response = {"message": "Data succesfully update my ring"}
	return response , 200

@app.route('/broadcast/block' , methods=['POST'])
def broadcast_block():
	data = json.loads(request.data)
	succeded = node.validate_block_and_add(data)
	if(succeded):
		response = {"message": "Block added to blockchain"}
	else:
		response = {"message": "Block failed to validate"}
	return response , 200

@app.route('/add/transaction/<int:node_id>/<int:amount>' , methods=['POST'])
def add_transaction(node_id , amount): 
	#node.create_transaction(receiver_address  , amount)
	if (node.id == node_id):
		response = {"message":"You can't give to yourself money..."}
		return response , 400
	else:
		receiver_address = node.ring[node_id]["public_key"]
		if(node.create_transaction(receiver_address , amount)):
			response = {"message": "Transaction was created"}
		else:
			response = {"message": "Wallet balance is not enough for the transaction"}
		return response , 200
	
@app.route('/balance', methods=['GET'])
def get_balance():
	balance = node.wallet_balance()
	response = {"message":  "{} NBC in wallet".format(balance)}
	return response , 200


@app.route('/get/lengths', methods=['GET'])
def get_lengths():
	response = {"length": len(node.blockchain.chain)}
	return response , 200


@app.route('/resolve/conflict', methods=['GET'])
def solve_conflict():
	response = {"blockchain": node.blockchain.chain, "utxos": node.utxos}
	return response , 200
	
@app.route('/getblock', methods=['GET'])
def get_block():
	for block in node.blockchain.chain:
		print(block["previous_hash"])
		print(block["hash"])
		print()
	response = {"message": "print"}
	return response , 200


@app.route('/allbalance', methods=['GET'])
def show_allbalance():
	response_balances = []
	balances = node.get_all_wallet_balance()
	if(len(balances) == 0):
		response = {"message": "Empty utxo list"}
		return response , 200
	for i,coins in enumerate(balances):
		response_balances.append("Node " + str(i) + " has " + str(coins) + " NBCs")
	response = {"message": response_balances}
	return response , 200

@app.route('/last/block' , methods=['GET'])
def last_block():
	result = node.view_transactions()
	return result , 200
	
@app.route('/experiments/<float:time>' , methods=['GET'])
def calculate_time(time):
	if(len(node.mining_block_times) == 0):
		mining_time = 0
	else:
		mining_time = sum(node.mining_block_times)/len(node.mining_block_times)
	throughput = node.count_of_transactions_served/time
	response = {"Throughput": throughput, "BlockTime": mining_time}
	return response , 200
# run it once fore every node

if __name__ == '__main__':
	from argparse import ArgumentParser
	parser = ArgumentParser()
	parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on') 
	args = parser.parse_args()
	port = args.port
	app.run(host=local_ip, port=port)

    

