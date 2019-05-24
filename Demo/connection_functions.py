""" File for establishing a secure connection between two identity owners, A and B. """

import random
import pickle
import asyncio
import json

""" This function creates a connection between two parties A and B from both sides """

import pprint

from indy import pool, ledger, wallet, did, crypto
from indy.error import IndyError, ErrorCode

from identity import ID
from write_did_functions import print_log

async def connection():



async def create_connection(A,B):

    # Typically you would want to enter the name of B:
    # B_name = input("Enter the name of party B for making connection:")

    msg = '\n Creating connection between '+ A['name']+' and'+B['name']+'\n'
    print_log(msg)

    AdidB = 'did_for_'+B['name']
    AkeyB = 'key_for_'+B['name']
    
    (A[AdidB],A[AkeyB]) = await did.create_and_store_my_did(A['wallet'], "{}")
    return A,B

async def connection_request(pool_,A,B):

    # Generate 9 digit random number for nonce:
    a = str(random.randint(0,9))
    for x in range(9):
        a = a + str(random.randint(0,9))        

    AdidB = 'did_for_'+B['name']

    # Connection request is created, to be sent from A to B

    A['connection_request'] = {
        'did': A[AdidB],
        'nonce': a
    }
    return A,B

async def connection_response(pool_,B,A):
    
    # This step assumes that A has sent an A['connection request'] to B, 
    # which will be saved as B['connection_request]:
    
    # This step assumes that A has already onboarded B onto the ledger:

    # AkeyB_ledger = await did.key_for_did(pool_['pool'], B['wallet'], B['connection_request']['did'])
    # txt = A['name']+'_key_for_'+B['name']
    # B[txt] = AkeyB_ledger

    AdidB = 'did_for_'+B['name']
    AkeyB = 'key_for_'+B['name']
    BdidA = 'did_for_'+A['name']
    BkeyA = 'key_for_'+A['name']

    B['connection_response'] = json.dumps({
        'did': B[BdidA],
        'verkey': B[BkeyA],
        'nonce': A['connection_request']['nonce']
    })

    B['anoncrypted_connection_response'] = \
        await crypto.anon_crypt(A[AkeyB], B['connection_response'].encode('utf-8'))

async def auth_connection_response(A,B):

    AdidB = 'did_for_'+B['name']
    AkeyB = 'key_for_'+B['name']
    BdidA = 'did_for_'+A['name']
    BkeyA = 'key_for_'+A['name']

    # Send Anoncrypted connection response from B to A:

    A['anoncrypted_connection_response'] = B['anoncrypted_connection_response']

    # Anoncrypted connection response from A to B:

    A['connection_response'] = \
        json.loads((await crypto.anon_decrypt(A['wallet'], A[AkeyB],
                                              A['anoncrypted_connection_response'])).decode("utf-8"))

    # Authenticate by comparison of Nonce:
    assert A['connection_request']['nonce'] == A['connection_response']['nonce']

    # The next step is to send Nym to the Ledger:

