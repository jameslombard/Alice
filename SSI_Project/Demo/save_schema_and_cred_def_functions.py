
import pickle
import asyncio
import json
import pprint

from indy import pool, ledger, wallet, did, anoncreds
from indy.error import ErrorCode, IndyError
from write_did_functions import print_log

async def schema_request(pool_,issuer):
    # 9.
    print_log('\n Build the SCHEMA request\n')

    name = input('Schema name?:')
    version = input('Version?:')
    
    A = [] # create list
    while True:
        for i in 

        

    # Define Schema:    
    schema = {
            'name': 'gvt',
            'version': '1.0',
            'attributes': ["age", "sex", "height", "name"]
    }

    # This function call creates the schema and assumes the issuer of credentials using the schema to be the 
    # submitter of the schema request:

    schema['id'],schema['json'] = await anoncreds.issuer_create_schema(issuer_did=issuer['did'],
                                                                        name=schema['name'],
                                                                        version=schema['version'],
                                                                        attrs=json.dumps(schema['attributes']))

    print_log('Schema: ')
    pprint.pprint(schema)
    print_log('Schema json: ')
    pprint.pprint(json.loads(schema['json']))

    # Create schema for an issuer: return issuer_schema_id, issuer_schema_json:

    schema_request = await ledger.build_schema_request(submitter['did'],schema['json'])
    print_log('Schema request: ') # form of a json string
    pprint.pprint(json.loads(schema_request))

    # 10.
    print_log('\n Sending the SCHEMA request to the ledger\n')

    schema_response = await ledger.sign_and_submit_request(pool_handle=pool_['handle'],
                                                            wallet_handle=submitter['wallet'],
                                                            submitter_did=submitter['did'],
                                                            request_json=schema_request)

    print_log('Schema response:')
    pprint.pprint(json.loads(schema_response))  
    schema_response_dict = json.loads(schema_response)

    if schema_response_dict['op'] == 'REJECT':
        print_log('\n Sending GET SCHEMA request to the ledger for existing Version Number\n')
        schema_response = await get_schema_request(pool_,submitter,schema)

    print_log('Schema response:')
    pprint.pprint(json.loads(schema_response))

    return(schema)

async def get_schema_request(pool_,submitter,schema):

    schema_request = await ledger.build_get_schema_request(submitter['did'],schema['id'])
    schema_response = await ledger.sign_and_submit_request(pool_handle=pool_['handle'],
                                                            wallet_handle=submitter['wallet'],
                                                            submitter_did=submitter['did'],
                                                            request_json=schema_request)
    return(schema_response)

async def credential_definition(pool_,issuer,schema):

    # Define a credential definition:
    # Cred['def'] : - id
    #               - json
    #               - tag 
    #               - type
    #               - config

    #Next, we create a credential definition. 
    # This references the schema that we just added, and announces 
    # who is going to be issuing credentials with that schema (our trust anchor identity, in this case), 
    # what type of signature method they plan to use ("CL" = "Camenisch Lysyanskya", 
    # the default method used for zero-knowledge proofs by indy), 
    # how they plan to handle revocation, and so forth.

    # 11.
    print_log('\n Creating and storing CRED DEFINITION.\n')
    
    cred_def = {'Issuer':issuer['name']}
    cred_def['tag'] = 'cred_def_tag'
    cred_def['type'] = 'CL'
    cred_def['config'] = json.dumps({"support_revocation": False})

    (cred_def['id'], cred_def['json']) = await anoncreds.issuer_create_and_store_credential_def(wallet_handle=issuer['wallet'],
                                                                                          issuer_did=issuer['did'], 
                                                                                          schema_json=schema['json'],
                                                                                          tag=cred_def['tag'], 
                                                                                          signature_type=cred_def['type'], 
                                                                                          config_json=cred_def['config'])
    print_log('Credential definition: ')
    pprint.pprint(json.loads(cred_def['json']))

    return(cred_def)
