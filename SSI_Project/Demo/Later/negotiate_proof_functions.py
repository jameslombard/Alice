
import pickle    
import asyncio
import json
import pprint

from indy.error import IndyError, ErrorCode
from indy import wallet, anoncreds

from write_did_functions import print_log

async def build_proof_request(issuer,schema):
# 18.
        print_log('\n Prover gets Credentials for Proof Request\n')
        proof_request = {
            'nonce': '123432421212',
            'name': 'proof_req_1',
            'version': '0.1',
            'requested_attributes': {
                'attr1_referent': {
                    'name': 'name',
                    "restrictions": {
                        "issuer_did": issuer['did'],
                        "schema_id": schema['id']
                    }
                }
            },
            'requested_predicates': {
                'predicate1_referent': {
                    'name': 'age',
                    'p_type': '>=',
                    'p_value': 18,
                    "restrictions": {
                       "issuer_did": issuer['did']
                    }
                }
            }
        }
        print_log('Proof Request: ')
        pprint.pprint(proof_request)

        return(proof_request)

async def fetch_credentials(prover, proof_req):

        # 19. 
        print_log('\n Prover gets Credentials for attr1_referent and predicate1_referent\n')
        proof_req['json'] = json.dumps(proof_req)
        prover['cred_search_handle'] = \
            await anoncreds.prover_search_credentials_for_proof_req(prover['wallet'], proof_req['json'], None)

        creds_for_attr1 = await anoncreds.prover_fetch_credentials_for_proof_req(prover['cred_search_handle'],
                                                                                 'attr1_referent', 1)
        prover['cred_for_attr1'] = json.loads(creds_for_attr1)[0]['cred_info']
        print_log('Prover credential for attr1_referent: ')
        pprint.pprint(prover['cred_for_attr1'])

        creds_for_predicate1 = await anoncreds.prover_fetch_credentials_for_proof_req(prover['cred_search_handle'],
                                                                                      'predicate1_referent', 1)
        prover['cred_for_predicate1'] = json.loads(creds_for_predicate1)[0]['cred_info']
        print_log('Prover credential for predicate1_referent: ')
        pprint.pprint(prover['cred_for_predicate1'])

        await anoncreds.prover_close_credentials_search_for_proof_req(prover['cred_search_handle'])

        return prover,proof_req

async def create_proof(proof_req,prover,cred,schema):

                # 20.
        print_log('\n Prover creates Proof for Proof Request\n')
        prover['requested_creds'] = json.dumps({
            'self_attested_attributes': {},
            'requested_attributes': {
                'attr1_referent': {
                    'cred_id': prover['cred_for_attr1']['referent'],
                    'revealed': True
                }
            },
            'requested_predicates': {
                'predicate1_referent': {
                    'cred_id': prover['cred_for_predicate1']['referent']
                }
            }
        })

        print_log('Requested Credentials for Proving: ')
        pprint.pprint(json.loads(prover['requested_creds']))

        prover['schema_id'] = json.loads(cred['offer_json'])['schema_id']
        schema['proof_json'] = json.dumps({prover['schema_id']: json.loads(schema['json'])})
        cred['def']['proof_json'] = json.dumps({cred['def']['id']: json.loads(cred['def']['json'])})
        proof_json = await anoncreds.prover_create_proof(prover['wallet'],
                                                         proof_req['json'],
                                                         prover['requested_creds'],
                                                         prover['link_secret_id'],
                                                         schema['proof_json'],
                                                         cred['def']['proof_json'],
                                                         "{}")
        proof = json.loads(proof_json)
        proof['json'] = proof_json
        assert 'Alex' == proof['requested_proof']['revealed_attrs']['attr1_referent']["raw"]
        return proof,prover

async def verify_proof(proof_req,proof,cred,schema):        
        # 21.
        print_log('\n Verifier is verifying proof from Prover\n')
        assert await anoncreds.verifier_verify_proof(proof_req['json'],
                                                             proof['json'],
                                                             schema['proof_json'],
                                                             cred['def']['proof_json'],
                                                             "{}", "{}")