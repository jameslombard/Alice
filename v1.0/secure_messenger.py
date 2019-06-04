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
from write_did_functions import print_log, create_wallet, did_and_verkey
from connection import connect

async def messenger(clientname,*args):

    if not args:
        A,Bname = await connect()
    else:
        for arg in args:
            Aname = arg
            A,Bname = await connect(Aname)

    while True:

        print('\n')
        print('Is this an existing secure pairwise connection?')
        print('1. Yes')
        print('2. No')

        crypt = (input('Please select a number:'))

        if crypt == '1' or crypt == '2':
            break
        else:
            print('Huh?')

    crypt = int(crypt)

    print_log('\n The Messenger recognizes the following commands:\n')

    print('prep: Sender prepares a text message.')
    print('send: Sender server listens for client response.')
    print('receive: Receiver client connects to server.')
    print('read: receiver reads the message.')
    print('request: Sender prepares a connection request.')
    print('response: Sender prepares a connection response.')
    print('verinym: Sender prepares a verinym request.')
    print('quit:Quit the messenger.')
    
    while True:

        argv = input('> ').strip().split(' ')
        cmd = argv[0].lower()
        rest = ' '.join(argv[1:])

        if re.match(cmd, 'prep'):
            msg = await prep(A,Bname,rest,crypt)

        elif re.match(cmd, 'send'):
            await server(msg)

        elif re.match(cmd, 'receive'):
            await client(clientname)

        elif re.match(cmd, 'read'): 
            msg = await read(A,Bname,crypt)

        elif re.match(cmd, 'save'):
            await save(A,Bname,msg)

        elif re.match(cmd, 'request'): # Connection request

            msg = await request(A,Bname)
            crypt = 2
            msg = await prep(A,Bname,msg,crypt)

        elif re.match(cmd, 'response'): # Connection response

            msg = await response(A,Bname)
            crypt = 1
            msg = await prep(A,Bname,msg,crypt)

        elif re.match(cmd, 'verinym'): # Request a verinym
            msg = await verinym_request(A,Bname)
            crypt = 1
            msg = await prep(A,Bname,msg,crypt)

        elif re.match(cmd, 'quit'):
            return A['name']
            break
        else:
            print('Huh?')

async def prep(A,Bname,msg,crypt):

    AkeyB = 'key_for_'+Bname
    BkeyA = 'key_from_'+Bname

    if crypt == 2:
        encrypted = bytes(msg, 'utf-8')
    else:
        msg = bytes(msg, "utf-8")
        try:
            encrypted = await crypto.auth_crypt(A['wallet'],A[AkeyB],A[BkeyA], msg)
            # encrypted = await crypto.anon_crypt(their_vk, msg)
            print()
            print('encrypted = %s' % repr(encrypted))
            print()
        except KeyError as e:
            print_log('Make sure you have retrieved the receivers Verkey from the ledger.')
            print()
            return

    with open('message.dat', 'wb') as f:
        f.write(encrypted)
        
    print('prepping %s' % msg)
    return encrypted

async def read(A,Bname,crypt):

    AkeyB = 'key_for_'+Bname 

    with open('message.dat', 'rb') as f:
        encrypted = f.read()

    if crypt == 1: 
        decrypted = await crypto.auth_decrypt(A['wallet'],A[AkeyB], encrypted)
        # decrypted = await crypto.anon_decrypt(wallet_handle, my_vk, encrypted)
        print()
        print(decrypted)
        print()
        verkey = decrypted[0]
        print('Sender verkey:',verkey)
        print()
        message = decrypted[1].decode('utf-8')
        
    else:
        message = encrypted.decode('utf-8')    
        decrypted = message

    print(message)
    return decrypted

async def save(A,Bname,msg):

    BdidA = 'did_from_'+Bname
    BkeyA = 'key_from_'+Bname
    Bdid = Bname+'_did'
    Bkey = Bname+'_key'

    pickle_file = A['name']+'.pickle'

    # Function for saving a received message:
    while True:
        print('Save as:')
        print ('1. Connection request (DID for '+Bname+')')
        print ('2. Connection response (DID and Verkey from '+Bname+')')
        print ('3. Verinym request ('+Bname+' DID and Verkey')

        sel = input('Please select a number:')

        if sel == '1' or sel == '2' or sel == '3':
            break
        else:
            print('Huh?')

    sel = int(sel)
    if sel == 1: # Connection request
        
        connection_request = json.loads(msg)
        A[BdidA] = connection_request['did']
        A['nonce'] = {Bname : connection_request['nonce']}
        print()
        print('Connection request information saved successfully.')

    elif sel == 2: # Connection response

        connection_response = json.loads(msg[1].decode('utf-8'))
        A[BdidA] = connection_response['did']
        A[BkeyA] = connection_response['verkey']
        A['nonce'] = {Bname: connection_response['nonce']}
        initial_request = json.loads(A['connection_requests'][Bname])

        if initial_request['nonce'] == A['nonce'][Bname]:
            print_log('\n The Response is Nonce Authenticated \n')
                print()
            print('Connection response information is saved successfully.')
        else:
            print('The Nonce in the Response does not match the Nonce in the Request')

    else: # Verinym
        verinym_request = json.loads(msg[1].decode('utf-8'))
        A[Bdid] = verinym_request['did']
        A[Bkey] = verinym_request['verkey']

        if A[BkeyA] == msg[0]:
            print('Message sender verkey matches connection verkey:')

            print_log('Sender Verkey: ',msg[0])
            print_log(Bname+' Verkey: ',A[BkeyA])             
            print()
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

    pickle_file = A['name']+'.pickle'

    with open(pickle_file,'rb') as f:
        A = pickle.load(f)   

    A['did_info'] = json.dumps({
        'did': A['did'],
        'verkey': A['verkey']})

    with open (pickle_file, 'wb') as f:
        pickle.dump(A, f)

    msg = A['did_info']
    return msg

async def server(msg): # Sender of message:

    port = 50000                    # Reserve a port for your service every new transfer wants a new port or you must wait.
    s = socket.socket()             # Create a socket object
    host = ""                       # Get local machine name

    # Allow for address re-use
    # ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind((host, port))            # Bind to the port
    s.listen(5)                     # Now wait for client connection.
    print('Server listening...')

    conn, addr = s.accept()         # Establish connection with client.
    print('Got connection from', addr)

    print('Sending message...')     
    conn.sendall(msg)
    print('Message sent.')
    conn.close()


async def client(clientname): # Receiver of message:

    s = socket.socket()             # Create a socket object

    host = socket.gethostbyname(clientname)  # Ip address of the TCPServer 
    port = 50000                        # Reserve a port for your service every new transfer wants a new port or you must wait.
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