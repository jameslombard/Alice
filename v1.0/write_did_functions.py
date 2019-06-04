""" This functions contains all the sub-functions called in order to run the 'write_did.py' tutorial """

import pickle
import asyncio
import json
import pprint
import os

from indy import pool, ledger, wallet, did
from indy.error import IndyError, ErrorCode
from src.utils import get_pool_genesis_txn_path, PROTOCOL_VERSION, run_coroutine
from identity import print_log,ID, IDconfig, create_wallet, did_and_verkey

# Step 1 of write_did:
async def pool_configuration(IP):
 
    pool_name = input('Pool name?:').strip().lower()          
    file_name = pool_name+'.pickle'

    try:
        with open(file_name, 'rb') as f:
            pool_ = pickle.load(f)
    except (FileNotFoundError) as e:
        pool_= {'name': pool_name}
        genesis_file_path = get_pool_genesis_txn_path(pool_name,IP)
        pool_['config'] = json.dumps({'genesis_txn': str(genesis_file_path)}) 

        # Set pool PROTOCAL VERSION:

    await pool.set_protocol_version(PROTOCOL_VERSION)
    genesis_file_path = get_pool_genesis_txn_path(pool_['name'],IP)

    # try:
    #     await pool.close_pool_ledger(pool_['handle'])
    # except IndyError as ex:
    #     if ex.error_code == ErrorCode.PoolLedgerInvalidPoolHandle:
    #         pass

    # try:
    #     await pool.delete_pool_ledger_config('pool')
    # except IndyError as ex:
    #     if ex.error_code == ErrorCode.CommonIOError:
    #         pass

    try:        
        await pool.create_pool_ledger_config(config_name=pool_['name'], config=pool_['config'])
        print_log('\n Setting up pool configuration.\n')
    except IndyError as ex:
        if ex.error_code == ErrorCode.PoolLedgerConfigAlreadyExistsError:
            pass
    try:          
        pool_['handle'] = await pool.open_pool_ledger(pool_['name'], None)
        print_log('\n Open ledger and get handle\n')  
    except IndyError as ex:
        if ex.error_code == ErrorCode.PoolLedgerInvalidPoolHandle:
            pass

    print(genesis_file_path)
    print('Pool handle:',pool_['handle'])

    with open(file_name, 'wb') as f:
        pickle.dump(pool_, f)

    return pool_

# Function for submitting a pool restart request:
# async def restart_pool(pool_,submitter):
#     restart_request = await ledger.build_pool_restart_request(submitter['did'],'start','14:40')
#     restart_request_response = await ledger.sign_and_submit_request(pool_handle=pool_['handle'],
#                                                                     wallet_handle=submitter['wallet'],
#                                                                     submitter_did=submitter['did'],
#                                                                     request_json=restart_request)
#     print_log('\n Pool Restart Request Response \n')
#     pprint.pprint(json.loads(restart_request_response))

# Step 4 of write_did:

async def nym_request(IP,*args): 

    # Load input:
    #########################################################################

    pool_ = await pool_configuration(IP)
            
    if not args:
        sub = input('Submitter? ').strip().lower()
    else: 
        for arg in args:
            sub = arg

    pickle_file = sub+'.pickle'
    await ID(sub) # Name, wallet and DID/Verkey creation

    with open(pickle_file,'rb') as f:
            name = pickle.load(f)
      
    submitter = name    

    target = {'name': input('Target? ').strip().lower()}

    print('Submitting NYM Request for?')
    print('1. DID and Verkey for '+target['name']+ '(Connection request).')
    print('2. DID and Verkey from '+target['name']+ '(Connection response).')
    print('3. '+target['name']+' DID and Verkey (Verinym).')

    tar = int(input('Please specify number:'))

    AdidB = 'did_for_'+target['name']
    AkeyB = 'key_for_'+target['name']
    BdidA = 'did_from_'+target['name']
    BkeyA = 'key_from_'+target['name']
    Bdid = target['name']+'_did'
    Bkey = target['name']+'_key'

    if tar == 1:
        target['did'] = name[AdidB]
        target['verkey'] = name[AkeyB]
        nymrole = None
    elif tar == 2:
        target['did'] = name[BdidA]
        target['verkey'] = name[BkeyA]
        nymrole = None
    else:
        target['did'] = name[Bdid]
        target['verkey'] = name[Bkey]
        nymrole = 'TRUST_ANCHOR'

    #########################################################################

    # Accepted values for nymrole: 
    #  
    #     :param role: Role of a user NYM record:
    #                          null (common USER)
    #                          TRUST_ANCHOR
    #                          NETWORK_MONITOR
    #                          empty string to reset role
    # :return: Request result as json.

    # print(' - None')
    # print(' - TRUST_ANCHOR')
    # print(' - NETWORK_MONITOR')
    # print(' - empty string to reset role')
    # nymrole = input('Role of target?')

    # Here, we are building the transaction payload that we'll send to write the Trust Anchor identity to the ledger.
    # We submit this transaction under the authority of the steward DID that the ledger already recognizes.
    # This call will look up the private key of the steward DID in our wallet, and use it to sign the transaction.

    print_log('\n Building NYM request\n')
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

    print_log('\n Sending NYM request to the ledger\n')
    nym_transaction_response = await ledger.sign_and_submit_request(pool_handle=pool_['handle'],
                                                                    wallet_handle=submitter['wallet'],
                                                                    submitter_did=submitter['did'],
                                                                    request_json=nym_transaction_request)

    print_log('NYM transaction response: ')
    pprint.pprint(json.loads(nym_transaction_response))

    # At this point, we have successfully written a new identity to the ledger. Our next step will be to query it.

