from wallet import wallet
import requests 
import uuid
from transaction import transaction, verify_transaction
from Crypto.PublicKey import RSA
import socket
import json
import threading
import time
from blockchain import blockchain , blockchain_to_send
from block import Block

class node:

	def __init__(self , bootstrap, ip, port, children = 4):
				
		self.utxos = []
		self.block_to_add = Block(0,0,0)
		self.blockchain = blockchain(1,4)
		self.is_bootstrap = bootstrap
		self.count_of_transactions_served = 0
		self.mining_block_times = []

		if bootstrap == True:
			self.first_blocks = []
			self.id = 0
			self.event = threading.Event()
			self.thread = threading.Thread(target = self.start)
			self.children = children
			self.current_id_count = 0
			
			self.wallet = self.create_wallet() 
			self.ring = [{"port":5000,"ip":"192.168.1.1","balance":500,"public_key":self.wallet.address}]
			self.genesis = self.create_genesis_block()
			init_transaction = self.first_transaction(500)
			self.genesis.listOfTransactions.append(init_transaction.to_send())
			self.blockchain.add_block(self.genesis.to_send())
			self.block_to_add.previousHash = self.blockchain.chain[-1]["hash"]
			self.thread.start()
			

		else:
			self.wallet = self.create_wallet()
			self.ring = []
			hostname = socket.gethostname()
			local_ip = socket.gethostbyname(hostname)
			response = requests.post("http://192.168.1.1:5000/add/node", json.dumps({"ip": local_ip, "public_key": self.wallet.address.export_key("PEM").decode("UTF-8") , "port": port}))
			self.id = response.json()["id"]
			print("Congrats!!!! You enter the Noobcash. Your id is {}".format(self.id))

	def start(self):
		self.event.wait()
		time.sleep(1)
		to_send = {"value":self.ring}
		if(self.current_id_count == self.children):
			self.event.set()
			to_send = {"value":self.ring}
			for i in range(0,len(self.ring)):
				to_send["value"][i]["public_key"] = to_send["value"][i]["public_key"].export_key("PEM").decode("UTF-8")
			to_send["utxo"] = self.utxos
			for block in self.first_blocks:
				self.blockchain.chain.append(block)
			to_send["blockchain"] = blockchain_to_send(self.blockchain)["blockchain"]
			for node in self.ring:
				response = requests.post("http://" + str(node["ip"]) + ":" + str(node["port"]) + "/broadcast/ring", json.dumps(to_send))
		return 0


	def get_all_wallet_balance(self):
		balance_all = []
		balance = 0
		for node in self.ring:
			for output in self.utxos:
				if(output["recipient"] == node["public_key"].export_key("PEM").decode("UTF-8")):
					balance += output["amount"]
			balance_all.append(balance)
			balance = 0
		return balance_all


	def wallet_balance(self):
		balance = 0
		for output in self.utxos:
			if(output["recipient"] == self.wallet.address.export_key("PEM").decode("UTF-8")):
				balance += output["amount"]
		return balance
	
	def create_genesis_block(self):
		return Block(0,0,1)	

	def create_new_block(self):
		return Block(len(self.blockchain.chain) + 1, 0,self.blockchain.chain[-1].hash)
		

	def create_wallet(self):
		#create a wallet for this node, with a public key and a private key
		return wallet()

	def register_node_to_ring(self,ip,public_key,port):
		#add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
		#bottstrap node informs all other nodes and gives the request node an id and 100 NBCs
		self.ring.append({"port":port,"ip":ip,"balance":0,"public_key":public_key})
		self.current_id_count += 1
		
		tr = self.create_first_transaction(public_key,100)
		
		if(self.current_id_count == self.children):
			self.event.set()



	def update_ring(self,ring,utxos , blockchain_sended): #blockchain is a list of blocks.to_send()
		self.ring = ring
		self.utxos = utxos
		if self.is_bootstrap == False:
			for block_sended in blockchain_sended:
				block = Block(block_sended["index"] , block_sended["nonce"] , block_sended["previous_hash"])
				block.timestamp = block_sended["timestamp"]
				block.hash = block_sended["hash"]
				for transaction_sended in block_sended["transactions"]:
					block.listOfTransactions.append(transaction_sended)
				self.blockchain.chain.append(block.to_send())
			if (self.valid_chain()):
				print("I received a valid Blockchain......" )	
		self.block_to_add.previousHash = self.blockchain.chain[-1]["hash"]
		return True
	
	def first_transaction(self, amount):
		key = RSA.generate(2048 , e = 65537)
		transaction1 = transaction(key.public_key(), key, self.wallet.address , amount)
		self.utxos.append({"id" : str(uuid.uuid1()), "id_trans" : str(transaction1.transaction_id) ,"recipient" : self.wallet.address.export_key("PEM").decode("UTF-8") , "amount" : amount})
		return transaction1
	

	def create_first_transaction(self, receiver, amount):
		first_transaction = transaction(self.wallet.address,self.wallet.private_key,receiver,amount)
		balance_so_far = 0
		inputs = {"previousOutputId":[]}
		for output in self.utxos:
			if(output["recipient"] == self.wallet.address.export_key("PEM").decode("UTF-8")):
				balance_so_far += output["amount"]
				inputs["previousOutputId"].append(output["id"])
				if(balance_so_far >= amount):
					break
		outputs = [{"id" : str(uuid.uuid1()), "id_trans" : str(first_transaction.transaction_id) ,"recipient" : receiver.export_key("PEM").decode("UTF-8") , "amount" : amount},{"id" : str(uuid.uuid1()), "id_trans" : str(first_transaction.transaction_id) ,"recipient" : self.wallet.public_key.export_key("PEM").decode("UTF-8") , "amount" : balance_so_far - amount}]
		first_transaction.transaction_inputs = inputs
		first_transaction.transaction_outputs = outputs
		if(self.validate_transaction(first_transaction.to_send() , first_transactions = True)):
			return first_transaction
	
		return False

	def create_transaction(self, receiver, amount):
		transaction1 = transaction(self.wallet.address,self.wallet.private_key,receiver,amount)
		balance_so_far = 0
		inputs = {"previousOutputId":[]}
		for output in self.utxos:
			if(output["recipient"] == self.wallet.address.export_key("PEM").decode("UTF-8")):
				balance_so_far += output["amount"]
				inputs["previousOutputId"].append(output["id"])
				if(balance_so_far >= amount):
					break
		if(balance_so_far < amount):
			return False
		outputs = [{"id" : str(uuid.uuid1()), "id_trans" : str(transaction1.transaction_id) ,"recipient" : receiver.export_key("PEM").decode("UTF-8") , "amount" : amount},{"id" : str(uuid.uuid1()), "id_trans" : str(transaction1.transaction_id) ,"recipient" : self.wallet.public_key.export_key("PEM").decode("UTF-8") , "amount" : balance_so_far - amount}]
		transaction1.transaction_inputs = inputs
		transaction1.transaction_outputs = outputs
		self.broadcast_transaction(transaction1.to_send())
		
		return transaction1


	def broadcast_transaction(self,transaction): #tranasction is a dict
		for node in self.ring:
			response = requests.post("http://" + str(node["ip"]) + ":" + str(node["port"]) + "/broadcast/transaction", json.dumps(transaction))
		return True		

	def validate_transaction(self, transaction , first_transactions = False): #transaction is a dictionary
		if(verify_transaction(transaction) == False):
			return False
		if(all(item in [d["id"] for d in self.utxos] for item in transaction["inputs"]["previousOutputId"])):
			self.utxos = [output for output in self.utxos if output["id"] not in transaction["inputs"]["previousOutputId"]]
			self.utxos.append(transaction["outputs"][0])
			self.utxos.append(transaction["outputs"][1])
			self.add_transaction_to_block(transaction , first_transactions)
			self.count_of_transactions_served += 1
			return True
		return False

	def add_transaction_to_block(self,transaction,first_transactions = False):
		last_block = self.blockchain.chain[-1]
		if(len(self.block_to_add.listOfTransactions) < self.blockchain.capacity):
			self.block_to_add.listOfTransactions.append(transaction)
			
		if(len(self.block_to_add.listOfTransactions) == self.blockchain.capacity):
			self.block_to_add.index = last_block["index"] + 1
			self.block_to_add.nonce = 0
			self.mine_block(self.block_to_add,first_transactions)
			self.block_to_add = Block(0,0,self.blockchain.chain[-1]["hash"])
		return True
			

	def mine_block(self,block,first_transactions):
		nonce = 0
		start = time.time()
		while(True):
			block.nonce = nonce	
			a = block.myHash()[:self.blockchain.difficulty]
			if(a == "0"*self.blockchain.difficulty):
				if(not(first_transactions)):
					self.broadcast_block(block.to_send())
				else:
					if(len(self.first_blocks) > 0):
						block.previousHash = self.first_blocks[-1]["hash"]
					self.first_blocks.append(block.to_send())
				break
			else:
				nonce += 1
		end = time.time()
		self.mining_block_times.append(end-start)
		return True

	def broadcast_block(self,block): #block is a dictionary
		for node in self.ring:
			response = requests.post("http://" + str(node["ip"]) + ":" + str(node["port"]) + "/broadcast/block", json.dumps(block))
		
		return True

	def validate_block_and_add(self,block):
		block_val = Block(block["index"],block["nonce"],block["previous_hash"])
		block_val.listOfTransactions = block["transactions"]
		block_val.timestamp = block["timestamp"]
		block_val.hash = block_val.myHash()
		last_block = self.blockchain.chain[-1]
		if(last_block["hash"] == block_val.previousHash and block_val.hash == block["hash"]):
			self.blockchain.add_block(block_val.to_send())
			return True
		if(last_block["hash"] != block_val.previousHash):
			self.resolve_conflicts()
			return True
		return False

	def validate_block(self,block,position):
		block_val = Block(block["index"],block["nonce"],block["previous_hash"])
		block_val.listOfTransactions = block["transactions"]
		block_val.timestamp = block["timestamp"]
		block_val.hash = block_val.myHash()
		last_block = self.blockchain.chain[position-1]
		if(last_block["hash"] == block_val.previousHash and block_val.hash == block["hash"]):
			return True
		return False

	def valid_chain(self):
		validated = True 
		for pos,block in enumerate(self.blockchain.chain):
			if pos > 0:
				if(not(self.validate_block(block,pos))):
					validated = False
		return validated

	def resolve_conflicts(self):
		maximum = 0
		maximum_ip = ""
		for node in self.ring:
			response = requests.get("http://" + str(node["ip"]) + ":" + str(node["port"]) + "/get/lengths")
			response = response.json()
			if(response["length"] > maximum):
				maximum = response["length"]
				maximum_ip = node["ip"]
		response = requests.get("http://" + str(maximum_ip) + ":" + str(node["port"]) + "/resolve/conflict")
		js = response.json()
		self.utxos = js["utxos"]
		self.blockchain.chain = js["blockchain"]
		return True


	def view_transactions(self):
		last_block = self.blockchain.chain[-1]
		json = {}
		json["transactions"] = []
		json["index"] = last_block["index"]
		json["previous_hash"] = last_block["previous_hash"]
		json["hash"] = last_block["hash"]
		for transaction in last_block["transactions"]:
			transaction_out = {}
			transaction_out["id"] = transaction["id"]
			json["transactions"].append(transaction_out)		

		return json

	
