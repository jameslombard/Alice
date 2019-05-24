""" App for demonstrating the functionality of the Indy-SDK Libindy libraries for managing Self Soverign Identification
on the internet """

import asyncio
import json

import pprint

from indy import pool, ledger, wallet, did
from indy.error import IndyError, ErrorCode

# Required functions:

from identity import ID

from identity import ID
from write_did_functions import print_log, pool_configuration, create_wallet, create_did_and_verkey, nym_request, query_did,cleanup

from save_schema_and_cred_def_functions import schema_request, credential_definition
from issue_credential_functions import prover_wallet_and_link_secret, offer_credential,request_credential, create_credential, process_and_store_credential
from negotiate_proof_functions import build_proof_request, fetch_credentials, create_proof, verify_proof

print_log('\n Please specify by entering the appropriate number:\n')
print_log('\n 1. Connect to the pool of genesis nodes on the ledger. \n')
print_log('\n 2. Create identity owner. \n')
print_log('\n 3. Create wallet for identity owner. \n')
print_log('\n 4. Create DID and verkey for Identity or Connection. \n')
print_log('\n 5. Create NYM_REQUEST. \n')
print_log('\n 6. Query DID. \n')
print_log('\n 7. Replace Keys. \n')
print_log('\n 8. Create identity owner. \n')
print_log('\n 9. Create identity owner. \n')
print_log('\n 10. Create identity owner. \n')
print_log('\n 11. Create identity owner. \n')
print_log('\n 12. Create identity owner. \n')
print_log('\n 13. Create identity owner. \n')
print_log('\n 14. Create identity owner. \n')
print_log('\n 15. Create identity owner. \n')
print_log('\n 16. Create identity owner. \n')
print_log('\n 17. Quit \n')

    



async def run():












    if __name__ == '__main__':
    run_coroutine(run)
    time.sleep(1)  # FIXME waiting for libindy thread complete