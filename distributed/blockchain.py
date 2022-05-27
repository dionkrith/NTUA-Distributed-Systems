import block

class blockchain():
	
	def __init__(self , capacity, difficulty):
		self.difficulty = difficulty
		self.chain = []
		self.capacity = capacity
	
	def add_block(self , block):
		self.chain.append(block)
	
	def to_dict(self):
		blockchain = {}
		blockchain["blocks"] = []
		for block in self.chain:
			blockchain["blocks"].append(block.to_dict())
		return blockchain
	

	"""
	def to_send(self,blockchain):
		sended_blockchain = blockchain 
		to_send = {}
		to_send["blockchain"] = self.chain
		print("I print the length of blockchain------------")
		print(len(self.chain))
		for i,block in enumerate(sended.chain):
			print("Change the form of every block in Blockchain-----------")
			to_send["blockchain"][i] = block.to_send()

		return to_send
	"""

	def __str__(self):
		string = ""
		for block in self.chain:
			string = string + block.__str__()  + "\n"
	
		return "All Blocks of Blockchain:\n" + string


def blockchain_to_send(blockchain):
	to_send = {}
	to_send["blockchain"] = blockchain.chain
	#print("I print the length of blockchain------------")
	#print(len(blockchain.chain))
	#for i,block in enumerate(blockchain.chain):
		#print("Change the form of every block in Blockchain-----------")
	#	to_send["blockchain"][i] = block.to_send()
	return to_send




'''
def main():
	blockhain = Blockchain(4)
	my_hash = block.myHash()
	block = Block(0 , 0 , "12")
	print(block)
	my_hash = block.myHash()

if __name__ == '__main__':
	main()
'''				
