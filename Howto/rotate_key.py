"""
Example demonstrating how to do the key rotation on the ledger.
Steward already exists on the ledger and its DID/Verkey are obtained using seed.
Trust Anchor's DID/Verkey pair is generated and stored into wallet.
Stewards builds NYM request in order to add Trust Anchor to the ledger.
Once NYM transaction is done, Trust Anchor wants to change its Verkey.
First, temporary key is created in the wallet.
Second, Trust Anchor builds NYM request to replace the Verkey on the ledger.
Third, when NYM transaction succeeds, Trust Anchor makes new Verkey permanent in wallet
(it was only temporary before).
To assert the changes, Trust Anchor reads both the Verkey from the wallet and the Verkey from the ledger
using GET_NYM request, to make sure they are equal to the new Verkey, not the original one
added by Steward
"""

import asyncio
import json
import pprint

from indy import pool, ledger, wallet, did
from indy.error import IndyError
from identity import ID

from write_did_functions import print_log, pool_configuration,create_wallet,create_did_and_verkey, nym_request, replace_keys, cleanup

pool_name = 'pool'

async def rotate_key_on_the_ledger():
    try:   
        # Step 1: Pool configuration   
        
        pool_= await pool_configuration(pool_name)

        # Step 2: Create ID and create and open wallet:

        steward = await ID('steward')
        steward = await create_wallet(steward)
        trust_anchor = await ID('trust_anchor')
        trust_anchor = await create_wallet(trust_anchor)

        # Add Seward and Trust Anchor DID and Verkey to the wallet:

        steward = await create_did_and_verkey(steward)
        trust_anchor = await create_did_and_verkey(trust_anchor)

        # Write the DID and Verkey for our trust anchor identity to the ledger

        nymrole = 'TRUST_ANCHOR'
        await nym_request(pool_,steward,trust_anchor,nymrole)

        # Rotate Trust Anchor keys in the wallet.

        await replace_keys(pool_,trust_anchor,trust_anchor,nymrole)

        # Cleaunup:

        await cleanup(pool_,steward)
        await cleanup(pool_,trust_anchor)

    except IndyError as e:
        print('Error occurred: %s' % e)


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(rotate_key_on_the_ledger())
    loop.close()


if __name__ == '__main__':
    main()