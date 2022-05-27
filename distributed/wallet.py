import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4



class wallet():

	def __init__(self):

		##set
		self.private_key = RSA.generate(2048 , e = 65537) #bits=2048 is reccomended and e should be an integer number at list 65537 
		self.public_key = self.private_key.publickey() 
		self.address = self.public_key
		#self.transactions =

	def balance(self):
		pass

	def __str__(self):
		return str("Wallet Data:\nPrivate_Key: %s\nPublic_Key: %s\nAddress: %s\n" %(self.private_key.exportKey("PEM") , self.public_key.exportKey("PEM") , self.address.exportKey("PEM")))

"""
def main():
	Wallet1 = wallet()
	print(Wallet1)

if __name__ == '__main__':
	main()
"""
