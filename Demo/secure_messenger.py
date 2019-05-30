import asyncio
import time
import re
import socket
import json
import pickle
import random

# Not used here, but will be required for the next steps
from indy import crypto, did, wallet
from identity import ID
from write_did_functions import print_log, create_wallet, create_did_and_verkey
from connection import connect

async def messenger(IP):

    A,Bname = await connect()

    print_log('\n The Messenger recognizes the following commands:\n')
    print('crypt: Activate message encryption.')
    print('prep: Sender prepares a text message.')
    print('send: Sender server listens for client response.')
    print('receive: Receiver client connects to server and message is sent.')
    print('read: receiver reads the message.')
    print('connection request: Sender prepares a connection request.')
    print('connection response: Sender prepares a connection response.')
    print('verinym request: Sender prepares a verinym request.')
    print('quit: Quit the messenger.')
    
    crypt = 0 # Indicates whether message is to be encrypted (default : NO)

    while True:

        argv = input('> ').strip().split(' ')
        cmd = argv[0].lower()
        rest = ' '.join(argv[1:])

        if re.match(cmd, 'crypt'):
            crypt = await activate_crypto(A,Bname)
        if re.match(cmd, 'prep'):
            msg = await prep(A,Bname,rest,crypt)

        elif re.match(cmd, 'send'):
            await server(msg)

        elif re.match(cmd, 'receive'):
            await client(IP)

        elif re.match(cmd, 'read'): 
            msg = await read(A,crypt)

        elif re.match(cmd, 'save'):
            await save(A,Bname,msg)

        elif re.match(cmd, 'connection request'): # Connection request
            msg = await request(A,Bname)
            crypt = 0
            msg = await prep(A,Bname,msg,crypt)
        elif re.match(cmd, 'connection response'): # Connection response
            msg = await response(A,Bname)
            crypt = 1
            msg = await prep(A,Bname,msg,crypt)
        elif re.match(cmd, 'verinym request'): # Request a verinym
            msg = await verinym_request(A,Bname)
            crypt = 1
            msg = await prep(A,Bname,msg,crypt)
        elif re.match(cmd, 'quit'):
            break
        else:
            print('Huh?')

async def activate_crypto(A,Bname):

    crypt = 0

    BkeyA = 'key_from_'+Bname

    if BkeyA not in A:
        print('Cannot activate Cryptography.')
        print('Public key required')
    else:
        crypt = 1

    return crypt

async def prep(A,Bname,msg,crypt):

    BkeyA = 'key_from_'+Bname

    if crypt == 0:
        encrypted = bytes(msg, 'utf-8')
    else:
        msg = bytes(msg, "utf-8")
        encrypted = await crypto.auth_crypt(A['wallet'],A['verkey'],A[BkeyA], msg)
        # encrypted = await crypto.anon_crypt(their_vk, msg)
        print('encrypted = %s' % repr(encrypted))

    with open('message.dat', 'wb') as f:
        f.write(encrypted)
    print('prepping %s' % msg)

    return encrypted

async def read(A,crypt):

    with open('message.dat', 'rb') as f:
        encrypted = f.read()
        print(repr(encrypted))

    if crypt == 1: 
        decrypted = await crypto.auth_decrypt(A['wallet'],A['verkey'], encrypted)
        # decrypted = await crypto.anon_decrypt(wallet_handle, my_vk, encrypted)
        print(decrypted)
        verkey = decrypted[0].decode('utf-8')
        print('Sender verkey:',verkey)
        message = decrypted[1].decode('utf-8')
        
    else:
        message = encrypted.decode('utf-8')    
        decrypted = message

    print('Message:', message)
    return decrypted

