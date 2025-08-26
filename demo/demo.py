
from web3 import Web3
import os
from dotenv import load_dotenv

from chainkit.registry_event import topic0_allowlist_minimal_v2
from chainkit.runner import Runner


def demo():
    load_dotenv()

    if "RPC_URL" in os.environ:
        RPC_URL = os.environ["RPC_URL"]
    else:
        RPC_URL = "https://1rpc.io/bnb"

    if "MAX_STEP_RPC" in os.environ:
        window_step = os.environ["MAX_STEP_RPC"]
    else:
        window_step = 5

    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    ALLOW_TOPICS0 = topic0_allowlist_minimal_v2()

    runner = Runner(w3, window=window_step, overlap_blocks=2, sleep_secs=10, max_seen=50, topics=ALLOW_TOPICS0)
    runner.run_loop()

if __name__ == "__main__":
    demo()

# End of file