async def query_did(IP,*args): # Same as a GET_NYM request
    
    # Load input:
    #########################################################################

    pool_ = await pool_configuration(IP)

    if not args:
        sub = input('Submitter? ').strip().lower()
    else: 
        for arg in args:
            sub = arg

    pickle_file = sub+'.pickle'
    
    await ID(sub)
    with open(pickle_file,'rb') as f:
        name = pickle.load(f)
    
    submitter = name    
    tar = input('Target? ').strip().lower()  

    Bdid = tar+'_did'
    target = {'did':name[Bdid]}

    ############################################################################

    print_log('\n Building the GET_NYM request to query trust anchor verkey\n')

    get_nym_request = await ledger.build_get_nym_request(submitter_did=submitter['did'],
                                                            target_did=target['did'])
    print_log('GET_NYM request: ')
    pprint.pprint(json.loads(get_nym_request))
    
    print_log('\n Sending the Get NYM request to the ledger\n')

    get_nym_response_json = await ledger.submit_request(pool_handle=pool_['handle'],
                                                        request_json=get_nym_request)
    get_nym_response = json.loads(get_nym_response_json)
    
    print_log('GET_NYM response: ')
    pprint.pprint(get_nym_response)

    return get_nym_response

async def replace_keys(IP,*args):

    # Load input:
    #########################################################################

    pool_ = await pool_configuration(IP)

    if not args:
        sub = input('Submitter? ').strip().lower()
    else: 
        for arg in args:
            sub = arg

    pickle_file = sub+'.pickle'
    
    await ID(sub)
    with open(pickle_file,'rb') as f:
        name = pickle.load(f)
    
    submitter = name    
         
    print(' - None')
    print(' - TRUST_ANCHOR')
    print(' - NETWORK_MONITOR')
    print(' - empty string to reset role')
    nymrole = input('Role of new verkey?')

    #########################################################################

    print_log('\n Generating new verkey of trust anchor in wallet\n')

    new_verkey = await did.replace_keys_start(submitter['wallet'], submitter['did'], "{}")
    print_log('New Verkey: ', new_verkey)
    
    print_log('\n Building NYM request to update new verkey to ledger\n')

    nym_request = await ledger.build_nym_request(submitter_did=submitter['did'], 
                                                    target_did=submitter['did'], 
                                                    ver_key=new_verkey, 
                                                    alias=None, 
                                                    role=nymrole)

    print_log('NYM request:')
    pprint.pprint(json.loads(nym_request))
    
    print_log('\n Sending NYM request to the ledger\n')

    nym_response = await ledger.sign_and_submit_request(pool_handle=pool_['handle'],
                                                            wallet_handle=submitter['wallet'],
                                                            submitter_did=submitter['did'],
                                                            request_json=nym_request)

    print_log('NYM response:')
    pprint.pprint(json.loads(nym_response))
    
    print_log('\n Apply new verkey in wallet\n')

    await did.replace_keys_apply(submitter['wallet'], submitter['did'])
    name['verkey'] = new_verkey

    with open (pickle_file, 'wb') as f:
        pickle.dump(name,f) 

async def get_verkey(IP,*args):

# Load input:
#########################################################################

    pool_ = await pool_configuration(IP)

    if not args:
        sub = input('Who dis? ').strip().lower()
    else: 
        for arg in args:
            sub = arg

    pickle_file = sub+'.pickle'
    
    await create_wallet(sub)
    with open(pickle_file,'rb') as f:
        name = pickle.load(f)
      
    Bname = input("Who's key? ").strip().lower()

    print('Requesting key for?')
    print('1. Connection with '+Bname+' (Pairwise Pseudonymous Private DID)')
    print('2. '+Bname+' Verinym (Public DID)')

    sel = int(input('Please select a number:'))

    BdidA = 'did_from_'+Bname
    Bdid = Bname+'_did'
    BkeyA = 'key_from_'+Bname
    Bkey = Bname+'_key'

    if BdidA not in name:
        print('Make sure you have the matching DID for the requested verkey.')
        return

    if sel == 1:
        DID = name[BdidA]
        name[BkeyA] = await did.key_for_did(pool_handle=pool_['handle'],
                            wallet_handle=name['wallet'],
                            did=DID)
    else:
        DID = name[Bdid]
        name[Bkey] = await did.key_for_did(pool_handle=pool_['handle'],
                            wallet_handle=name['wallet'],
                            did=DID)

    if sel == 1:
        print_log('Successfully stored the matching Verkey from '+Bname+' connection request (private pairwise DID).')

    else:
        print_log('Successfully stored the matching Verkey for '+Bname+' Verinym (Public DID).')
        

    with open (pickle_file, 'wb') as f:
        pickle.dump(name,f)   

async def cleanup(IP,*args):    # Do some cleanup.

# Load variables:
##########################################################################
     
    if not args:
        IDname = input('Who closin? ').strip().lower()
    else: 
        for arg in args:
            IDname = arg

    pickle_file = IDname+'.pickle'

    try:
        with open(pickle_file,'rb') as f:
            name = pickle.load(f)   
            
        try:
            await wallet.close_wallet(name['wallet'])
            msg = '\n Closing ' + name['name'] + ' wallet\n'    
            print_log(msg)            
        except IndyError as ex:
            if ex.error_code == ErrorCode.WalletInvalidHandle:
                print(name['name']+ ' wallet already closed.')
                print('If shutdown error occurred, a wallet delete is recommended.')
                pass

    except (FileNotFoundError) as e:
        print("ID data has been removed. Deleting wallet...")
        await delete_wallet(IDname)

#########################################################################

    pool_name = input('Pool name?:')
    file_name = pool_name+'.pickle'

    try:
        with open(file_name, 'rb') as f:
            pool_ = pickle.load(f) 

            try:
                await pool.close_pool_ledger(pool_['handle'])
                print_log('\n Closing ledger...\n')  
            except IndyError as ex:
                if ex.error_code == ErrorCode.PoolLedgerInvalidPoolHandle:
                    pass

            try:
                await pool.delete_pool_ledger_config(pool_['name'])
                print_log('\n Deleting pool ledger config\n')
                
                pickle_path = os.path.dirname(os.path.realpath(__file__))
                path = pickle_path+'/'+file_name
                os.remove(path)        

            except IndyError as ex:
                if ex.error_code == ErrorCode.CommonIOError:
                    pass
    except (FileNotFoundError) as e:
        print('Pool ledger never opened.')
        

async def delete_wallet(*args):

    if not args:
        IDname = input('Who dyin? ').strip().lower()
    else: 
        for arg in args:
            IDname = arg

    pickle_file = IDname+'.pickle'

    try:
        with open(pickle_file,'rb') as f:
            name = pickle.load(f)               
    except (FileNotFoundError) as e:
        await IDconfig(IDname)

    with open(pickle_file,'rb') as f:
        name = pickle.load(f)     

    msg = '\n Deleting ' + IDname + ' wallet\n'
    print_log(msg) 

    try:
        await wallet.delete_wallet(name['wallet_config'], name['wallet_credentials'])
    except IndyError as ex:
        if ex.error_code == ErrorCode.WalletNotFoundError:
            pass

    # Once a wallet is deleted, the associated pickle path must also be deleted:
    pickle_path = os.path.dirname(os.path.realpath(__file__))
    path = pickle_path+'/'+pickle_file
    os.remove(path)

    print('Goodbye '+ IDname + ' :(')