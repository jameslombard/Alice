"""
This sample is extensions of "write_schema_and_cred_def.py"

Shows how to issue a credential as a Trust Anchor which has created a Cred Definition
for an existing Schema.

After Trust Anchor has successfully created and stored a Cred Definition using Anonymous Credentials,
Prover's wallet is created and opened, and used to generate Prover's Master Secret.
After that, Trust Anchor generates Credential Offer for given Cred Definition, using Prover's DID
Prover uses Credential Offer to create Credential Request
Trust Anchor then uses Prover's Credential Request to issue a Credential.
Finally, Prover stores Credential in its wallet.
"""

import asyncio
import json
import pprint
import sys


from indy import pool, ledger, wallet, did, anoncreds, crypto
from indy.error import IndyError

from identity import ID
from write_did_functions import print_log, pool_configuration, create_wallet, create_did_and_verkey, nym_request, query_did,cleanup
from save_schema_and_cred_def_functions import schema_request, credential_definition
from issue_credential_functions import prover_wallet_and_link_secret, offer_credential, request_credential, create_credential, process_and_store_credential

pool_name = 'pool'

async def issue_credential():
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

        # Step 5: Rotate keys (skipped)

    # Step 3: Build and submit a schema request

        schema = await schema_request(pool_,steward)

    # Step 4: Create a Credential Definition:

        cred_def = await credential_definition(pool_,trust_anchor,schema)

        # Define the credential based on the credential definition:

        cred = {'def': cred_def}

        print_log('Credential:')
        pprint.pprint(cred)

# Step 3: Create prover ID and link-secret:

        print_log('\n12. Creating Prover\n')
        prover = await ID('prover')
        prover = await create_wallet(prover)
        prover = await create_did_and_verkey(prover)      
        prover = await prover_wallet_and_link_secret(prover)
        
        # Step 4 code goes here:

        cred = await offer_credential(trust_anchor,cred)
        
        print_log("Cred Definition")
        print(cred_def)

        cred = await request_credential(prover,cred)
        cred = await create_credential(trust_anchor, cred)
        cred = await process_and_store_credential(prover,cred)

        print_log('Credential:')
        pprint.pprint(cred)

    # Clean-up:

        await cleanup(pool_,trust_anchor)
        await cleanup(pool_,steward)
        await cleanup(pool_,prover)

    except IndyError as e:
        print('Error occurred: %s' % e)

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(issue_credential())
    loop.close()


if __name__ == '__main__':
    main()