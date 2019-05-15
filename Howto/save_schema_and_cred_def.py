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
name = 'trust_anchor'
role = 'TRUST_ANCHOR'
trust_anchor = {'name': name}

async def write_schema_and_cred_def():
    try:
    # "Scaffolding:"

       # Pool config:

        pool_ = await pool_configuration(pool_name)
        print(pool_)
        print_log('\n2. Open ledger and get handle\n')           
        pool_['handle'] = await pool.open_pool_ledger(pool_['name'], None)
        
        # Create and open wallet:

        trust_anchor = await ID(name,role)
        trust_anchor = await create_wallet(trust_anchor)
        
        # Create did and verkey for steward and trust anchor:

        steward,trust_anchor = await create_did_and_verkey(trust_anchor)

        # write did and verkey to the ledger
        
        await nym_request(pool_,steward,trust_anchor) 

    # Step 3 code goes here.

        schema = await schema_request(pool_,steward,trust_anchor)

    # Step 4 code goes here.

        await credential_definition(pool_,trust_anchor,schema)

    # Clean-up:

        await cleanup(pool_,trust_anchor)
 
    except IndyError as e:
        print('Error occurred: %s' % e)

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(write_schema_and_cred_def())
    loop.close()

if __name__ == '__main__':
    main()