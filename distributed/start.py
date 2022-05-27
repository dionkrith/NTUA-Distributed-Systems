import requests
import socket
import time 

if __name__ == '__main__':
	hostname = socket.gethostname()
	local_ip = socket.gethostbyname(hostname)
	BASE = 'http://'+local_ip+':5000/'
	f = open("transactions/5nodes/transactions0.txt", "r")
	lines = f.readlines()
	start = time.time()
	for line in lines[:20]:
		transaction = line.strip().split()
		print("I will create transaction from me to node " + transaction[0][2] + " with " + transaction[1] + " coins")
		response = requests.post(BASE + 'add/transaction/' + transaction[0][2]  + "/" + transaction[1])
		print(response.json())
	end = time.time()
	response = requests.get(BASE + 'experiments/' + str(end-start))
	js = response.json()
	print("Throughput: " + str(js["Throughput"]))
	print("Block Time: " + str(js["BlockTime"]))
