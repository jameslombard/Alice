# Function for creating a Sovrin Identity Owner with associated agent (wallet)

import json
import asyncio
from indy import wallet
from indy.error import IndyError, ErrorCode

# Note: Official Sovrin Roles:

async def ID(IDname):

    # Role can be:
    # - Subject
    # - Issuer
    # - Holder
    # - Prover
    # - Verifier
    
    name = {'name': IDname}
    name['wallet_config'] = json.dumps({'id':name['name']+'_'+'wallet_id'})
    name['wallet_credentials'] = json.dumps({'key':name['name']+'_'+'wallet_key'})

    # Deletes wallet if it already exists:

    try:
        await wallet.delete_wallet(name['wallet_config'], name['wallet_credentials'])
    except IndyError as ex:
        if ex.error_code == ErrorCode.WalletNotFoundError:
            pass

    return(name)