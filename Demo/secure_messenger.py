import asyncio
import time
import re
import socket

# Not used here, but will be required for the next steps
from indy import crypto, did, wallet
from identity import ID
from write_did_functions import print_log, create_wallet, create_did_and_verkey

async def messenger(IP,msg,call):

    me,them = await init()

    print_log('\n The Messenger recognizes the following commands:\n')
    print('prep: Sender prepares a message.')
    print('send: Sender server listens for client response.')
    print('receive: Receiver client connects to server and message is sent.')
    print('read: receiver reads the message.')
    print('Connection Request: Send a connection request.')
    print('Connection response: Send a connection response.')
    print('quit: Quit the messenger.')
    
    crypt = 0 # Indicates whether message is to be encrypted (default : NO)

    while True:

        argv = input('> ').strip().split(' ')
        cmd = argv[0].lower()
        rest = ' '.join(argv[1:])

        if re.match(cmd, 'prep'):
            msg = await prep(me,them,rest,crypt)

        elif re.match(cmd, 'send'):
            await server(msg)

        elif re.match(cmd, 'receive'):
            await client(IP)

        elif re.match(cmd, 'read'): 
            await read(me,crypt)

        elif call == 0 # Connection request
            await request(msg)

        elif call == 1 # Connection response
            await response(msg)

        elif re.match(cmd, 'quit'):
            break
        else:
            print('Huh?')

async def crypt():

    their = input("Other party's Verkey? ").strip()
    them = {'Verkey': their}
    return them

async def init():

    # 1. Create Wallet and Get Wallet Handle

    me = input('Who dis?')
    pickle_file = me +'.pickle'

    try:
        with open(pickle_file,'rb') as f:
            name = pickle.load(f)
    except (FileNotFoundError) as e:
        print('Sovrin insists...')
        await ID()
        with open(pickle_file,'rb') as f:
            name = pickle.load(f)    

    print('wallet = %s' % me['wallet'])
    me = await create_did_and_verkey(me)
    them = {}

    return me,them

async def prep(me,them,msg,crypt):

    if crypt == 0:
        encrypted = bytes(msg, 'utf-8')
    else:
        msg = bytes(msg, "utf-8")
        encrypted = await crypto.auth_crypt(me['wallet'],me['verkey'],them['verkey'], msg)
        # encrypted = await crypto.anon_crypt(their_vk, msg)
        print('encrypted = %s' % repr(encrypted))

    with open('message.dat', 'wb') as f:
        f.write(encrypted)
    print('prepping %s' % msg)

    return encrypted

async def read(me,crypt):

    with open('message.dat', 'rb') as f:
        encrypted = f.read()
        print(repr(encrypted))

    if crypt == 1: 
        decrypted = await crypto.auth_decrypt(me['wallet'],me['verkey'], encrypted)
        # decrypted = await crypto.anon_decrypt(wallet_handle, my_vk, encrypted)
        print(decrypted)
        message = decrypted[1].decode('utf-8')
    else:
        message = encrypted.decode('utf-8')    

    print(message)
    print(type(message))

async def request():

async def response():

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