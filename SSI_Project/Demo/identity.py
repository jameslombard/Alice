# Function for creating a Sovrin Identity Owner with associated agent (wallet)

import pickle
import json
import asyncio
from indy import wallet,did
from indy.error import IndyError, ErrorCode

def print_log(value_color="", value_noncolor=""):
    """set the colors for text."""
    HEADER = '\033[92m'
    ENDC = '\033[0m'
    print(HEADER + value_color + ENDC + str(value_noncolor))

# Script for building a Sovrin ID:

async def ID(*args):

    if not args:
        IDname = input('Who dis? ').strip().lower()
    else: 
        for arg in args:
            IDname = arg
                
    pickle_file = IDname +'.pickle'

    try:
        with open(pickle_file, 'rb') as f:
            name = pickle.load(f)

    except (FileNotFoundError) as e:

        await IDconfig(IDname)

    await create_wallet(IDname) 
    await did_and_verkey(IDname) 

    return IDname    

async def IDconfig(IDname):        

    print_log('\n Creating new ID for '+IDname+'\n')
    pickle_file = IDname+'.pickle'

    name = {'name': IDname}
    name['wallet_config'] = json.dumps({'id':name['name']+'_'+'wallet'})
    name['wallet_credentials'] = json.dumps({'key':name['name']+'_'+'wallet_key'})

    with open(pickle_file, 'wb') as f:
        pickle.dump(name, f)

async def create_wallet(*args):

    # Creates a wallet using a generic config. Be sure to check the IndySDK python wrapper for
    # detailed documentation of the different variations this wallet config can look like.
    # Additionally, we're setting credentials which is how we password protect and encrypt our
    # wallet. In this case, our password is "wallet_key" as defined in the template. In production,
    # the user should define this and it should have some sort of complexity validation to provide
    # proper protection of the wallet. DO NOT HARDCODE THIS IN PRODUCTION. Once we've created the
    # wallet we're now going to open it which allows us to interact with it by passing the
    # wallet_handle around.

    if not args:
        IDname = input('Who dis? ').strip().lower()
    else: 
        for arg in args:
            IDname = arg
            
    pickle_file = IDname +'.pickle'

    try:
        with open(pickle_file,'rb') as f:
            name = pickle.load(f)
    except (FileNotFoundError) as e:
        await IDconfig(IDname)
        with open(pickle_file,'rb') as f:
            name = pickle.load(f)

    try:       
        await wallet.create_wallet(name['wallet_config'], name['wallet_credentials'])
        msg = '\n Create new '+ name['name']+ ' wallet\n'
        print_log(msg) 
    except IndyError as ex:
        if ex.error_code == ErrorCode.WalletAlreadyExistsError:
            pass

    try:
        name['wallet'] = await wallet.open_wallet(name['wallet_config'], name['wallet_credentials'])
        msg = '\n Open wallet for '+ name['name']+ '\n'
        print_log(msg)
    except IndyError as ex:
        if ex.error_code == ErrorCode.WalletAlreadyOpenedError:
            pass
     
    with open(pickle_file, 'wb') as f:
        pickle.dump(name, f)        
  
# Step 3 of write_did:
async def did_and_verkey(*args):

    # First, put a steward DID and its keypair in the wallet. This doesn't write anything to the ledger,
    # but it gives us a key that we can use to sign a ledger transaction that we're going to submit later.

    # The DID and public verkey for this steward key are already in the ledger; they were part of the genesis
    # transactions we told the SDK to start with in the previous step. But we have to also put the DID, verkey,
    # and private signing key into our wallet, so we can use the signing key to submit an acceptably signed
    # transaction to the ledger, creating our *next* DID (which is truly new). This is why we use a hard-coded seed
    # when creating this DID--it guarantees that the same DID and key material are created that the genesis txns
    # expect.

    if not args:
        IDname = input('Who dis? ').strip().lower()
    else: 
        for arg in args:
            IDname = arg

    pickle_file = IDname +'.pickle'

    try:
        with open(pickle_file,'rb') as f:
            name = pickle.load(f)

    except FileNotFoundError as e:
        await IDconfig(IDname)
    
    await create_wallet(IDname)

    with open(pickle_file,'rb') as f:
        name = pickle.load(f)

    # Handle case for Steward:
    if 'did' not in name:
        msg = '\n Generating and storing ' + name['name'] + ' DID and verkey\n'     
        print_log(msg)

        if name['name'] == 'steward':
            name['seed'] = '000000000000000000000000Steward1'
            did_json = json.dumps({'seed': name['seed']})    
            try:
                name['did'], name['verkey'] = await did.create_and_store_my_did(name['wallet'], did_json)
            except IndyError as ex:
                if ex.error_code == ErrorCode.DidAlreadyExistsError:
                    pass           
        else:
            
    # Now, create a new DID and verkey for a trust anchor, and store it in our wallet as well. Don't use a seed;
    # this DID and its keys are secure and random. Again, we're not writing to the ledger yet.
            try:
                name['did'], name['verkey'] = await did.create_and_store_my_did(name['wallet'], "{}")
            except IndyError as ex:
                if ex.error_code == ErrorCode.DidAlreadyExistsError:
                    pass

    print_log(name['name']+' DID:',name['did'])
    print_log(name['name']+' Verkey:',name['verkey'])        

    with open (pickle_file, 'wb') as f:
        pickle.dump(name,f)

