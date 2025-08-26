"""
Events registry and handler.
- Builtin events: ERC20/271, PancakeSwap V2/V3 pools, WBNB
- Tools to use
- build_registry()
"""

from typing import Dict, Any, List
from hexbytes import HexBytes
from eth_utils import keccak, to_hex
import json, os
from types import MappingProxyType
from typing import Mapping, Optional

from .decoders import sig_topic, uint256_at, int256_at, bool_at, to_hexstr, make_readonly

# Handlers
def h_erc20_transfer(log, topics_hex: List[str], data_bytes: bytes) -> Dict[str, Any]:
    return {
        "type": "erc20_transfer",
        "name": "ERC20.Transfer",
        "contract": log["address"].lower(),
        "args": {
            "from": "0x" + topics_hex[1][-40:],
            "to":   "0x" + topics_hex[2][-40:],
            "value": int.from_bytes(data_bytes[-32:], "big"),
        },
    }

def h_erc20_approval(log, topics_hex: List[str], data_bytes: bytes) -> Dict[str, Any]:
    value = int.from_bytes(data_bytes[-32:], "big")
    return {
        "type": "erc20_approval",
        "name": "ERC20.Approval",
        "contract": log["address"].lower(),
        "args": {
            "owner":   "0x" + topics_hex[1][-40:],
            "spender": "0x" + topics_hex[2][-40:],
            "value": value,
            "unlimited": value == (1 << 256) - 1,
        },
    }

def h_erc721_approval_for_all(log, topics_hex: List[str], data_bytes: bytes) -> Dict[str, Any]:
    return {
        "type": "erc721_approval_for_all",
        "name": "ERC721.ApprovalForAll",
        "contract": log["address"].lower(),
        "args": {
            "owner":    "0x" + topics_hex[1][-40:],
            "operator": "0x" + topics_hex[2][-40:],
            "approved": bool_at(data_bytes, 0),
        },
    }

# --- UniswapV2 / Pancake V2 Pair ---

def h_v2_swap(log, topics_hex: List[str], data_bytes: bytes) -> Dict[str, Any]:
    return {
        "type": "v2_swap",
        "name": "UniV2.Swap",
        "contract": log["address"].lower(),  # pair
        "args": {
            "sender":   "0x" + topics_hex[1][-40:],
            "to":       "0x" + topics_hex[2][-40:],
            "amount0In":  uint256_at(data_bytes, 0),
            "amount1In":  uint256_at(data_bytes, 1),
            "amount0Out": uint256_at(data_bytes, 2),
            "amount1Out": uint256_at(data_bytes, 3),
        },
    }

def h_v2_mint(log, topics_hex: List[str], data_bytes: bytes) -> Dict[str, Any]:
    return {
        "type": "v2_mint",
        "name": "UniV2.Mint",
        "contract": log["address"].lower(),
        "args": {
            "sender":  "0x" + topics_hex[1][-40:],
            "amount0": uint256_at(data_bytes, 0),
            "amount1": uint256_at(data_bytes, 1),
        },
    }

def h_v2_burn(log, topics_hex: List[str], data_bytes: bytes) -> Dict[str, Any]:
    # Burn(address indexed sender, uint amount0, uint amount1, address indexed to)
    to_addr = "0x" + topics_hex[2][-40:] if len(topics_hex) > 2 else None
    return {
        "type": "v2_burn",
        "name": "UniV2.Burn",
        "contract": log["address"].lower(),
        "args": {
            "sender":  "0x" + topics_hex[1][-40:],
            "to":      to_addr,
            "amount0": uint256_at(data_bytes, 0),
            "amount1": uint256_at(data_bytes, 1),
        },
    }

def h_v2_sync(log, topics_hex: List[str], data_bytes: bytes) -> Dict[str, Any]:
    return {
        "type": "v2_sync",
        "name": "UniV2.Sync",
        "contract": log["address"].lower(),
        "args": {
            "reserve0": uint256_at(data_bytes, 0),  # ABI 上是 uint112，按 uint256 解析无碍
            "reserve1": uint256_at(data_bytes, 1),
        },
    }

