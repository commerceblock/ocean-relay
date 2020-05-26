#!/usr/bin/env python3
import os
import random
import sys
import shutil
import logging
import json
import time
import argparse
from decimal import *
from pdb import set_trace
from .test_framework.authproxy import AuthServiceProxy, JSONRPCException
from .watch import OceanWatcher
from .hsm import HsmPkcs11

PRVKEY = ""

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--rpconnect', required=True, type=str, help="Client RPC host")
    parser.add_argument('--rpcport', required=True, type=str, help="Client RPC port")
    parser.add_argument('--rpcuser', required=True, type=str, help="RPC username for client")
    parser.add_argument('--rpcpassword', required=True, type=str, help="RPC password for client")
    parser.add_argument('--in', required=True, type=str, help="The recieve address to consolodate payments from")

    parser.add_argument('--out',required=True, type=str, help="The address to send incoming payments to")
    parser.add_argument('--privkey', required=True, type=str, help="The private key for the recieve address")

    parser.add_argument('--interval', default=10080, type=int, help="Consolodation interval (in blocks)")
    return parser.parse_args()

def main():
    args = parse_args()

    logging.basicConfig(
        format='%(asctime)s %(name)s:%(levelname)s:%(process)d: %(message)s',
        level=logging.INFO
    )

    conf = {}
    conf["rpcuser"] = args.rpcuser
    conf["rpcpassword"] = args.rpcpassword
    conf["rpcport"] = args.rpcport
    conf["rpcconnect"] = args.rpconnect
    conf["in"] = args.inaddress

    pvk = args.privkey
    conf["privkey"] = pvk
    conf["out"] = args.outaddress
    conf["interval"] = args.interval

    signer = None
    if args.hsm:
        signer = HsmPkcs11(os.environ['KEY_LABEL'])

    ocean_watch = OceanWatcher(conf, signer)
    ocean_watch.start()

    try:
        while 1:
            if ocean_watch.stopped():
                ocean_watch.join()
                raise Exception("Node thread has stopped")
            time.sleep(0.01)
    except KeyboardInterrupt:
        ocean_watch.stop()
        ocean_watch.join()


if __name__ == "__main__":
    main()
