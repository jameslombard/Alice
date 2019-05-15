# Step 4: Write the DID and Verkey for our trust anchor identity to the ledger.

import asyncio
import pprint
import json
from indy import ledger, did    
from Step2 import print_log
from did_methods import process_did_list

async def write_did_and_verkey_to_ledger(pool_,steward, name):
    
    # Here, we are building the transaction payload that we'll send to write the Trust Anchor identity to the ledger.
    # We submit this transaction under the authority of the steward DID that the ledger already recognizes.
    # This call will look up the private key of the steward DID in our wallet, and use it to sign the transaction.

    print_log('\n7. Building NYM request to add Trust Anchor to the ledger\n')
    nym_transaction_request = await ledger.build_nym_request(submitter_did=steward['did'],
                                                                target_did=name['did'],
                                                                ver_key=name['verkey'],
                                                                alias=None,
                                                                role=name['role'])
    print_log('NYM transaction request: ')
    pprint.pprint(json.loads(nym_transaction_request))

    # Now that we have the transaction ready, send it. The building and the sending are separate steps because some
    # clients may want to prepare transactions in one piece of code (e.g., that has access to privileged backend systems),
    # and communicate with the ledger in a different piece of code (e.g., that lives outside the safe internal
    # network).

    print_log('\n8. Sending NYM request to the ledger\n')
    nym_transaction_response = await ledger.sign_and_submit_request(pool_handle=pool_['handle'],
                                                                    wallet_handle=name['wallet'],
                                                                    submitter_did=steward['did'],
                                                                    request_json=nym_transaction_request)
    print_log('NYM transaction response: ')
    pprint.pprint(json.loads(nym_transaction_response))
    
    # At this point, we have successfully written a new identity to the ledger. Our next step will be to query it.