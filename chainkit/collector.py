
from typing import Iterable, List, Set, Optional
from web3 import Web3

from .decoders import to_hexstr

PANCAKE_V2_BCFX_BUSD_ADDR = "0xA0387eBeA6be90849c2261b911fBBD52B4C9eAC4"

def collect_tx_hashes(w3: Web3, watch_addresses: Iterable[str], from_block: int, to_block: int, topics: Optional[List[str]]=None) -> List[dict]:
    if not watch_addresses or from_block > to_block:
        return []
    # TODO: consider to apply binary cut when free level rpc raises limit error
    params = {"fromBlock": from_block, "toBlock": to_block, "address": watch_addresses}
    if topics:
        params["topics"] = [topics]
    return w3.eth.get_logs(params)

def _test_collector():
    import os, json
    from dotenv import load_dotenv
    load_dotenv()

    from .tx_tracker import analyze_tx

    RPC_URL = os.environ["RPC_URL"]
    w3 = Web3(Web3.HTTPProvider(RPC_URL))

    latest = w3.eth.block_number
    seen: Set[str] = set()
    print(collect_tx_hashes(w3, [PANCAKE_V2_BCFX_BUSD_ADDR], latest-7, latest-2))
    log = collect_tx_hashes(w3, [PANCAKE_V2_BCFX_BUSD_ADDR], 58538700, 58538705)
    for ele in log:
        for k, v in ele.items():
            if k == "transactionHash":
                if k in seen:
                    continue
                seen.add(k)
                out = analyze_tx(w3, v)
                print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    _test_collector()

# End of file