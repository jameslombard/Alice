"""
Example demonstrating Proof Verification.
First Issuer creates Claim Definition for existing Schema.
After that, it issues a Claim to Prover (as in issue_credential.py example)
Once Prover has successfully stored its Claim, it uses Proof Request that he
received, to get Claims which satisfy the Proof Request from his wallet.
Prover uses the output to create Proof, using its Master Secret.
After that, Proof is verified against the Proof Request
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

async def proof_negotiation():
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

        # Step 3 code goes here.

        # Step 4 code goes here.

        # Step 5 code goes here.

    except IndyError as e:
        print('Error occurred: %s' % e)

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(proof_negotiation())
    loop.close()

if __name__ == '__main__':
    main()