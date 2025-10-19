
from typing import Optional, Iterable, Set, List
from web3 import Web3
from collections import deque
import json, os, time

from .registry_event import topic0_allowlist_minimal_v2
from .tx_tracker import analyze_tx
from .collector import collect_tx_hashes, PANCAKE_V2_BCFX_BUSD_ADDR

class DequeSet:
    """Fixed volume deque + set to store detected tx hashes"""
    def __init__(self, capacity: int=20000):
        self.capacity = int(capacity)
        self._dq = deque(maxlen=capacity)
        self._set: Set[str] = set()

    def add(self, key: str) -> bool:
        """Add new tx hash, return False if tx hash already stored"""
        if key in self._set:
            return False
        if len(self._dq) == self._dq.maxlen and self._dq:
            old = self._dq.popleft()
            # When necessary, make additional proceed for old tx hash
            self._set.discard(old)
        self._dq.append(key)
        self._set.add(key)
        return True

    def __contains__(self, key: str) -> bool:
        return key in self._set

    def to_list(self) -> List[str]:
        return list(self._dq)

    @classmethod
    def from_list(cls, items: Iterable[str], capacity: int=20000) -> "DequeSet":
        inst = cls(capacity)
        for k in items:
            inst.add(k)
        return inst

class Runner:
    def __init__(self, w3: Web3, window: int=5, confirmations: int=3, sleep_secs: float=10.0, max_seen: int=20000, overlap_blocks: int=0, store_tx_hashes: bool=False, store_tx_analyze: bool=False, state_path: Optional[str]=None, topics: Optional[List[str]]=None):
        self.w3 = w3
        self.window = int(window)
        self.confirmations = int(confirmations)
        self.sleep_secs = sleep_secs
        self.overlap_blocks = int(overlap_blocks) # Allow slight overlapping when requesting blocks
        self.store_tx_hashes = store_tx_hashes
        self.store_tx_analyze = store_tx_analyze
        self.seen = DequeSet(max_seen)
        self.state_path = state_path
        self.topics = topics
        self.last_safe_head: Optional[int] = None

        # Allow continue guarding from state file
        if self.state_path and os.path.exists(self.state_path):
            try:
                with open(self.state_path, "r", encoding="utf-8") as f:
                    st = json.load(f)
                self.last_safe_head = st.get("last_safe_head")
                self.seen = DequeSet.from_list(
                    st.get("seen_tx", []),
                    capacity=st.get("max_seen", max_seen),
                )
                print(f"[runner] restored last_safe_head={self.last_safe_head}, seen={len(self.seen.to_list())}")
            except Exception as e:
                print(f"[runner] restore failed: {e}")

    def _safe_head(self) -> int:
        latest = self.w3.eth.block_number
        return max(0, latest - self.confirmations)

    def _range_this_round(self, safe_head: int) -> tuple[int, int]:
        """
        This round we are going to demand information from start to safe_head
        - Basically: [safe_head - window + 1, safe_head]
        - Overlapping: Allow overlap blocks before last_safe_head
        """
        if self.last_safe_head is not None and safe_head <= self.last_safe_head:
            return -1, -2

        end = safe_head
        base_start = max(0, end - (self.window - 1))

        if self.last_safe_head is None:
            candidate = max(0, end - (self.window - 1 + self.overlap_blocks))
        else:
            candidate = max(0, self.last_safe_head + 1 - self.overlap_blocks)

        start = max(base_start, candidate)

        max_span = self.window
        if end - start + 1 > max_span:
            start = end - (max_span - 1)
            if start < 0:
                start = 0
        return start, end

    def _save_state(self) -> None:
        if not self.state_path:
            return
        data = {
            "last_safe_head": self.last_safe_head,
            "seen_tx": self.seen.to_list(),
            "dedup_capacity": self.seen.capacity,
        }
        tmp = self.state_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f)
        os.replace(tmp, self.state_path)

    def proceed(self) -> int:
        safe = self._safe_head()
        if self.last_safe_head is not None and safe <= self.last_safe_head:
            # print(f"[runner] no new safe head ({safe}), skip")
            return 0

        b0, b1 = self._range_this_round(safe)
        if b0 > b1:
            return 0

        # print(f"DEBUG range: [{b0}, {b1}] span={b1-b0+1} window={self.window} overlap={self.overlap_blocks}")
        cand = collect_tx_hashes(self.w3, [PANCAKE_V2_BCFX_BUSD_ADDR], b0, b1, topics=self.topics)
        todo = [h for h in cand if h not in self.seen]

        out = [analyze_tx(self.w3, h, save_data=self.store_tx_analyze) for h in todo]
        for h in todo:
            self.seen.add(h)

        self.last_safe_head = b1
        self._save_state()
        print(f"[runner] blocks [{b0},{b1}] candidates={len(cand)} processed={len(out)}")
        return len(out)

    def run_loop(self) -> None:
        print(f"[runner] loop start: window={self.window}, conf={self.confirmations}, interval={self.sleep_secs}s")
        try:
            while True:
                try:
                    self.proceed()
                except Exception as e:
                    print(f"[runner] step error: {e}")
                time.sleep(self.sleep_secs)
        except KeyboardInterrupt:
            print("[runner] stopped")

def _test_runner():
    import os, json
    from dotenv import load_dotenv
    load_dotenv()

    RPC_URL = os.environ["RPC_URL"]
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    ALLOW_TOPICS0 = topic0_allowlist_minimal_v2()

    runner = Runner(w3, window=5, overlap_blocks=2, sleep_secs=10, max_seen=50, topics=ALLOW_TOPICS0)
    runner.run_loop()

if __name__ == "__main__":
    _test_runner()

# End of file