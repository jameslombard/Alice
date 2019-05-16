import asyncio
import json

import pprint

from indy import pool, ledger, wallet, did
from indy.error import IndyError, ErrorCode

from src.utils import get_pool_genesis_txn_path, PROTOCOL_VERSION
from Step2 import print_log

async def pool_configuration(pool_name):

    pool_= {'name': pool_name}
    genesis_file_path = get_pool_genesis_txn_path(pool_name)
    pool_['config'] = json.dumps({'genesis_txn': str(genesis_file_path)})

# Check if the pool configuration is already open:
    
    try:
        await pool.delete_pool_ledger_config(pool_['name'])
    except IndyError as ex:
        if ex.error_code == ErrorCode.CommonIOError:
            pass

    print_log('\n1. Create new pool ledger configuration to connect to ledger.\n')

    try:        
        await pool.create_pool_ledger_config(config_name=pool_['name'], config=pool_['config'])
    except IndyError as ex:
        if ex.error_code == ErrorCode.PoolLedgerConfigAlreadyExistsError:
            pass

    print(genesis_file_path)

    print_log('\n2. Open ledger and get handle\n')
    pool_['handle'] = await pool.open_pool_ledger(pool_['name'], None)

    # Set pool PROTOCAL VERSION:
    await pool.set_protocol_version(PROTOCOL_VERSION)

    return(pool_)


