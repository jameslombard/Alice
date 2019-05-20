""" This functions contains all the sub-functions called in order to run the 'write_did.py' tutorial"""

import asyncio
import json
import pprint

from indy import pool, ledger, wallet, did
from indy.error import IndyError, ErrorCode
from src.utils import get_pool_genesis_txn_path, PROTOCOL_VERSION, run_coroutine
from identity import ID


def print_log(value_color="", value_noncolor=""):
    """set the colors for text."""
    HEADER = '\033[92m'
    ENDC = '\033[0m'
    print(HEADER + value_color + ENDC + str(value_noncolor))

# Step 1 of write_did:
async def pool_configuration(pool_name):

    pool_= {'name': pool_name}
    genesis_file_path = get_pool_genesis_txn_path(pool_name)
    pool_['config'] = json.dumps({'genesis_txn': str(genesis_file_path)})

    # Set pool PROTOCAL VERSION:
    await pool.set_protocol_version(PROTOCOL_VERSION)
   
    # Check if the pool configuration is already open:
    try:
        await pool.delete_pool_ledger_config(pool_['name'])
    except IndyError as ex:
        if ex.error_code == ErrorCode.CommonIOError:
            pass

    try:        
        await pool.create_pool_ledger_config(config_name=pool_['name'], config=pool_['config'])
    except IndyError as ex:
        if ex.error_code == ErrorCode.PoolLedgerConfigAlreadyExistsError:
            pass

    print(genesis_file_path)

    print_log('\n2. Open ledger and get handle\n')
    pool_['handle'] = await pool.open_pool_ledger(pool_['name'], None)

    return(pool_)

# Function for submitting a pool restart request:

async def restart_pool(pool_,submitter):
    restart_request = await ledger.build_pool_restart_request(submitter['did'],'start','14:40')
    restart_request_response = await ledger.sign_and_submit_request(pool_handle=pool_['handle'],
                                                                    wallet_handle=submitter['wallet'],
                                                                    submitter_did=submitter['did'],
                                                                    request_json=restart_request)
    print_log('Pool Restart Request Response: ')
    pprint.pprint(json.loads(restart_request_response))

# Step 2 of write_did:
async def create_wallet(name):

    # Creates a wallet using a generic config. Be sure to check the IndySDK python wrapper for
    # detailed documentation of the different variations this wallet config can look like.
    # Additionally, we're setting credentials which is how we password protect and encrypt our
    # wallet. In this case, our password is "wallet_key" as defined in the template. In production,
    # the user should define this and it should have some sort of complexity validation to provide
    # proper protection of the wallet. DO NOT HARDCODE THIS IN PRODUCTION. Once we've created the
    # wallet we're now going to open it which allows us to interact with it by passing the
    # wallet_handle around.

    msg = '\n3. Create new '+ name['name']+ ' wallet\n'
    print_log(msg)

    try:        
        await wallet.create_wallet(name['wallet_config'], name['wallet_credentials'])
        print('pow')
    except IndyError as ex:
        if ex.error_code == ErrorCode.WalletAlreadyExistsError:
            pass

    msg = '\n4. Open '+ name['name']+ ' wallet and get handle\n'
    print_log(msg)

    try:
        name['wallet'] = await wallet.open_wallet(name['wallet_config'], name['wallet_credentials'])
    except IndyError as ex:
        if ex.error_code == ErrorCode.WalletAlreadyOpenedError:
            pass

    return(name)    

# Step 3 of write_did:
async def create_did_and_verkey(name):

    # First, put a steward DID and its keypair in the wallet. This doesn't write anything to the ledger,
    # but it gives us a key that we can use to sign a ledger transaction that we're going to submit later.

    # The DID and public verkey for this steward key are already in the ledger; they were part of the genesis
    # transactions we told the SDK to start with in the previous step. But we have to also put the DID, verkey,
    # and private signing key into our wallet, so we can use the signing key to submit an acceptably signed
    # transaction to the ledger, creating our *next* DID (which is truly new). This is why we use a hard-coded seed
    # when creating this DID--it guarantees that the same DID and key material are created that the genesis txns
    # expect.

    if name['name'] == 'steward':
        name['seed'] = '000000000000000000000000Steward1'
        did_json = json.dumps({'seed': name['seed']})       

        try:
            print_log('\n5. Generate and store steward DID and verkey\n')
            name['did'],name['verkey'] = await did.create_and_store_my_did(name['wallet'], did_json) # Returns newly created steward DID and verkey
        except IndyError as ex:
            if ex.error_code == ErrorCode.DidAlreadyExistsError:
                pass

        print_log('Steward DID: ', name['did'])
        print_log('Steward Verkey: ', name['verkey'])
        return(name)

    # Now, create a new DID and verkey for a trust anchor, and store it in our wallet as well. Don't use a seed;
    # this DID and its keys are secure and random. Again, we're not writing to the ledger yet.
    
    try:
        name['did'], name['verkey'] = await did.create_and_store_my_did(name['wallet'], "{}")
    except IndyError as ex:
        if ex.error_code == ErrorCode.DidAlreadyExistsError:
            pass

    msg = '\n6. Generating and storing ' + name['name'] + ' DID and verkey\n'
    print_log(msg)

    print_log(name['name']+' DID:', name['did'])
    print_log(name['name']+' Verkey:',name['verkey'])

    return(name)

