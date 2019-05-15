# Function for creating a Sovrin Identity Owner with associated agent (wallet)

import json
import asyncio
from indy import wallet
from indy.error import IndyError, ErrorCode

async def ID(IDname, role):
    
    name = {'name': IDname}
    name['wallet_config'] = json.dumps({'id':name['name']+'_'+'wallet_id'})
    name['wallet_credentials'] = json.dumps({'key':name['name']+'_'+'wallet_key'})
    name['role'] = role

    # Deletes wallet if it already exists:
    try:
        await wallet.delete_wallet(name['wallet_config'], name['wallet_credentials'])
        print('pow')
    except IndyError as ex:
        if ex.error_code == ErrorCode.WalletNotFoundError:
            pass

    return(name)