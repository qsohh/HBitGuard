"""MInimum ABI
"""
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple
from types import MappingProxyType
import copy

from .decoders import make_readonly, sig_topic

# ---------------- ERC-20 ----------------
ERC20_MIN_ABI = [
    # read
    {"name":"decimals","inputs":[],"outputs":[{"type":"uint8","name":""}],
     "stateMutability":"view","type":"function"},
    {"name":"symbol","inputs":[],"outputs":[{"type":"string","name":""}],
     "stateMutability":"view","type":"function"},
    {"name":"name","inputs":[],"outputs":[{"type":"string","name":""}],
     "stateMutability":"view","type":"function"},
    {"name":"totalSupply","inputs":[],"outputs":[{"type":"uint256","name":""}],
     "stateMutability":"view","type":"function"},
    {"name":"balanceOf","inputs":[{"type":"address","name":"owner"}],
     "outputs":[{"type":"uint256","name":""}],"stateMutability":"view","type":"function"},
    {"name":"allowance","inputs":[{"type":"address","name":"owner"},{"type":"address","name":"spender"}],
     "outputs":[{"type":"uint256","name":""}],"stateMutability":"view","type":"function"},
    # events
    {"anonymous":False,"type":"event","name":"Transfer",
     "inputs":[
        {"indexed":True,"name":"from","type":"address"},
        {"indexed":True,"name":"to","type":"address"},
        {"indexed":False,"name":"value","type":"uint256"}]},
    {"anonymous":False,"type":"event","name":"Approval",
     "inputs":[
        {"indexed":True,"name":"owner","type":"address"},
        {"indexed":True,"name":"spender","type":"address"},
        {"indexed":False,"name":"value","type":"uint256"}]},
]

# ------------- ERC-721 -------------
ERC721_MIN_ABI = [
    {"name":"ownerOf","inputs":[{"type":"uint256","name":"tokenId"}],
     "outputs":[{"type":"address","name":""}],"stateMutability":"view","type":"function"},
    {"name":"isApprovedForAll","inputs":[{"type":"address","name":"owner"},{"type":"address","name":"operator"}],
     "outputs":[{"type":"bool","name":""}],"stateMutability":"view","type":"function"},
    {"anonymous":False,"type":"event","name":"Transfer",
     "inputs":[
        {"indexed":True,"name":"from","type":"address"},
        {"indexed":True,"name":"to","type":"address"},
        {"indexed":True,"name":"tokenId","type":"uint256"}]},
    {"anonymous":False,"type":"event","name":"ApprovalForAll",
     "inputs":[
        {"indexed":True,"name":"owner","type":"address"},
        {"indexed":True,"name":"operator","type":"address"},
        {"indexed":False,"name":"approved","type":"bool"}]},
]

# --------- WBNB / WETH ----------
WETH_MIN_ABI = [
    # for the functions, reuse ERC20_MIN_ABI
    {"anonymous":False,"type":"event","name":"Deposit",
     "inputs":[
        {"indexed":True,"name":"dst","type":"address"},
        {"indexed":False,"name":"wad","type":"uint256"}]},
    {"anonymous":False,"type":"event","name":"Withdrawal",
     "inputs":[
        {"indexed":True,"name":"src","type":"address"},
        {"indexed":False,"name":"wad","type":"uint256"}]},
]

