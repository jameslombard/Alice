
import asyncio
import json
import pprint

from indy import pool, ledger, wallet, did, anoncreds
from indy.error import ErrorCode, IndyError
from write_did_functions import print_log

async def schema_request(pool_,steward,name):
    # 9.
    print_log('\n9. Build the SCHEMA request to add new schema to the ledger as a Steward\n')
    seq_no = 1
    schema = {
        'seqNo': seq_no,
        'dest': steward['did'],
        'data': {
            'id': '1',
            'name': 'gvt',
            'version': '1.0',
            'ver': '1.0',
            'attrNames': ['age', 'sex', 'height', 'name']
        }
    }

    schema_data = schema['data']
    print_log('Schema data: ')
    pprint.pprint(schema_data)
    print_log('Schema: ')
    pprint.pprint(schema)
    schema_request = await ledger.build_schema_request(steward['did'], json.dumps(schema_data))
    print_log('Schema request: ')
    pprint.pprint(json.loads(schema_request))

    # 10.
    print_log('\n10. Sending the SCHEMA request to the ledger\n')

    schema_response = await ledger.sign_and_submit_request(pool_['handle'], name['wallet'], steward['did'], schema_request)
    print_log('Schema response:')
    pprint.pprint(json.loads(schema_response))
    
    # schema_response_dict = json.loads(schema_response)
    # if schema_response_dict['op'] == 'REJECT':
    #     print_log('\nSending GET SCHEMA request to the ledger for existing Version Number\n')
    #     schema_response = await get_schema_request(pool_,steward,name,schema_data)

    # print_log('Schema response:')
    # pprint.pprint(json.loads(schema_response))

    return(schema)

async def get_schema_request(pool_,steward,name,schema_data):
    pprint.pprint(schema_data)
    print(type(schema_data))
    print(type(schema_data['id']))

    schema_request = await ledger.build_get_schema_request(steward['did'],schema_data['id'])
    schema_response = await ledger.sign_and_submit_request(pool_['handle'], name['wallet'], steward['did'], schema_request)
    return(schema_response)

async def credential_definition(pool_,name,schema):

    # 11.
    print_log('\n11. Creating and storing CRED DEFINITION using anoncreds as Trust Anchor, for the given Schema\n')
    cred_def_tag = 'cred_def_tag'
    cred_def_type = 'CL'
    cred_def_config = json.dumps({"support_revocation": False})

    (cred_def_id, cred_def_json) = await anoncreds.issuer_create_and_store_credential_def(name['wallet'], name['did'], json.dumps(schema['data']),
                                                                            cred_def_tag, cred_def_type, cred_def_config)
    print_log('Credential definition: ')
    pprint.pprint(json.loads(cred_def_json))

