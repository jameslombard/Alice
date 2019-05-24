import asyncio
import time
import re
import socket

# Not used here, but will be required for the next steps
from indy import crypto, did, wallet
from identity import ID
from write_did_functions import print_log, create_wallet, create_did_and_verkey

async def messenger(IP):

    me,them = await init()

    print_log('\n The Messenger recognizes the following commands:\n')
    print('prep: Sender prepares a message.')
    print('send: Sender server listens for client response.')
    print('receive: Receiver client connects to server and message is sent.')
    print('read: receiver reads the message.')

    while True:

        argv = input('> ').strip().split(' ')
        cmd = argv[0].lower()
        rest = ' '.join(argv[1:])
        if re.match(cmd, 'prep'):
            # Call prep
            msg = await prep(me,them,rest)
            # Call read
        elif re.match(cmd, 'send'):
            # Call send
            await server(msg)
        elif re.match(cmd, 'receive'):
            await client(IP)
        elif re.match(cmd, 'read'):            
            await read(me)
        elif re.match(cmd, 'quit'):
            break
        else:
            print('Huh?')

async def init():

    # 1. Create Wallet and Get Wallet Handle

    me = await ID()
    me = await create_wallet(me)

    print('wallet = %s' % me['wallet'])
    me = await create_did_and_verkey(me)
    their = input("Other party's DID and verkey? ").strip().split(' ')
    them = {'did': their[0] ,
            'verkey': their[1]}

    return me,them

async def prep(me,them,msg):

    msg = bytes(msg, "utf-8")
    encrypted = await crypto.auth_crypt(me['wallet'],me['verkey'],them['verkey'], msg)
    # encrypted = await crypto.anon_crypt(their_vk, msg)
    print('encrypted = %s' % repr(encrypted))
    with open('message.dat', 'wb') as f:
        f.write(encrypted)
    print('prepping %s' % msg)
    return(encrypted)

async def read(me):

    with open('message.dat', 'rb') as f:
        encrypted = f.read()
        print(repr(encrypted))
    decrypted = await crypto.auth_decrypt(me['wallet'],me['verkey'], encrypted)
    # decrypted = await crypto.anon_decrypt(wallet_handle, my_vk, encrypted)
    print(decrypted)
    message = decrypted[1].decode('utf-8')
    print(message)
    print(type(message))

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
    host = IP                       # Ip address that the TCPServer  is there
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