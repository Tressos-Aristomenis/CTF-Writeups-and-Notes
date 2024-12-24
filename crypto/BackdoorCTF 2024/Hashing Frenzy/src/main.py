from Crypto.Util.number import *
from flag import flag
import hashlib
import random

class testhash:
    def __init__(self, data):
        self.data = data

    def digest(self):
        return self.data 

## more hashes, more security
hashes = []
hashes.append(testhash)
hashes.append(hashlib.md5)
hashes.append(hashlib.sha224)
hashes.append(hashlib.sha256)
hashes.append(hashlib.sha3_224)
hashes.append(hashlib.sha3_256)

BITS = 2048
p = getPrime(BITS) 

def menu():
    print("1. Sign a message")
    print("2. Verify a Signature for a message")

def ask():
    response = int(input("Enter your choice: "))
    if response < 1 or response > 2:
        exit(0)

    return response

welcome_message = '''Welcome to My Extra Hashes Extra Secure Edition of my very own Message Signature and Verification Scheme. Since it's a good practice to use secure hashes, I've combined multiple hashes in this scheme.'''
print(welcome_message) 

def generate_signatures(message):
    signatures = []
    accumulate = 0
    
    for hash_object in hashes:
        signatures.append(random.randint(2, p - 1))
        accumulate += bytes_to_long(hash_object(message).digest()) * signatures[-1] % p

    signatures.append(accumulate)
    return signatures

def verify_signature(message, signatures):
    accumulate = 0

    for index, hash_object in enumerate(hashes):
        hashed_message = bytes_to_long(hash_object(message).digest())
        accumulate += hashed_message * signatures[index] % p 

    if accumulate == signatures[-1]:
        return True 

    return False

testing_message = '''To prove that the scheme works, i'll test it with a sample message.'''
print(testing_message)

signatures = generate_signatures(flag)
print(signatures)

if verify_signature(flag, signatures):
    print("Signature Verified! Your turn. The functions that are allowed are: ")
else:
    print("Signature Verification Failed!")
    exit(0)

menu()

for _ in ['_', '__']:
    if _ == '_':
        print("Let's sign a message!")
    else:
        print("Now let's verify the signature!")
    response = ask() 

    if response == 1:
        message = str(input("Please enter the message to be signed: ")).encode('utf-8')

        signatures = generate_signatures(message)
        print(signatures)

    else: 
        message = str(input("Please enter the message to be verified: ")).encode('utf-8')
        signatures = list(map(int, input("Please enter the signature to be verified: ").split()))

        try:
            if len(signatures) == len(hashes) + 1:
                if verify_signature(message, signatures):
                    print("Signature Verified!")
                else:
                    print("Signature Verification Failed!")
                    exit(0)
        except:
            exit(0)
