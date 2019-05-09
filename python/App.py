""" Import required libraries """
# Initializing the project

import time

from indy import anoncreds, crypto, did, ledger, pool, wallet, blob_storage

import json
import logging

import argparse
import sys
from ctypes import *
from os.path import dirname

from indy.error import ErrorCode, IndyError

from src.utils import get_pool_genesis_txn_path, run_coroutine, PROTOCOL_VERSION

# Setting up a pool configuration:
# List Nodes: Stored as NODE transactions - genesis transactions
# Pool config: Name ; Pool config JSON
# 
# Set protocol version 2 to work with Indy Node 1.4