# --- WBNB/WETH ---

def h_wrap_deposit(log, topics_hex: List[str], data_bytes: bytes) -> Dict[str, Any]:
    # Deposit(address indexed dst, uint256 wad)
    return {
        "type": "wrap_deposit",
        "name": "WBNB.Deposit",
        "contract": log["address"].lower(),
        "args": {
            "dst": "0x" + topics_hex[1][-40:],
            "wad": uint256_at(data_bytes, 0),
        },
    }

def h_wrap_withdrawal(log, topics_hex: List[str], data_bytes: bytes) -> Dict[str, Any]:
    # Withdrawal(address indexed src, uint256 wad)
    return {
        "type": "wrap_withdrawal",
        "name": "WBNB.Withdrawal",
        "contract": log["address"].lower(),
        "args": {
            "src": "0x" + topics_hex[1][-40:],
            "wad": uint256_at(data_bytes, 0),
        },
    }

# --- UniswapV3 / PancakeV3 ---

def h_v3_swap(log, topics_hex: List[str], data_bytes: bytes) -> Dict[str, Any]:
    # Swap(address indexed sender, address indexed recipient, int256 amount0, int256 amount1, uint160 sqrtPriceX96, uint128 liquidity, int24 tick)
    return {
        "type": "v3_swap",
        "name": "UniV3.Swap",
        "contract": log["address"].lower(),
        "args": {
            "sender":    "0x" + topics_hex[1][-40:],
            "recipient": "0x" + topics_hex[2][-40:],
            "amount0":   int256_at(data_bytes, 0),
            "amount1":   int256_at(data_bytes, 1),
            "sqrtPriceX96": uint256_at(data_bytes, 2),
            "liquidity": uint256_at(data_bytes, 3),
            "tick":        int256_at(data_bytes, 4),  # 编码为 int24，但占 32B slot，按有符号整型取即可
        },
    }

def h_v3_flash(log, topics_hex: List[str], data_bytes: bytes) -> Dict[str, Any]:
    # Flash(address indexed sender, address indexed recipient, uint256 amount0, uint256 amount1, uint256 paid0, uint256 paid1)
    return {
        "type": "v3_flash",
        "name": "UniV3.Flash",
        "contract": log["address"].lower(),
        "args": {
            "sender":    "0x" + topics_hex[1][-40:],
            "recipient": "0x" + topics_hex[2][-40:],
            "amount0":   uint256_at(data_bytes, 0),
            "amount1":   uint256_at(data_bytes, 1),
            "paid0":     uint256_at(data_bytes, 2),
            "paid1":     uint256_at(data_bytes, 3),
        },
    }


