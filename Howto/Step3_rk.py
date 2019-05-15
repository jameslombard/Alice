# Code for Step 3 of Rotating a key pair	

import json	
from indy import did, ledger
from Step2 import print_log
import pprint

async def replace_keys(pool_,name):

    print_log('\n9. Generating new verkey of trust anchor in wallet\n')
    new_verkey = await did.replace_keys_start(name['wallet'], name['did'], "{}")
    print_log('New Trust Anchor Verkey: ', new_verkey)
    
    print_log('\n10. Building NYM request to update new verkey to ledger\n')
    nym_request = await ledger.build_nym_request(submitter_did=name['did'], 
                                                    target_did=name['did'], 
                                                    ver_key=new_verkey, 
                                                    alias=None, 
                                                    role=name['role'])

    print_log('NYM request:')
    pprint.pprint(json.loads(nym_request))
    
    print_log('\n11. Sending NYM request to the ledger\n')
    nym_response = await ledger.sign_and_submit_request(pool_handle=pool_['handle'],
                                                            wallet_handle=name['wallet'],
                                                            submitter_did=name['did'],
                                                            request_json=nym_request)

    print_log('NYM response:')
    pprint.pprint(json.loads(nym_response))
    
    print_log('\n12. Apply new verkey in wallet\n')
    await did.replace_keys_apply(name['wallet'], name['did'])