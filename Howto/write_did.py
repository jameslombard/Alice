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

from identity import ID

from write_did_functions import pool_configuration, restart_pool,  print_log, create_wallet, create_did_and_verkey, nym_request, query_did, cleanup

# Get input from the user:
# pool_name = input("Please input the pool name:")
# wallet_id = input("Please input the wallet ID:")
# wallet_key = input("Please input the wallet Key:")

pool_name = 'pool'
name = 'trust_anchor'
role = 'TRUST_ANCHOR'
trust_anchor = {'name': name}

async def write_nym_and_query_verkey():

    try:
     
        print_log('\n1. Create new pool ledger configuration to connect to ledger.\n')
        
        # Step 1: Pool configuration

        pool_ = await pool_configuration(pool_name)

        print(pool_)
        print_log('\n2. Open ledger and get handle\n')
            
        pool_['handle'] = await pool.open_pool_ledger(pool_['name'], None)
        
        # Step 2: Create and open wallet:

        trust_anchor = await ID(name,role)
        trust_anchor = await create_wallet(trust_anchor)
        
        # Step 3 code goes here:

        steward,trust_anchor = await create_did_and_verkey(trust_anchor)

        # Step 4 code goes here:

        await nym_request(pool_,steward,trust_anchor)

        # Step 5 code goes here:

        await query_did(pool_,steward,trust_anchor)

        # Close and delete pool and wallet:

        await cleanup(pool_,trust_anchor)

    except IndyError as e:
        print('Error occurred: %s' % e)


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(write_nym_and_query_verkey())
    loop.close()


if __name__ == '__main__':
    main()