
import asyncio
import json
import pprint

from indy import pool, ledger, wallet, did, anoncreds
from indy.error import ErrorCode, IndyError
from write_did_functions import print_log

async def schema_request(pool_,submitter):
    # 9.
    print_log('\n9. Build the SCHEMA request to add new schema to the ledger as a Steward\n')

    # Define Schema:    
    schema = {
        'data': {
            'name': 'gvt',
            'version': '1.0',
            'ver': '1.0',
            'attributes': '["age", "sex", "height", "name"]'
        }
    }

    # This function call creates the schema and assumes the issuer of credentials using the schema to be the 
    # submitter of the schema request:

    schema['id'],schema['json'] = await anoncreds.issuer_create_schema(issuer_did=submitter['did'],
                                                                        name=schema['data']['name'],
                                                                        version=schema['data']['version'],
                                                                        attrs=schema['data']['attributes'])

    print_log('Schema data: ')
    pprint.pprint(schema['data'])
    print_log('Schema json: ')
    pprint.pprint(json.loads(schema['json']))
    print_log('Schema: ')
    pprint.pprint(schema)

    # Create schema for an issuer: return issuer_schema_id, issuer_schema_json:

    schema_request = await ledger.build_schema_request(submitter['did'],schema['json'])
    print_log('Schema request: ') # form of a json string
    pprint.pprint(json.loads(schema_request))

    # 10.
    print_log('\n10. Sending the SCHEMA request to the ledger\n')

    schema_response = await ledger.sign_and_submit_request(pool_handle=pool_['handle'],
                                                            wallet_handle=submitter['wallet'],
                                                            submitter_did=submitter['did'],
                                                            request_json=schema_request)

    print_log('Schema response:')
    pprint.pprint(json.loads(schema_response))  
    schema_response_dict = json.loads(schema_response)

    if schema_response_dict['op'] == 'REJECT':
        print_log('\nSending GET SCHEMA request to the ledger for existing Version Number\n')
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

    # 11.
    print_log('\n11. Creating and storing CRED DEFINITION using anoncreds as Trust Anchor, for the given Schema\n')
    
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
