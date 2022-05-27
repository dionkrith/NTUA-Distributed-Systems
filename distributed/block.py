import blockchain
import hashlib
import time
import json 

class Block():
	
	def __init__(self , index , nonce , previousHash):
		self.index = index
		self.nonce = nonce
		self.previousHash = previousHash
		self.listOfTransactions = []
		self.timestamp = time.time()
		self.hash = self.myHash()

	def update_hash(self , *args):
        	hashing_text = ""
        	h = hashlib.sha256()
        	count = 0
        	for arg in args:
                	hashing_text += str(arg)
                	count = count + 1
        	h.update(hashing_text.encode('utf-8'))
        	return h.hexdigest()

	def myHash(self):
		self.hash = self.update_hash(self.index , self.nonce , self.previousHash , self.listOfTransactions , self.timestamp)
		return self.hash
	
	def to_dict(self):
		return {"index": self.index , "transactions": self.listOfTransactions , "nonce": self.nonce ,"hash": self.hash ,"previous_hash": self.previousHash, "timestamp": self.timestamp}

	def to_send(self):
		to_send = {}
		to_send["index"] = self.index
		to_send["transactions"] = self.listOfTransactions
		for i in range(0,len(self.listOfTransactions)):
			if(not type(to_send["transactions"][i]) is dict):
				to_send["transactions"][i] = to_send["transactions"][i].to_send()
	
		to_send["nonce"] = self.nonce
		to_send["hash"] = self.hash
		to_send["previous_hash"] = self.previousHash
		to_send["timestamp"] = self.timestamp
		return to_send

	def print_transactions(self):
		for transaction in self.listOfTransactions:
			print(transaction)

	def __str__(self):
		return str("Block Data:\nIndex: %s\nTimestamp: %s\nTransactions: %s\nNonce: %s\nBlockHash: %s\nPreviousHash: %s\n" %(self.index , self.timestamp , self.listOfTransactions , self.nonce , self.hash , self.previousHash))
		

'''
def main():
	block = Block(0 , 0 , "12")
	print(block)
	

if __name__ == '__main__':
	main()	
'''
