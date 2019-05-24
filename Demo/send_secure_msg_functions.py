
import asyncio
import time
import re

# Not used here, but will be required for the next steps
from indy import crypto, did, wallet
from identity import ID
from write_did_functions import create_wallet, create_did_and_verkey

async def init():
    me = await ID()
    
    # 1. Create Wallet and Get Wallet Handle

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

        
async def read(me):
    with open('message.dat', 'rb') as f:
        encrypted = f.read()
    decrypted = await crypto.auth_decrypt(me['wallet'],me['verkey'], encrypted)
    # decrypted = await crypto.anon_decrypt(wallet_handle, my_vk, encrypted)
    print(decrypted)