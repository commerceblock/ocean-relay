# Ocean Relay daemon

Application for performing automated consolodation of payments at a specified interval on an Ocean-based blockchain. 

The application connects to an Ocean blockchain via an RPC connection to an `oceand` client. The application is configured with the address to consolodate payments from `$INADDRESS`, the corresponding private key `$PRIVKEY` and the address to send the consolodated payments to. In addition, the consolodation interval can be supplied as `$INTERVAL` blocks (the default is 1 week: 10080 blocks). 

## Instructions
1. `pip3 install -r requirements.txt`
2. `python3 setup.py build && python3 setup.py install`
3. To run the client `./run_relay` or `python3 -m relay` and provide the following arguments:
`--rpcconnect $HOST --rpocport $PORT --rpcuser $USER --rpcpass --privkey $PRIVKEY $PASS --in $INADDRESS --out $OUTADDRESS`

Arguments:

- `--rpconnect`: rpc host of Ocean node
- `--rpcport`: rpc port of Ocean node
- `--rpcuser`: rpc username
- `--rpcpassword`: rpc password
- `--in`: The recieve address to aggregate payments from
- `--out`: The address to send aggregated payments to
- `--privkey`: Private key for the recieve address
- `--interval`: Consolodation interval (in blocks)
