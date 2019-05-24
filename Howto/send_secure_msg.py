import asyncio
import time
import re

# Not used here, but will be required for the next steps
from indy import crypto, did, wallet
from send_secure_msg_functions import init, prep,read

async def demo():
    me,them = await init()

    while True:
        argv = input('> ').strip().split(' ')
        cmd = argv[0].lower()
        rest = ' '.join(argv[1:])
        if re.match(cmd, 'prep'):
            # Call prep
            await prep(me,them,rest)
            # Call read
        elif re.match(cmd, 'read'):
            await read(me)
        elif re.match(cmd, 'quit'):
            break
        else:
            print('Huh?')

if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(demo())
        time.sleep(1)  # waiting for libindy thread complete
    except KeyboardInterrupt:
        print('')