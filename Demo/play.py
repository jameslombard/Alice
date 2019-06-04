# function for generating a variable length random number
# import random
# import os
# c_old = str(random.randint(0,9))
# for x in range(1111):
#       c_old = c_old + str(random.randint(0,9))
# c_old = int(c_old)
# print(c_old)
# print(os.getcwd())

import asyncio
from secure_messenger import messenger
IP = '192.168.11.215'

async def main():

    # await messenger(IP)
    p = input('Whddup?').lower()
    print(p)

if __name__ == '__main__':

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()