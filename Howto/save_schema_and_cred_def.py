"""
Example demonstrating how to write Schema and Cred Definition on the ledger
As a setup, Steward (already on the ledger) adds Trust Anchor to the ledger.
After that, Steward builds the SCHEMA request to add new schema to the ledger.
Once that succeeds, Trust Anchor uses anonymous credentials to issue and store
claim definition for the Schema added by Steward.
"""
import asyncio
import json
import pprint

from indy import pool, ledger, wallet, did, anoncreds
from indy.error import ErrorCode, IndyError
from identity import ID

from write_did_functions import print_log, pool_configuration, create_wallet, create_did_and_verkey, nym_request, query_did,cleanup
from save_schema_and_cred_def_functions import schema_request, credential_definition

pool_name = 'pool'

async def write_schema_and_cred_def():
    try:
    # "Scaffolding:"

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

        nymrole = 'TRUST_ANCHOR' # Define role for NYM transaction
        await nym_request(pool_,steward,trust_anchor,nymrole)

    # Step 3: Build and submit a schema request

        schema = await schema_request(pool_,steward)

    # Step 4 code goes here.

        cred_def = await credential_definition(pool_,trust_anchor,schema)
        cred = {'def': cred_def}
        
    # Clean-up:

        await cleanup(pool_,trust_anchor)
        await cleanup(pool_,steward)
 
    except IndyError as e:
        print('Error occurred: %s' % e)

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(write_schema_and_cred_def())
    loop.close()

if __name__ == '__main__':
    main()