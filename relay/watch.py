#!/usr/bin/env python3
from web3 import Web3, HTTPProvider
import json
import sys
import logging
from time import sleep, time
from hashlib import sha256 as _sha256
from .daemon import DaemonThread
from .test_framework.authproxy import JSONRPCException
from .connectivity import getoceand

#watch interval is the time in seconds between oceand queries
WATCH_INTERVAL = 60
CON_INTERVAL = 10080

class OceanWatcher(DaemonThread):
    def __init__(self, conf, signer=None):
        super().__init__()
        self.conf = conf
        self.default_con_interval = CON_INTERVAL if "interval" not in conf else conf["interval"]
        self.con_interval = self.default_con_interval
        self.logger = logging.getLogger(self.__class__.__name__)
        self.signer = signer

        self.ocean = getoceand(conf)

        self.privkey = conf["privkey"]
        self.inaddress = conf["inaddress"]
        self.outaddress = conf["outaddress"]

        #Check if the node wallet already has the deposit key before importing
        validate = self.ocean.validateaddress(self.inaddress)
        have_va_addr = bool(validate["ismine"])
        watch_only = bool(validate["iswatchonly"])
        have_va_prvkey = have_va_addr and not watch_only

        rescan_needed = True

        if have_va_prvkey == False:
            try:
                self.ocean.importprivkey(self.privkey,"privkey",rescan_needed)
            except Exception as e:
                self.logger.error("{}\nFailed to import Ocean wallet private key".format(e))
                sys.exit(1)

            #Have just imported the private key so another rescan should be unnecesasary
            rescan_needed=False

        #Check if we still need to import the address given that we have just imported the private key
        validate = self.ocean.validateaddress(self.inaddress)
        have_va_addr = bool(validate["ismine"])
        if have_va_addr == False:
            ocean.importaddress(self.inaddress,"deposit",rescan_needed)

        #verify that the payment address is valid
        verifyout = self.ocean.validateaddress(self.outaddress)
        if not verifyout["isvalid"]:
            self.logger.error("\nPayment address is invalid")
            sys.exit(1)

    def run(self):
        while not self.stopped():
            sleep(WATCH_INTERVAL - time() % WATCH_INTERVAL)
            start_time = int(time())

            blockinfo = self.ocean.getblockchaininfo()

            print("checkblock "+str(blockinfo["blocks"]))

            if blockinfo["blocks"] % self.con_interval == 0:
                print("consolodate")
                # get full balance of inaddress
                unspent = self.ocean.listunspent()
                assets = {}
                outpoints = []
                total = 0.0
                print(self.inaddress)
                for output in unspent:
                    try:
                        oaddress = output["address"]
                    except:
                        oaddress = None
                    if oaddress == self.inaddress: 
                        print("match")
                        try:
                            assets[output["asset"]] = assets[output["asset"]] + output["amount"]
                        except:
                            assets[output["asset"]] = output["amount"]
                        total += float(output["amount"])
                        outpoints.append({"txid":output["txid"],"vout":output["vout"]})
                outputs = []
                for asset, amt in assets.items():
                    outp = {"address":self.outaddress, "asset":asset, "amount":amt}
                    outputs.append(outp)

                print("inputs")
                print(outpoints)
                print("outputs")
                print(outputs)

                # send to out address
                if len(outpoints) > 0:
                    tx_us = self.ocean.createrawtxoutputs(outpoints,outputs)
                    tx_s = self.ocean.signrawtransaction(tx_us)
                    txid = self.ocean.sendrawtransaction(tx_s["hex"])

                    self.logger.info("Sent consolodation: "+tx["txid"]+" Amount: "+str(total))
                    print("Sent consolodation: "+txid+" Amount: "+str(total))
                
            elapsed_time = time() - start_time
            sleep(WATCH_INTERVAL / 2 - (elapsed_time if elapsed_time < WATCH_INTERVAL / 2 else 0))

    def rpc_retry(self, rpc_func, *args):
        for i in range(5):
            try:
                return rpc_func(*args)
            except Exception as e:
                self.logger.warning("{}\nReconnecting to client...".format(e))
                self.ocean = getoceand(self.conf)
        self.logger.error("Failed reconnecting to client")
        self.stop()