# -------- UniswapV2 / PancakeV2 Pair -------
UNIV2_PAIR_MIN_ABI = [
    # read
    {"name":"token0","inputs":[],"outputs":[{"type":"address","name":""}],
     "stateMutability":"view","type":"function"},
    {"name":"token1","inputs":[],"outputs":[{"type":"address","name":""}],
     "stateMutability":"view","type":"function"},
    {"name":"getReserves","inputs":[],"outputs":[
        {"type":"uint112","name":"_reserve0"},
        {"type":"uint112","name":"_reserve1"},
        {"type":"uint32","name":"_blockTimestampLast"}],
     "stateMutability":"view","type":"function"},
    # events
    {"anonymous":False,"type":"event","name":"Swap",
     "inputs":[
        {"indexed":True,"name":"sender","type":"address"},
        {"indexed":False,"name":"amount0In","type":"uint256"},
        {"indexed":False,"name":"amount1In","type":"uint256"},
        {"indexed":False,"name":"amount0Out","type":"uint256"},
        {"indexed":False,"name":"amount1Out","type":"uint256"},
        {"indexed":True,"name":"to","type":"address"}]},
    {"anonymous":False,"type":"event","name":"Mint",
     "inputs":[
        {"indexed":True,"name":"sender","type":"address"},
        {"indexed":False,"name":"amount0","type":"uint256"},
        {"indexed":False,"name":"amount1","type":"uint256"}]},
    {"anonymous":False,"type":"event","name":"Burn",
     "inputs":[
        {"indexed":True,"name":"sender","type":"address"},
        {"indexed":False,"name":"amount0","type":"uint256"},
        {"indexed":False,"name":"amount1","type":"uint256"},
        {"indexed":True,"name":"to","type":"address"}]},
    {"anonymous":False,"type":"event","name":"Sync",
     "inputs":[
        {"indexed":False,"name":"reserve0","type":"uint112"},
        {"indexed":False,"name":"reserve1","type":"uint112"}]},
]

UNIV2_FACTORY_MIN_ABI = [
    {"name":"getPair","inputs":[{"type":"address","name":"tokenA"},{"type":"address","name":"tokenB"}],
     "outputs":[{"type":"address","name":"pair"}],"stateMutability":"view","type":"function"},
]

# ------------- UniswapV3 / PancakeV3 --------------
UNIV3_POOL_MIN_ABI = [
    # read
    {"name":"token0","inputs":[],"outputs":[{"type":"address","name":""}],
     "stateMutability":"view","type":"function"},
    {"name":"token1","inputs":[],"outputs":[{"type":"address","name":""}],
     "stateMutability":"view","type":"function"},
    {"name":"fee","inputs":[],"outputs":[{"type":"uint24","name":""}],
     "stateMutability":"view","type":"function"},
    {"name":"liquidity","inputs":[],"outputs":[{"type":"uint128","name":""}],
     "stateMutability":"view","type":"function"},
    {"name":"slot0","inputs":[],"outputs":[
        {"type":"uint160","name":"sqrtPriceX96"},
        {"type":"int24","name":"tick"},
        {"type":"uint16","name":"observationIndex"},
        {"type":"uint16","name":"observationCardinality"},
        {"type":"uint16","name":"observationCardinalityNext"},
        {"type":"uint8","name":"feeProtocol"},
        {"type":"bool","name":"unlocked"}],
     "stateMutability":"view","type":"function"},
    {"anonymous":False,"type":"event","name":"Swap",
     "inputs":[
        {"indexed":True,"name":"sender","type":"address"},
        {"indexed":True,"name":"recipient","type":"address"},
        {"indexed":False,"name":"amount0","type":"int256"},
        {"indexed":False,"name":"amount1","type":"int256"},
        {"indexed":False,"name":"sqrtPriceX96","type":"uint160"},
        {"indexed":False,"name":"liquidity","type":"uint128"},
        {"indexed":False,"name":"tick","type":"int24"}]},
    {"anonymous":False,"type":"event","name":"Flash",
     "inputs":[
        {"indexed":True,"name":"sender","type":"address"},
        {"indexed":True,"name":"recipient","type":"address"},
        {"indexed":False,"name":"amount0","type":"uint256"},
        {"indexed":False,"name":"amount1","type":"uint256"},
        {"indexed":False,"name":"paid0","type":"uint256"},
        {"indexed":False,"name":"paid1","type":"uint256"}]},
]

UNIV3_FACTORY_MIN_ABI = [
    {"name":"getPool","inputs":[
        {"type":"address","name":"tokenA"},
        {"type":"address","name":"tokenB"},
        {"type":"uint24","name":"fee"}],
     "outputs":[{"type":"address","name":"pool"}],
     "stateMutability":"view","type":"function"}
]

