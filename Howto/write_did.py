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

# Define Pool:
pool_name = 'pool'

async def write_nym_and_query_verkey():

    try:
           
        # Step 1: Pool configuration

        pool_ = await pool_configuration(pool_name)
      
        # Step 2: Create and open wallets:

        steward = await ID('steward')
        steward = await create_wallet(steward)
        trust_anchor = await ID('trust_anchor')
        trust_anchor = await create_wallet(trust_anchor)
        
        # Step 3: Create did and verkey

        steward = await create_did_and_verkey(steward)
        trust_anchor = await create_did_and_verkey(trust_anchor)

        # Step 4: NYM request:

        nymrole = 'TRUST_ANCHOR'
        await nym_request(pool_,steward,trust_anchor,nymrole)

        # Step 5: Query DID (GET_NYM request):

        print_log('\n9. Generating and storing DID and verkey representing a Client '
                    'that wants to obtain Trust Anchor Verkey\n')

        client = await ID('client')
        client = await create_wallet(client)
        client['did'],client['verkey'] = await did.create_and_store_my_did(client['wallet'], "{}")

        print_log('Client DID: ', client['did'])
        print_log('Client Verkey: ', client['verkey'])

        get_nym_response = await query_did(pool_,steward,trust_anchor)

        # See whether we received the same info that we wrote the ledger in step 4.
        
        print_log('\n12. Comparing Trust Anchor verkey as written by Steward and as retrieved in GET_NYM '
                    'response submitted by Client\n')

        print_log('Written by Steward: ', trust_anchor['verkey'])
        verkey_from_ledger = json.loads(get_nym_response['result']['data'])['verkey']
        print_log('Queried from ledger: ', verkey_from_ledger)
        print_log('Matching: ', verkey_from_ledger == trust_anchor['verkey'])
        
        # Close and delete pool and wallets:

        await cleanup(pool_,trust_anchor)
        await cleanup(pool_,steward)
        await cleanup(pool_,client)

    except IndyError as e:
        print('Error occurred: %s' % e)

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(write_nym_and_query_verkey())
    loop.close()

if __name__ == '__main__':
    main()