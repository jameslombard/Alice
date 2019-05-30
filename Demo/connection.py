""" File for establishing a secure connection between two identity owners, A and B. """

import random
import pickle
import asyncio
import json
import re

""" This function creates a connection between two parties A and B. The function works from the point of view of 
A for both the connection request and response."""

import pprint

from indy import pool, ledger, wallet, did, crypto
from indy.error import IndyError, ErrorCode

from identity import ID, print_log, create_wallet

async def connect():

    Aname = input('Who u? ').strip()
    Bname = input('Who dem? ').strip()

    pickle_file = Aname +'.pickle'    

    await create_wallet(Aname)
    with open(pickle_file,'rb') as f:
            A = pickle.load(f)    
     
    AdidB = 'did_for_'+Bname
    AkeyB = 'key_for_'+Bname
    
    try:
        print_log('\n Generate and store unique pairwise pseudonymous DID and verkey in wallet\n')
        A[AdidB],A[AkeyB] = await did.create_and_store_my_did(A['wallet'], "{}") # Returns newly created steward DID and verkey
        # Save new version of A containing the did's and verkeys for the pairwise relationship:
        with open(pickle_file, 'wb') as f:
            pickle.dump(A, f)
            
    except IndyError as ex:
        if ex.error_code == ErrorCode.DidAlreadyExistsError:
            pass

    print_log(AdidB+': ',A[AdidB])
    print_log(AkeyB+': ',A[AkeyB])

    return A,Bname




