
import asyncio
import json
import pprint

from indy import pool, ledger, wallet, did
from indy.error import IndyError, ErrorCode

from src.utils import get_pool_genesis_txn_path, PROTOCOL_VERSION

def print_log(value_color="", value_noncolor=""):
    """set the colors for text."""
    HEADER = '\033[92m'
    ENDC = '\033[0m'
    print(HEADER + value_color + ENDC + str(value_noncolor))


# Step 2 of Walk-Through
async def create_wallet(name):

    # Creates a wallet using a generic config. Be sure to check the IndySDK python wrapper for
    # detailed documentation of the different variations this wallet config can look like.
    # Additionally, we're setting credentials which is how we password protect and encrypt our
    # wallet. In this case, our password is "wallet_key" as defined in the template. In production,
    # the user should define this and it should have some sort of complexity validation to provide
    # proper protection of the wallet. DO NOT HARDCODE THIS IN PRODUCTION. Once we've created the
    # wallet we're now going to open it which allows us to interact with it by passing the
    # wallet_handle around.

    print_log('\n3. Create new identity wallet\n')

    try:        
        await wallet.create_wallet(name['wallet_config'], name['wallet_credentials'])
    except IndyError as ex:
        if ex.error_code == ErrorCode.WalletAlreadyExistsError:
            pass

    print_log('\n4. Open identity wallet and get handle\n')
    name['wallet'] = await wallet.open_wallet(name['wallet_config'], name['wallet_credentials'])
    
    return(name)    

