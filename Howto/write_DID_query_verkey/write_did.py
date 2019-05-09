"""
Example demonstrating how to add DID with the role of Trust Anchor to ledger.
Uses seed to obtain Steward's DID which already exists on the ledger.
Then it generates new DID/Verkey pair for Trust Anchor.
Using Steward's DID, NYM transaction request is built to add Trust Anchor's DID and Verkey
on the ledger with the role of Trust Anchor.
Once the NYM is successfully written on the ledger, it generates new DID/Verkey pair that represents
a client, which are used to create GET_NYM request to query the ledger and confirm Trust Anchor's Verkey.
For the sake of simplicity, a single wallet is used. In the real world scenario, three different wallets
would be used and DIDs would be exchanged using some channel of communication
"""

import asyncio
import json

import pprint

from indy import pool, ledger, wallet, did
from indy.error import IndyError, ErrorCode

from src.utils import get_pool_genesis_txn_path, PROTOCOL_VERSION

from Step2 import step2, print_log 
from Step3 import step3

async def write_nym_and_query_verkey():

    try:
        # Set protocol version 2 to work with Indy Node 1.4
        await pool.set_protocol_version(PROTOCOL_VERSION)

        # Step 2 code goes here.

        # Pool name / wallet config
        pool_= {'name': 'pool'}
        genesis_file_path = get_pool_genesis_txn_path(pool_['name'])
        print(genesis_file_path)
        wallet_ = {'config' : json.dumps({"id": "wallet"}) ,
           'credentials' : json.dumps({"key": "wallet_key"})
        }

        await step2(pool_,wallet_,genesis_file_path)
        
        # Step 3 code goes here.

        await step3(wallet_)

        # Step 4 code goes here.


        # Step 5 code goes here.


    except IndyError as e:
        print('Error occurred: %s' % e)


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(write_nym_and_query_verkey())
    loop.close()


if __name__ == '__main__':
    main()