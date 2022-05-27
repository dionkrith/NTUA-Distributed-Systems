import binascii
from wallet import wallet
from datetime import datetime
import hashlib
import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5,pkcs1_15
import json
import requests
import uuid
from flask import Flask, jsonify, request, render_template


class transaction():
	def __init__(self, sender_address, sender_private_key, recipient_address, value):
		self.sender_address = sender_address 
		self.receiver_address = recipient_address 
		self.amount = value
		self.date = datetime.timestamp(datetime.now())
		js_string = json.dumps(self.transaction_hash()).encode()
		self.transaction_id = SHA.new(js_string)
		self.transaction_inputs = {}
		self.transaction_outputs = []
		self.Signature = self.sign_transaction(sender_private_key)
 	
	def to_dict(self):
		return {"sender_address": self.sender_address.export_key('PEM').decode('UTF-8'), "receiver_address": self.receiver_address.export_key('PEM').decode('UTF-8'), "value": self.amount, "inputs" : self.transaction_inputs, "outputs": self.transaction_outputs ,"id" : self.transaction_id, "signature" : self.Signature}

	def to_send(self):
		to_send = {}
		to_send["sender_address"] = self.sender_address.export_key('PEM').decode('UTF-8')
		to_send["receiver_address"] = self.receiver_address.export_key('PEM').decode('UTF-8')
		to_send["value"] = self.amount
		to_send["inputs"] = self.transaction_inputs
		#print(to_send["inputs"]["previousOutputId"])
		#for i in range(0,len(to_send["inputs"]["previousOutputId"])):
		#	to_send["inputs"]["preiousOutputId"][i] = str(to_send["inputs"]["previousOutputId"][i])
		to_send["outputs"] = self.transaction_outputs
		#for i in range(0,len(to_send["outputs"])):
	#		to_send["outputs"][i]["id"] = str( to_send["outputs"]["id"])
		#	to_send["outputs"][i]["id_trans"] = str(to_send["outputs"][i]["id_trans"])
		#	to_send["outputs"][i]["recipient"] = to_send["outputs"][i]["recipient"].export_key('PEM').decode('UTF-8')

		to_send["datetime"] = self.date
		to_send["id"] = self.transaction_id.hexdigest()
		to_send["signature"] = self.Signature.decode("latin-1")

		return to_send
			
	
	def transaction_hash(self):
		return {"sender_address": self.sender_address.export_key('PEM').decode('UTF-8'), "receiver_address": self.receiver_address.export_key('PEM').decode('UTF-8'), "value": self.amount, "timestamp" : self.date}


	def sign_transaction(self , sender_private_key):
		"""
		Sign transaction with private key
		"""
		return pkcs1_15.new(sender_private_key).sign(self.transaction_id)

	def __str__(self):
		return str("Transaction: \nSender_address: %s\nRecipient_address: %s\nAmount: %s\n" %(self.sender_address.export_key("PEM") , self.receiver_address.export_key("PEM") , self.amount))


def verify_transaction(transaction):
	js = {"sender_address": transaction["sender_address"], "receiver_address": transaction["receiver_address"], "value": transaction["value"], "timestamp" : transaction["datetime"]}
	transaction_id = SHA.new(json.dumps(js).encode())
	public_key = RSA.import_key(transaction["sender_address"])
	Signature = transaction["signature"].encode("latin-1")
	try:
		pkcs1_15.new(public_key).verify(transaction_id,Signature)
		return True
	except (ValueError, TypeError):
		return False	
'''
def main():
	Wallet1 = wallet()
	Wallet2 = wallet()
	Wallet3 = wallet()
	trans = transaction(Wallet1.public_key,Wallet1.private_key,Wallet2.public_key,50)
	trans_to_send = trans.to_send()
	print(trans_to_send)
	#print(verify_transaction(Wallet1.public_key,js["id"],js["signature"]))
	#print(Wallet3.public_key.export_key('PEM'))
	#print(Wallet2.public_key.export_key('PEM'))
	#print(Wallet1.public_key.export_key('PEM'))
if __name__ == '__main__':
        main()
'''
