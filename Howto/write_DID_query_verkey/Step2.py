# Step 2 code goes here.
# Tell SDK which pool you are going to use. You should have already started
        # this pool using docker compose or similar. Here, we are dumping the config
        # just for demonstration purposes.

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

async def step2(pool_, wallet_, genesis_file_path):
        
    pool_['config'] = json.dumps({'genesis_txn': str(genesis_file_path)})

    print_log('\n1. Create new pool ledger configuration to connect to ledger.\n')
    
    try:        
        await pool.create_pool_ledger_config(config_name=pool_['name'], config=pool_['config'])
    except IndyError as ex:
        if ex.error_code == ErrorCode.PoolLedgerConfigAlreadyExistsError:
            pass

        print_log('\n2. Open ledger and get handle\n')

        pool_['handle'] = await pool.open_pool_ledger(pool_['name'], None)

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
        await wallet.create_wallet(wallet_['config'], wallet_['credentials'])
    except IndyError as ex:
        if ex.error_code == ErrorCode.WalletAlreadyExistsError:
            pass

        print_log('\n4. Open identity wallet and get handle\n')
        wallet_['handle'] = await wallet.open_wallet(wallet_['config'], wallet_['credentials'])
        