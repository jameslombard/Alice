# Function for creating a Sovrin Identity Owner with associated agent (wallet)

import pickle
import json
import asyncio
from indy import wallet
from indy.error import IndyError, ErrorCode

# Note: Official Sovrin Roles:

async def ID():

    IDname = input('Who dis?:').strip()

    # Role can be:
    # - Subject
    # - Issuer
    # - Holder
    # - Prover
    # - Verifier

    name = {'name': IDname}
    pickle_file = name['name']+'.pickle'

    try:
        with open(pickle_file,'rb') as f:
            name = pickle.load(f)
            return name
    except (FileNotFoundError) as e:
        pass

    name['wallet_config'] = json.dumps({'id':name['name']+'_'+'wallet'})
    name['wallet_credentials'] = json.dumps({'key':name['name']+'_'+'wallet_key'})

    # Deletes wallet if it already exists:
    if name['name'] == 'steward':
        try:
            await wallet.delete_wallet(name['wallet_config'], name['wallet_credentials'])
        except IndyError as ex:
            if ex.error_code == ErrorCode.WalletNotFoundError:
                pass

    pickle_file = name['name']+'.pickle'
    with open(pickle_file, 'wb') as f:
        pickle.dump(name, f)

    # return(name)