def _abi_item_key(item: Mapping[str, Any]) -> Tuple[Any, ...]:
    """
    Generate a key using to avoid repetition.
    - function/event: ('function'/'event', name, (input_type0, input_type1, ...))
    - Other types: ('type', name)
    """
    t = item.get("type")
    name = item.get("name", "")
    if t in ("function", "event"):
        inputs = item.get("inputs", []) or []
        in_types = tuple((arg or {}).get("type", "") for arg in inputs)
        return (t, name, in_types)
    return (t, name)

def get_readonly_abi(fundamental_abi: Iterable[Mapping[str, Any]], extra_abi: Optional[Iterable[Mapping[str, Any]]] = None) -> tuple[MappingProxyType]:
    """
    Generate a readonly minimum ABI with optional extra ABI, avoiding external modification.
    - Any repeated ABI in extra with those in fundamental ABI is dropped
    - return a tuple[MappingProxyType] which is not modifiable.
    """
    combined: List[Dict[str, Any]] = []
    seen = set()

    # Minimum ABI
    for item in fundamental_abi:
        key = _abi_item_key(item)
        if key not in seen:
            combined.append(copy.deepcopy(dict(item)))
            seen.add(key)

    # Optional extra ABI
    if extra_abi:
        for item in extra_abi:
            if not isinstance(item, Mapping):
                # raise ValueError("Non-mapping item exists in extra ABI.")
                continue
            key = _abi_item_key(item)
            if key in seen:
                continue  # Skipping repeated ABI item
            combined.append(copy.deepcopy(dict(item)))
            seen.add(key)
    return make_readonly(combined)

def get_erc20_abi(extra_abi: Optional[Iterable[Mapping[str, Any]]] = None) -> tuple[MappingProxyType]:
    return get_readonly_abi(ERC20_MIN_ABI, extra_abi)

def get_v2_factory_abi(extra_abi: Optional[Iterable[Mapping[str, Any]]] = None) -> tuple[MappingProxyType]:
    return get_readonly_abi(UNIV2_FACTORY_MIN_ABI, extra_abi)

def get_v2_pair_abi(extra_abi: Optional[Iterable[Mapping[str, Any]]] = None) -> tuple[MappingProxyType]:
    return get_readonly_abi(UNIV2_PAIR_MIN_ABI, extra_abi)

def get_weth_abi(extra_abi: Optional[Iterable[Mapping[str, Any]]] = None) -> tuple[MappingProxyType]:
    merged_extra = list(WETH_MIN_ABI)
    if extra_abi:
        merged_extra.extend(list(extra_abi))
    return get_readonly_abi(ERC20_MIN_ABI, merged_extra)

def topics_from_abi(abi: list[dict]) -> list[str]:
    """Generate a list of topics[0] from all events"""
    out = []
    for it in abi:
        if (it or {}).get("type") != "event":
            continue
        name = it.get("name")
        ins  = it.get("inputs", []) or []
        sig  = f"{name}({','.join(arg.get('type','') for arg in ins)})"
        out.append(sig_topic(sig))
    return out

def default_topics_from_min_abi() -> list[str]:
    topics: List[str] = []
    topics += topics_from_abi(ERC20_MIN_ABI)
    topics += topics_from_abi(UNIV2_PAIR_MIN_ABI)
    return list({t.lower() for t in topics})

def _test_min_abi() -> None:
    APPROVE_FN = {
    "name": "approve",
    "inputs": [{"type": "address", "name": "spender"}, {"type": "uint256", "name": "amount"}],
    "outputs": [{"type": "bool", "name": ""}],
    "stateMutability": "nonpayable",
    "type": "function",
    }
    erc_abi = get_erc20_abi(WETH_MIN_ABI + [APPROVE_FN])
    for ele in erc_abi:
        for k, v in ele.items():
            print(k, v)
    try:
        erc_abi[0]["name"] = "changed name"
    except TypeError as e:
        print("checked readonly: ", e)

if __name__ == "__main__":
    _test_min_abi()

# End of file