# builtin events registry
BUILTIN_EVENTS: Dict[str, Dict[str, Any]] = {
    # ERC20
    sig_topic("Transfer(address,address,uint256)"): {
        "name": "ERC20.Transfer", "sig": "Transfer(address,address,uint256)",
        "handler": h_erc20_transfer, "priority": 100,
    },
    sig_topic("Approval(address,address,uint256)"): {
        "name": "ERC20.Approval", "sig": "Approval(address,address,uint256)",
        "handler": h_erc20_approval, "priority": 95,
    },
    # ERC721/1155
    sig_topic("ApprovalForAll(address,address,bool)"): {
        "name": "ERC721.ApprovalForAll", "sig": "ApprovalForAll(address,address,bool)",
        "handler": h_erc721_approval_for_all, "priority": 94,
    },
    # V2
    sig_topic("Swap(address,uint256,uint256,uint256,uint256,address)"): {
        "name": "UniV2.Swap", "sig": "Swap(address,uint256,uint256,uint256,uint256,address)",
        "handler": h_v2_swap, "priority": 90,
    },
    sig_topic("Mint(address,uint256,uint256)"): {
        "name": "UniV2.Mint", "sig": "Mint(address,uint256,uint256)",
        "handler": h_v2_mint, "priority": 70,
    },
    sig_topic("Burn(address,uint256,uint256,address)"): {
        "name": "UniV2.Burn", "sig": "Burn(address,uint256,uint256,address)",
        "handler": h_v2_burn, "priority": 70,
    },
    sig_topic("Sync(uint112,uint112)"): {
        "name": "UniV2.Sync", "sig": "Sync(uint112,uint112)",
        "handler": h_v2_sync, "priority": 60,
    },
    # WBNB / WETH
    sig_topic("Deposit(address,uint256)"): {
        "name": "WBNB.Deposit", "sig": "Deposit(address,uint256)",
        "handler": h_wrap_deposit, "priority": 80,
    },
    sig_topic("Withdrawal(address,uint256)"): {
        "name": "WBNB.Withdrawal", "sig": "Withdrawal(address,uint256)",
        "handler": h_wrap_withdrawal, "priority": 80,
    },
    # V3
    sig_topic("Swap(address,address,int256,int256,uint160,uint128,int24)"): {
        "name": "UniV3.Swap", "sig": "Swap(address,address,int256,int256,uint160,uint128,int24)",
        "handler": h_v3_swap, "priority": 88,
    },
    sig_topic("Flash(address,address,uint256,uint256,uint256,uint256)"): {
        "name": "UniV3.Flash", "sig": "Flash(address,address,uint256,uint256,uint256,uint256)",
        "handler": h_v3_flash, "priority": 85,
    },
}

def build_registry(extra_paths: List[str] = None) -> Mapping[str, Mapping[str, Any]]:
    merged = dict(BUILTIN_EVENTS)
    if extra_paths:
        merged.update(load_extras(extra_paths))
    return make_readonly(merged)

def topic0_allowlist() -> list[str]:
    """List of all Buildin events"""
    return list(build_registry().keys())

def topic0_allowlist_minimal_v2() -> list[str]:
    """Minimum topic[0] list for ERC20 Transfer/Approval + UniV2/PancakeV2 Swap """
    sigs = [
        # "Transfer(address,address,uint256)",
        # "Approval(address,address,uint256)",
        "Swap(address,uint256,uint256,uint256,uint256,address)",
    ]
    topics = [sig_topic(s) for s in sigs]
    return list({t.lower() for t in topics})

def load_extras(paths: List[str]) -> Dict[str, Dict[str, Any]]:
    raise NotImplementedError("Fonctionality of load_extras should still be tested.")
    merged = {}
    for p in paths:
        if not p or not os.path.exists(p): 
            continue
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        for e in data:
            topic0 = e.get("topic0") or sig_topic(e["sig"])
            merged[topic0.lower()] = {
                "name": e.get("name"), "sig": e["sig"],
                "handler": e["handler"], "priority": e.get("priority", 50),
                **{k:v for k,v in e.items() if k not in {"name","sig","handler","priority","topic0"}}
            }
    return merged

def make_unknown_raw(tx: Dict[str, Any], receipt: Dict[str, Any], log: Dict[str, Any]) -> Dict[str, Any]:
    """Make unknown (un registered) events dictionary, in order to store to row database and consider to add or not in the registery.
    """
    topics_hex = [to_hexstr(t).lower() for t in log.get("topics", [])]
    data_hex = to_hexstr(log.get("data", "0x")).lower()
    return {
        "block_number": receipt.get("blockNumber"),
        "block_hash": to_hexstr(receipt.get("blockHash", "0x")).lower(),
        "tx_hash": to_hexstr(receipt.get("transactionHash", "0x")).lower(),
        "tx_index": receipt.get("transactionIndex"),
        "log_index": log.get("logIndex"),
        "address": log.get("address", "").lower(),
        "topic0": topics_hex[0] if topics_hex else None,
        "topics": topics_hex,
        "topics_count": len(topics_hex),
        "data_hex": data_hex,
        "data_len": (len(data_hex) - 2) // 2 if data_hex.startswith("0x") else 0,
        "removed": bool(log.get("removed", False)),
    }

# End of file