# Step 4 of write_did:
async def nym_request(pool_,submitter,target,nymrole): 

    # Accepted values for nymrole: 
    #  
    #     :param role: Role of a user NYM record:
    #                          null (common USER)
    #                          TRUSTEE
    #                          STEWARD
    #                          TRUST_ANCHOR
    #                          NETWORK_MONITOR
    #                          empty string to reset role
    # :return: Request result as json.

    # Here, we are building the transaction payload that we'll send to write the Trust Anchor identity to the ledger.
    # We submit this transaction under the authority of the steward DID that the ledger already recognizes.
    # This call will look up the private key of the steward DID in our wallet, and use it to sign the transaction.

    print_log('\n7. Building NYM request to add Trust Anchor to the ledger\n')
    nym_transaction_request = await ledger.build_nym_request(submitter_did=submitter['did'],
                                                            target_did=target['did'],
                                                            ver_key=target['verkey'],
                                                            alias=None,
                                                            role=nymrole)
    print_log('NYM transaction request: ')
    pprint.pprint(json.loads(nym_transaction_request))

    # Now that we have the transaction ready, send it. The building and the sending are separate steps because some
    # clients may want to prepare transactions in one piece of code (e.g., that has access to privileged backend systems),
    # and communicate with the ledger in a different piece of code (e.g., that lives outside the safe internal
    # network).

    print_log('\n8. Sending NYM request to the ledger\n')
    nym_transaction_response = await ledger.sign_and_submit_request(pool_handle=pool_['handle'],
                                                                    wallet_handle=submitter['wallet'],
                                                                    submitter_did=submitter['did'],
                                                                    request_json=nym_transaction_request)

    print_log('NYM transaction response: ')
    pprint.pprint(json.loads(nym_transaction_response))

    # At this point, we have successfully written a new identity to the ledger. Our next step will be to query it.

# Step 5 of write_did:
async def query_did(pool_,submitter,target):

    print_log('\n10. Building the GET_NYM request to query trust anchor verkey\n')

    get_nym_request = await ledger.build_get_nym_request(submitter_did=submitter['did'],
                                                            target_did=target['did'])
    print_log('GET_NYM request: ')
    pprint.pprint(json.loads(get_nym_request))
    
    print_log('\n11. Sending the Get NYM request to the ledger\n')

    get_nym_response_json = await ledger.submit_request(pool_handle=pool_['handle'],
                                                        request_json=get_nym_request)
    get_nym_response = json.loads(get_nym_response_json)
    
    print_log('GET_NYM response: ')
    pprint.pprint(get_nym_response)

    return(get_nym_response)

# Primary function for replacing the verkeys of a Trust Anchor ('rotate_key.py' tutorial):

async def replace_keys(pool_,submitter,target,nymrole):

    print_log('\n9. Generating new verkey of trust anchor in wallet\n')

    new_verkey = await did.replace_keys_start(submitter['wallet'], submitter['did'], "{}")
    print_log('New Trust Anchor Verkey: ', new_verkey)
    
    print_log('\n10. Building NYM request to update new verkey to ledger\n')

    nym_request = await ledger.build_nym_request(submitter_did=submitter['did'], 
                                                    target_did=submitter['did'], 
                                                    ver_key=new_verkey, 
                                                    alias=None, 
                                                    role=nymrole)

    print_log('NYM request:')
    pprint.pprint(json.loads(nym_request))
    
    print_log('\n11. Sending NYM request to the ledger\n')

    nym_response = await ledger.sign_and_submit_request(pool_handle=pool_['handle'],
                                                            wallet_handle=submitter['wallet'],
                                                            submitter_did=submitter['did'],
                                                            request_json=nym_request)

    print_log('NYM response:')
    pprint.pprint(json.loads(nym_response))
    
    print_log('\n12. Apply new verkey in wallet\n')

    await did.replace_keys_apply(submitter['wallet'], submitter['did'])

async def cleanup(pool_,name):    # Do some cleanup.

    msg = '\n13. Closing ' + name['name'] + ' wallet and pool\n'    

    await wallet.close_wallet(name['wallet'])

    try:
        await pool.close_pool_ledger(pool_['handle'])
    except IndyError as ex:
        if ex.error_code == ErrorCode.PoolLedgerInvalidPoolHandle:
            pass

    try:
        await pool.delete_pool_ledger_config(pool_['name'])
        print_log('\n14. Deleting pool ledger config\n')
    except IndyError as ex:
        if ex.error_code == ErrorCode.CommonIOError:
            pass

    msg = '\n15. Deleting ' + name['name'] + ' wallet\n'
    print_log(msg)

    try:
        await wallet.delete_wallet(name['wallet_config'], name['wallet_credentials'])
    except IndyError as ex:
        if ex.error_code == ErrorCode.WalletNotFoundError:
            pass
