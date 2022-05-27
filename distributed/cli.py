import requests
import socket

if __name__ == '__main__':
	from argparse import ArgumentParser
	hostname = socket.gethostname()
	local_ip = socket.gethostbyname(hostname)
	parser = ArgumentParser()
	parser.add_argument('--view' , action='store_true' , help='Print the transactions that are contained in the last validated noobcash block')
	parser.add_argument('--balance' , action='store_true' , help='Print balance of the wallet')
	parser.add_argument('--printhelloworld' , action='store_true' , help='Print helloworld')
	parser.add_argument('--t' , nargs=2 , help='create new transaction')
	parser.add_argument('--show', action='store_true', help='show blockchain')
	parser.add_argument('--allbalance', action='store_true', help='show balance of everyone')
	args = parser.parse_args()
	view = args.view
	show = args.show
	balance = args.balance
	allbalance = args.allbalance
	printhelloworld = args.printhelloworld
	create_transaction = args.t
	BASE = 'http://'+local_ip+':5000/'
	if allbalance:
		response = requests.get(BASE + 'allbalance')
		print(response.json())
	if show:
		requests.get(BASE+ 'getblock')
	if balance == True:
		response = requests.get(BASE + 'balance')
		print(response.json())
	if create_transaction is not None:
		response = requests.post(BASE + 'add/transaction/' + create_transaction[0] + "/" + create_transaction[1])
		print(response.json())	

	if view:
		response = requests.get(BASE + 'last/block')
		response = response.json()
		print("Last block of Blockchain:")
		print("Index:" + " " + str(response["index"]))
		print("Previous Hash:" + " " + str(response["previous_hash"]))
		print("Hash: " + str(response["hash"]))
		print("Transactions of last Block:")
		for transaction in response["transactions"]:
			print("Transaction with id: " + str(transaction["id"]))
