
from web3 import Web3
import json, os
from dotenv import load_dotenv

from chainkit import analyze_tx

def demo():
    load_dotenv()

    if "RPC_URL" in os.environ:
        RPC_URL = os.environ["RPC_URL"]
    else:
        RPC_URL = "https://1rpc.io/bnb"
    
    if "EX_TX_HASH" in os.environ:
        tx_hash = os.environ["EX_TX_HASH"]
    else:
        tx_hash = "0xad190676ea27d3a189ccea71e1de59b5e3d8dc9c1e1ffaea0c7d8204946df4e6"

    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    out = analyze_tx(w3, tx_hash)
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    demo()

# End of file