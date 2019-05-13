import asyncio
import json

import pprint

from indy import pool, ledger, wallet, did
from indy.error import IndyError, ErrorCode

from src.utils import get_pool_genesis_txn_path, PROTOCOL_VERSION
from Step2 import print_log

async def pool_configuration(pool_name):

    # await pool.delete_pool_ledger_config(pool_name)

    pool_= {'name': pool_name}
    genesis_file_path = get_pool_genesis_txn_path(pool_name)
    pool_['config'] = json.dumps({'genesis_txn': str(genesis_file_path)})

    try:        
        await pool.create_pool_ledger_config(config_name=pool_['name'], config=pool_['config'])
    except IndyError as ex:
        if ex.error_code == ErrorCode.PoolLedgerConfigAlreadyExistsError:
            pass

    await pool.set_protocol_version(PROTOCOL_VERSION)
        # Pool name / wallet config for Trust Anchor:

    print(genesis_file_path)

    return(pool_)