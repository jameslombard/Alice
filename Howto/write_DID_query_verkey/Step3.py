# Code for Step3:

import asyncio
import json
import pprint

from indy import pool, ledger, wallet, did
from indy.error import IndyError, ErrorCode

from src.utils import get_pool_genesis_txn_path, PROTOCOL_VERSION
from Step2 import print_log
from did_methods import process_did_list

async def step3(wallet_):

        # First, put a steward DID and its keypair in the wallet. This doesn't write anything to the ledger,
        # but it gives us a key that we can use to sign a ledger transaction that we're going to submit later.

        # The DID and public verkey for this steward key are already in the ledger; they were part of the genesis
        # transactions we told the SDK to start with in the previous step. But we have to also put the DID, verkey,
        # and private signing key into our wallet, so we can use the signing key to submit an acceptably signed
        # transaction to the ledger, creating our *next* DID (which is truly new). This is why we use a hard-coded seed
        # when creating this DID--it guarantees that the same DID and key material are created that the genesis txns
        # expect.

        steward = {'seed': '000000000000000000000000Steward1'}
        did_json = json.dumps({'seed': steward['seed']})

        print_log('\n5. Generate and store steward DID and verkey\n')

        try:
            steward['did'],steward['verkey'] = await did.create_and_store_my_did(wallet_['handle'], did_json) # Returns newly steward DID and verkey
        except IndyError as ex:
            if ex.error_code == ErrorCode.DidAlreadyExistsError:
                pass
                # did_list = await did.list_my_dids_with_meta(wallet_['handle'])
                # dids = process_did_list(did_list)  # dids: List of form dids[0][x], where x = '{"key : "value"}' string contain dids and metadata
                # print(dids)

        print_log('Steward DID: ', steward['did'])
        print_log('Steward Verkey: ', steward['verkey'])

        # Now, create a new DID and verkey for a trust anchor, and store it in our wallet as well. Don't use a seed;
        # this DID and its keys are secure and random. Again, we're not writing to the ledger yet.
       
        Trust_Anchor = {'name': 'Trust_Anchor'}

        try:
            Trust_Anchor['did'], Trust_Anchor['verkey'] = await did.create_and_store_my_did(wallet_['handle'], "{}")
        except IndyError as ex:
            if ex.error_code == ErrorCode.DidAlreadyExistsError:
                pass

        print_log('\n6. Generating and storing trust anchor DID and verkey\n')

        print_log('Trust anchor DID: ', Trust_Anchor['did'])
        print_log('Trust anchor Verkey: ', Trust_Anchor['verkey'])

        return steward,Trust_Anchor
        
        
