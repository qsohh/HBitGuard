"""Transaction Tracker"""

from web3 import Web3
from typing import Dict, Any

from .decoders import to_hexstr, to_bytes
from .registry_event import build_registry, make_unknown_raw

REGISTRY = build_registry()

def analyze_tx(w3: Web3, tx_hash: str, save_data: bool=False) -> Dict[str, Any]:
    """Analyze a transaction by its hash, decode events and record unregistered events. Can save database if necessary."""
    tx = w3.eth.get_transaction(tx_hash)
    receipt = w3.eth.get_transaction_receipt(tx_hash)
    result = {
        "tx_hash": to_hexstr(receipt["transactionHash"]).lower(),
        "from": tx["from"].lower(),
        "to_contract": (tx["to"] or "").lower(),
        "block_number": receipt["blockNumber"],
        "gas_used": receipt["gasUsed"],
        "status": "success" if receipt["status"] == 1 else "failed",
        "events": [],
        "unknown_events_raw": [],
    }

    for log in sorted(receipt["logs"], key=lambda x: x["logIndex"]):
        topics_hex = [to_hexstr(t).lower() for t in log.get("topics", [])]
        data_bytes = to_bytes(log.get("data", "0x"))
        if not topics_hex:
            result["unknown_events_raw"].append(make_unknown_raw(tx, receipt, log))
            continue

        topic0 = topics_hex[0]
        meta = REGISTRY.get(topic0)
        if meta is None:
            result["unknown_events_raw"].append(make_unknown_raw(tx, receipt, log))
            continue

        handler = meta["handler"]
        try:
            ev = handler(log, topics_hex, data_bytes)
            ev.update({
                "block_number": receipt["blockNumber"],
                "tx_hash": to_hexstr(receipt["transactionHash"]).lower(),
                "log_index": log["logIndex"],
            })
            result["events"].append(ev)
        except Exception as e:
            raw = make_unknown_raw(tx, receipt, log)
            raw["parse_error"] = str(e)
            result["unknown_events_raw"].append(raw)

    if save_data:
        save_normalized_events(result["events"])
        save_unknown_events(result["unknown_events_raw"])

    return result

def save_normalized_events(events: list) -> None:
    """
    TODO:
    """
    raise NotImplementedError
    return

def save_unknown_events(rows: list) -> None:
    """
    TODO:
    """
    raise NotImplementedError
    return


if __name__ == "__main__":
    import sys, json, os
    from dotenv import load_dotenv
    load_dotenv()
    RPC_URL = os.environ["RPC_URL"]
    if len(sys.argv) < 2:
        tx_hash = os.environ["EX_TX_HASH"]
    else:
        tx_hash = sys.argv[1]
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    out = analyze_tx(w3, tx_hash)
    print(json.dumps(out, ensure_ascii=False, indent=2))