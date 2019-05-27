# Function for creating a Sovrin Identity Owner with associated agent (wallet)

import pickle
import json
import asyncio
from indy import wallet
from indy.error import IndyError, ErrorCode

# Note: Official Sovrin Roles:

async def ID():

    IDname = input('Who dis?')
    pickle_file = IDname +'.pickle'

    # Role can be:
    # - Subject
    # - Issuer
    # - Holder
    # - Prover
    # - Verifier

    try:
        with open(pickle_file,'rb') as f:
            name = pickle.load(f)  
            quit()      
    except (FileNotFoundError) as e:
        name = {'name': IDname}
        name['wallet_config'] = json.dumps({'id':name['name']+'_'+'wallet'})
        name['wallet_credentials'] = json.dumps({'key':name['name']+'_'+'wallet_key'})
        with open(pickle_file, 'wb') as f:
            pickle.dump(name, f)

    return name