async def save(A,Bname,msg):

    BdidA = 'did_from_'+Bname
    BkeyA = 'key_from_'+Bname
    Bdid = Bname+'_did'
    Bkey = Bname+'_key'

    pickle_file = A['name']+'.pickle'

    # Function for saving a received message:
    print('Save as:')
    print ('1. Connection request:')
    print ('2. Connection response')
    print ('3. Verinym request')

    sel = input('Please select a number:')
    if sel == 1: # Connection request
        
        connection_request = json.loads(msg[1].decode('utf-8'))
        A[BdidA] = connection_request['did']
        A['nonce'][Bname] = connection_request['nonce']
        print('Connection request information saved successfully.')

    elif sel == 2: # Connection response

        connection_response = json.loads(msg[1].decode('utf-8'))
        A[BdidA] = connection_response['did']
        A[BkeyA] = connection_response['verkey']
        A['nonce'][Bname] = connection_response['nonce']
        initial_request = json.loads(A['connection_requests'][Bname])

        if initial_request['nonce'] == A['nonce'][Bname]:
            print('The Response is Nonce Authenticated')
            print('Connection response information is saved successfully.')
        else:
            print('The Nonce in the Response does not match the Nonce in the Request')

    else: # Verinym
        verinym_request = json.loads(msg[1].decode('utf-8'))
        A[Bdid] = verinym_request['did']
        A[Bkey] = verinym_request['verkey']

        if A[BkeyA] == msg[0].decode('utf-8'):
            print('Message sender verkey matches connection verkey.')
            print('Verinym request information is saved successfully')

    with open (pickle_file, 'wb') as f:
        pickle.dump(A, f)

async def request(A,Bname):

    pickle_file = A['name']+'.pickle'

    # Generate 9 digit random number for nonce:
    a = str(random.randint(0,9))
    for x in range(9):
        a = a + str(random.randint(0,9))        

    AdidB = 'did_for_'+Bname

    # Connection request is created, to be sent from A to B

    A['connection_requests'] = {
        Bname : 
        json.dumps({'did': A[AdidB],
        'nonce': a})
        }

    msg = A['connection_requests'][Bname]

    # Save new version of A containing connection request.
    with open (pickle_file, 'wb') as f:
        pickle.dump(A, f)

    return msg

async def response(A,Bname):

        # This step assumes that a connection request has already been accepted and NYM request
    # submitted for the responder.

    # AkeyB_ledger = await did.key_for_did(pool_['pool'], B['wallet'], B['connection_request']['did'])
    # txt = A['name']+'_key_for_'+B['name']
    # B[txt] = AkeyB_ledger

    pickle_file = A['name']+'.pickle'

    AdidB = 'did_for_'+Bname
    AkeyB = 'key_for_'+Bname

    A['connection_responses'] = {Bname:
        json.dumps({
        'did': A[AdidB],
        'verkey': A[AkeyB],
        'nonce': A['nonce'][Bname]})
        }

    msg = A['connection_responses'][Bname]

    # Save new version of A containing connection response.
    with open (pickle_file, 'wb') as f:
        pickle.dump(A, f)

    return msg

async def verinym_request(A,Bname):

    await ID(A['name'])
    with open(pickle_file,'rb') as f:
            A = pickle.load(f)   

    A['did_info'] = json.dumps({
        'did': A['did'],
        'verkey': A['verkey']})

    with open (pickle_file, 'wb') as f:
        pickle.dump(A, f)

    msg = A['did_info']

async def server(msg): # Sender of message:

    port = 50000                    # Reserve a port for your service every new transfer wants a new port or you must wait.
    s = socket.socket()             # Create a socket object
    host = ""                       # Get local machine name
    s.bind((host, port))            # Bind to the port
    s.listen(5)                     # Now wait for client connection.
    print('Server listening...')

    conn, addr = s.accept()         # Establish connection with client.
    print('Got connection from', addr)

    print('Sending message...')     
    conn.sendall(msg)
    print('Message sent.')
    conn.close()
        
async def client(IP): # Receiver of message:

    s = socket.socket()             # Create a socket object
    host = IP                       # Ip address of the TCPServer 
    port = 50000                    # Reserve a port for your service every new transfer wants a new port or you must wait.
    s.connect((host, port))
    print("Connected to the server")
    
    f = open('message.dat','wb') #The file you want to transfer must be in the same folder as this file.
    while True:
        data = s.recv(1024)
        if not data:
            break
        # write bytes on file
        f.write(data)
    f.close() 

    # Close the connection:    
    s.close()
    print('connection closed')