""" App for demonstrating the functionality of the Indy-SDK Libindy libraries for managing Self Soverign Identification
on the internet """

import time
import re
import asyncio
import json

import pprint

from indy import pool, ledger, wallet, did
from indy.error import IndyError, ErrorCode

# Required functions:

from identity import ID

from write_did_functions import print_log, pool_configuration, create_wallet, create_did_and_verkey, nym_request, query_did,cleanup
from save_schema_and_cred_def_functions import schema_request, credential_definition
from issue_credential_functions import prover_wallet_and_link_secret, offer_credential,request_credential, create_credential, process_and_store_credential
from negotiate_proof_functions import build_proof_request, fetch_credentials, create_proof, verify_proof
from secure_messenger import messenger

print_log('\n Welcome to Sovrin:\n')
print_log('\n ______________________________________________________________\n')
print_log('\n 1. Connect to the Sovrin nodes pool. \n')
print_log('\n 2. Sovrin Messenger. \n')
print_log('\n 3. Create/Load identity. \n')
print_log('\n 4. Create and Open wallet for identity. \n')
print_log('\n 5. Create DID and verkey for Identity. \n')
print_log('\n 6. Create Connection (Onboarding). \n')    
print_log('\n 7. Create NYM Request. \n')
print_log('\n 8. Create GET_NYM Request. \n')
print_log('\n 9. Replace Keys. \n')
print_log('\n 10. Get key for DID on the ledger.')
print_log('\n 11. Create Schema Request. \n')
print_log('\n 12. Create Get Schema Request. \n')
print_log('\n 13. Create Credential Definition. \n')
print_log('\n 14. Create Prover Link Secret. \n')
print_log('\n 15. Offer Credential. \n')
print_log('\n 16. Request Credential. \n')
print_log('\n 17. Create Credential. \n')
print_log('\n 18. Process and Store Credential. \n')
print_log('\n 19. Build Proof Request. \n')
print_log('\n 20. Fetch Credentials. \n')
print_log('\n 21. Create Proof. \n')
print_log('\n 22. Verify Proof. \n')
print_log('\n 23. Clean-up and Quit \n')
print_log('\n ______________________________________________________________\n')  

IP = '192.168.11.215' # Network IP address for server of Nodes pool
Sov = input('Please select:')

async def run():

    while True:

        # Pool config:
        if Sov==1:   

            pool_ = await pool_configuration(IP)

        # Send secure message:
        elif Sov==2:

            msg = None 
            await messenger(IP,msg)

        # Create ID: 
        elif Sov==3:

            await ID() # This step creates/loads and stores a new 

        # Create/Open wallet:
        elif Sov==4:

        # Create DID and Verkey for identity owner:
        elif Sov==5:

        # Create DID and Verkey for connection:
        elif Sov==6:

        # Create NYM request:
        elif Sov==7:

        # Create GET_NYM request:
        elif Sov==8:

        # Replace Keys:
        elif Sov==9:

        # Get Verkey for DID on the Ledger:
        elif Sov==10:

        # Create Schema Request:
        elif Sov==11:

        # Create Get Schema Request:    
        elif Sov==12: 

        # Create Credential Definition:
        elif Sov==13:

        # Create Prover Link Secret:
        elif Sov==14:

        # Offer Credential:
        elif Sov==15:

        # Request Credential:
        elif Sov==16:

        # Create Credential:
        elif Sov==17:

        # Process and Store Credential:
        elif Sov==18:

        # Build Proof Request:
        elif Sov==19:

        # Fetch Credentials:
        elif Sov==20:

        # Create Proof:
        elif Sov==21:

        # Verify Proof:
        elif Sov==22:
            
        # Close and Clean-up:
        else:

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
    time.sleep(1)  # waiting for libindy thread complete
    loop.close()

if __name__ == '__main__':
    main()