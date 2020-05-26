#!/usr/bin/env python3
import os
import random
import sys
import time
import subprocess
import shutil
from .test_framework.authproxy import AuthServiceProxy, JSONRPCException

def startoceand(oceanpath, datadir, conf, args=""):
    subprocess.Popen((oceanpath+"  -datadir="+datadir+" "+args).split(), stdout=subprocess.PIPE)
    return getoceand(conf)

def getoceand(conf):
    if "rpcconnect" in conf:
        rpcconnect = conf["rpcconnect"]
    else:
        rpcconnect = "127.0.0.1"

    return AuthServiceProxy("http://"+conf["rpcuser"]+":"+conf["rpcpassword"]+"@"+rpcconnect+":"+conf["rpcport"])

