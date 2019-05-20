   
import asyncio
import json
import pprint

from indy.error import IndyError, ErrorCode
from indy import wallet, anoncreds

from write_did_functions import print_log, create_wallet

async def prover_wallet_and_link_secret(prover):   

        # prover = await create_wallet(prover)
        # prover['did'] = 'VsKV7grR1BUE29mG2Fm2kX'
        # prover['wallet'] = await wallet.open_wallet(prover['wallet_config'], prover['wallet_credentials'])

        # 13.
        print_log('\n13. Prover is creating Link Secret\n')
        prover['link_secret_name'] = 'link_secret'
        prover['link_secret_id'] = await anoncreds.prover_create_master_secret(prover['wallet'],
                                                                     prover['link_secret_name'])  
        
        return(prover)

# 'Three steps embodying a negotiation pattern that is used in many Indy interactions (proving)':
# Either party can begin; the other party acknowledges and accepts--or makes a counter proposal. 
# In the case of a counter proposal, a new negotiation cycle begins; 
# in the simpler case, the negotiation is concluded successfully. 
# Negotiation could be used during credential issuance to negotiate a change to a credential 
# (e.g., to correct a typo or to ask an issuer to include or omit a piece of data that they 
# didn't initially propose); however, we don't cover that advanced workflow here.

async def offer_credential(issuer,cred):
        # 14. Issuer creates offer:

        print_log('\n14. Issuer (Trust Anchor) is creating a Credential Offer for Prover\n')

        cred['offer_json'] = await anoncreds.issuer_create_credential_offer(wallet_handle=issuer['wallet'], 
                                                                            cred_def_id=cred['def']['id'])
        print_log('Credential Offer: ')
        pprint.pprint(json.loads(cred['offer_json']))
        return cred

async def request_credential(prover,cred):

        # 15. Prover creates credential request:
        print_log('\n15. Prover creates Credential Request for the given credential offer\n')
        (cred['req_json'], cred['req_metadata_json']) = await anoncreds.prover_create_credential_req(wallet_handle=prover['wallet'], 
                                                                                               prover_did=prover['did'], 
                                                                                               cred_offer_json=cred['offer_json'], 
                                                                                               cred_def_json=cred['def']['json'], 
                                                                                               master_secret_id=prover['link_secret_id'])
        
        print_log('Credential Request: ')
        pprint.pprint(json.loads(cred['req_json']))
        return(cred)

async def create_credential(issuer,cred):

        # 16. Issuer creates credential:
        print_log('\n16. Issuer (Trust Anchor) creates Credential for Credential Request\n')
        
        cred['values_json']= json.dumps({
            'sex': ['male', '5944657099558967239210949258394887428692050081607692519917050011144233115103'],
            'name': ['Alex', '1139481716457488690172217916278103335'],
            'height': ['175', '175'],
            'age': ['28', '28']
        })

        (cred['json'],_, _) = await anoncreds.issuer_create_credential(wallet_handle=issuer['wallet'], 
                                                                     cred_offer_json=cred['offer_json'], 
                                                                     cred_req_json=cred['req_json'], 
                                                                     cred_values_json=cred['values_json'], 
                                                                     rev_reg_id=None, 
                                                                     blob_storage_reader_handle=None)
        print_log('Credential: ')
        pprint.pprint(json.loads(cred['json']))
        return(cred)

async def process_and_store_credential(prover,cred):

        # 17.
        print_log('\n17. Prover processes and stores Credential\n')
        await anoncreds.prover_store_credential(wallet_handle=prover['wallet'], 
                                                cred_id=None, 
                                                cred_req_metadata_json=cred['req_metadata_json'], 
                                                cred_json=cred['json'], 
                                                cred_def_json=cred['def']['json'], 
                                                rev_reg_def_json=None)
        return(cred)

