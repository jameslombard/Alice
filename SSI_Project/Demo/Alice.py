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

from identity import ID, print_log, create_wallet, did_and_verkey

from write_did_functions import pool_configuration, nym_request, query_did, replace_keys, get_verkey, cleanup, delete_wallet
from connection import connect
from secure_messenger import messenger

# from save_schema_and_cred_def_functions import schema_request, credential_definition
# from issue_credential_functionls import prover_wallet_and_link_secret, offer_credential,request_credential, create_credential, process_and_store_credential
# from negotiate_proof_functions import build_proof_request, fetch_credentials, create_proof, verify_proof

IP = 'JamesL'             # Network IP address for server of Nodes pool
clientname = 'JamesL'     # Ip Address for messenger client (receiver)

async def run():

    while True:
        print_log('\n')
        print_log('Welcome to Sovrin:')
        print_log(' ______________________________________________________________')
        print_log('1. Connect to the Sovrin nodes pool.')
        print_log('2. Sovrin Messenger.')
        print_log('3. Create/Load identity.')
        print_log('4. Create/Open wallet for identity.')
        print_log('5. Create/Get DID and verkey for Identity (Public DID).')            
        print_log('6. Create Connection (Private DID).')             
        print_log('7. Create NYM Request.')
        print_log('8. Query DID (GET_NYM Request).')
        print_log('9. Replace Keys.')
        print_log('10. Get Verkey for DID on the ledger.')
        # print_log('11. Create Schema Request.')
        # print_log('12. Create Get Schema Request.')
        # print_log('13. Create Credential Definition.')
        # print_log('14. Create Prover Link Secret.')
        # print_log('15. Offer Credential.')
        # print_log('16. Request Credential.')
        # print_log('17. Create Credential.')
        # print_log('18. Process and Store Credential.')
        # print_log('19. Build Proof Request.')
        # print_log('20. Fetch Credentials.')
        # print_log('21. Create Proof.')
        # print_log('22. Verify Proof.')
        print_log('11. Clean-up.')
        print_log('12. Delete Identity Owner Wallet.')    
        print_log('13. Quit.')
        print_log(' ______________________________________________________________')  

        Sov = input('Please select:').strip()

        # Pool config:

        if Sov=='1':   

            await pool_configuration(IP)

        # Send secure message:
        elif Sov=='2':

            await messenger(clientname)

        # Create ID: 
        elif Sov=='3':

            await ID() # This step creates/loads and stores a new user ID

        # Create/Open wallet:
        elif Sov=='4':

            await create_wallet()

        # Create DID and Verkey for identity owner:
        elif Sov=='5':

            await did_and_verkey()            

        # Create connection:
        elif Sov=='6':

            await connect()

        # Create NYM request:
        elif Sov=='7':

            await nym_request(IP)

        # Create GET_NYM request:
        elif Sov=='8':

            await query_did(IP)

        # Replace Keys:
        elif Sov=='9':

            await replace_keys(IP)

        # Get Verkey for DID on the Ledger:
        elif Sov=='10':

            await get_verkey(IP)

        # # Create Schema Request:
        # elif Sov==11:

        # # Create Get Schema Request:    
        # elif Sov==12: 

        # # Create Credential Definition:
        # elif Sov==13:

        # # Create Prover Link Secret:
        # elif Sov==14:

        # # Offer Credential:
        # elif Sov==15:

        # # Request Credential:
        # elif Sov==16:

        # # Create Credential:
        # elif Sov==17:

        # # Process and Store Credential:
        # elif Sov==18:

        # # Build Proof Request:
        # elif Sov==19:

        # # Fetch Credentials:
        # elif Sov==20:

        # # Create Proof:
        # elif Sov==21:

        # # Verify Proof:
        # elif Sov==22:
            
        # Close and Clean-up:
        elif Sov == '11':

            await cleanup(IP)

        elif Sov == '12':

            await delete_wallet()

        elif Sov == '13':

            await cleanup(IP)
            break

        else:
            print('Huh?')

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
    time.sleep(1)  # waiting for libindy thread complete
    loop.close()

# Is this file being run directly or is it being imported?
if __name__ == '__main__': 
    main()