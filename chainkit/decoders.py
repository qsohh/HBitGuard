"""Decoder tools"""

from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple
from types import MappingProxyType
from hexbytes import HexBytes
from eth_utils import keccak, to_hex

def decode_address(data: str) -> str:
    """extract address from data string"""
    # adress from QuickNode logs-topics is string
    # if found bytes or HexBytes in the future, consider to fix it
    return "0x" + data[-40:]

def decode_uint256(data: str | bytes | bytearray) -> int:
    """extract uint256 from data with 0x-, or in HexBytes/bytes format"""
    if isinstance(data, (bytes, bytearray)):
        return int.from_bytes(data, byteorder="big")
    elif isinstance(data, str):
        if data.startswith("0x"):
            return int(data, 16)
        return int(data, 16)
    else:
        raise TypeError("Type error decode_unit256. Input should be str | bytes | bytearray")

def sig_topic(sig: str) -> str:
    """Event sig to topics[0]"""
    return to_hex(keccak(text=sig)).lower()

def to_hexstr(x) -> str:
    """HexBytes/bytes -> '0x...'; for string, return itself"""
    if isinstance(x, (bytes, bytearray, HexBytes)):
        return "0x" + bytes(x).hex()
    return str(x)

def to_bytes(x) -> bytes:
    if isinstance(x, (bytes, bytearray, HexBytes)):
        return bytes(x)
    if isinstance(x, str) and x.startswith("0x"):
        return bytes.fromhex(x[2:])
    raise TypeError(f"Unsupported type: {type(x)}")

def slice32(b: bytes, i: int) -> bytes:
    """Extract the i-st 32-bytes slice (0-based)"""
    start = 32 * i
    end = start + 32
    return b[start:end]

def uint256_at(b: bytes, i: int) -> int:
    return int.from_bytes(slice32(b, i), "big", signed=False)

def int256_at(b: bytes, i: int) -> int:
    return int.from_bytes(slice32(b, i), "big", signed=True)

def bool_at(b: bytes, i: int) -> bool:
    return uint256_at(b, i) != 0

def make_readonly(obj: Any | List | Dict | Mapping | set) -> Any:
    """
    list / tuple -> tuple, 
    dict / Mapping -> MappingProxyType,
    set -> frozenset,
    other -> unchanged
    """
    if isinstance(obj, (list, tuple)):
        return tuple(make_readonly(v) for v in obj)
    if isinstance(obj, Mapping): # Dict, Mapping, MappingProxyType
        return MappingProxyType({k: make_readonly(v) for k, v in obj.items()})
    if isinstance(obj, set):
        return frozenset(make_readonly(v) for v in obj)
    return obj

if __name__ == "__main__":
    pass

# End of file