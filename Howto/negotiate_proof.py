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
import sys

from indy import pool, ledger, wallet, did, anoncreds, crypto
from indy.error import IndyError

from identity import ID
from write_did_functions import print_log, pool_configuration, create_wallet, create_did_and_verkey, nym_request, query_did,cleanup

from save_schema_and_cred_def_functions import schema_request, credential_definition
from issue_credential_functions import prover_wallet_and_link_secret, offer_credential,request_credential, create_credential, process_and_store_credential
from negotiate_proof_functions import build_proof_request, fetch_credentials, create_proof, verify_proof

pool_name = 'pool'

async def proof_negotiation():
    try:

    # "Scaffolding:"

            # Step 1: Pool configuration

        pool_ = await pool_configuration(pool_name)
      
            # Step 2: Create and open wallets:

        steward = await ID('steward')
        steward = await create_wallet(steward)
        issuer = await ID('issuer')
        issuer = await create_wallet(issuer)
        
            # Step 3: Create did and verkey

        steward = await create_did_and_verkey(steward)
        issuer = await create_did_and_verkey(issuer)

            # Step 4: NYM request:

        nymrole = 'TRUST_ANCHOR' # Define role for NYM transaction
        await nym_request(pool_,steward,issuer,nymrole)

            # Step 5: Rotate keys (skipped):

        # Step 3: Build and submit a schema request

        schema = await schema_request(pool_,steward)

        # Step 4: Create a Credential Definition

        cred_def = await credential_definition(pool_,issuer,schema)

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

        cred = await offer_credential(issuer,cred)
        
        print_log("Cred Definition")
        print(cred_def)

        cred = await request_credential(prover,cred)
        cred = await create_credential(issuer, cred)
        cred = await process_and_store_credential(prover,cred)

        # Step 3 code goes here.

        proof_req = await build_proof_request(issuer,schema)
        prover,proof_req = await fetch_credentials(prover,proof_req)

        # Step 4 code goes here.

        proof,prover = await create_proof(proof_req,prover,cred,schema)

        # Step 5 code goes here.

        await verify_proof(proof_req,proof,cred,schema)

    # Clean-up:

        await cleanup(pool_,issuer)
        await cleanup(pool_,steward)
        await cleanup(pool_,prover)

    except IndyError as e:
        print('Error occurred: %s' % e)

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(proof_negotiation())
    loop.close()

if __name__ == '__main__':
    main()
