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
from Step4 import step4
from Step5 import step5
from pool_config import pool_configuration

# Get input from the user:
# pool_name = input("Please input the pool name:")
# wallet_id = input("Please input the wallet ID:")
# wallet_key = input("Please input the wallet Key:")

pool_name = 'pool'
wallet_id = 'wallet'
wallet_key = 'wallet_key'

async def write_nym_and_query_verkey():

    try:
        # Set protocol version 2 to work with Indy Node 1.4
     
        print_log('\n1. Create new pool ledger configuration to connect to ledger.\n')
        
        # Step 2 code goes here.
        pool_ = await pool_configuration(pool_name)
        print(pool_)

        print_log('\n2. Open ledger and get handle\n')

        pool_['handle'] = await pool.open_pool_ledger(pool_['name'], None)

        wallet_ = await step2(wallet_id, wallet_key)
        
        # Step 3 code goes here.

        steward, Trust_Anchor = await step3(wallet_)

        # Step 4 code goes here.

        await step4(pool_,wallet_,steward,Trust_Anchor)

        # Step 5 code goes here.

        await step5(wallet_,steward,Trust_Anchor,pool_)

    except IndyError as e:
        print('Error occurred: %s' % e)


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(write_nym_and_query_verkey())
    loop.close()


if __name__ == '__main__':
    main()