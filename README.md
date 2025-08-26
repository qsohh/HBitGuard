# HBitGuard

A lightweight Python toolkit for monitoring and decoding on-chain events on **BNB Smart Chain (BSC)**. It may help tracking complete chain of transactions in order to analyze any abnormal signal or eventual web3 attacking events.

It supports minimal ERC20/721/Uniswap V2/V3/WBNB ABI, event registry, transaction tracking and a simple runner loop.

## Features

- Minimal ABI collection for common standards (ERC20, ERC721, Uniswap V2/V3, WBNB).
- Built-in event registry with handlers for `Transfer`, `Approval`, `Swap`, `Mint`, `Burn`, `Deposit`, `Withdrawal`, `Flash`.
- Transaction analysis into normalized events and unknown raw events.
- Runner loop with block window, safe head confirmations, deduplication of tx hashes.
- Easy extension for ABIs and customized event handler.

## Project Structure

```text
chainkit/               # Core toolkit
|── sql/                # Placeholder for PostgreSQL database schema
|    └── schema.sql     # Currently empty, TODO for CREATE TABLE
├── collector.py        # Collect logs / tx hashes from blockchain
├── decoders.py         # Decode helpers (uint256, address, etc.)
├── min_abi.py          # Minimal ABIs for ERC20/721, V2/V3 pools, WBNB
├── registry_event.py   # Builtin event registry & handlers
├── runner.py           # Runner class for continuous monitoring
├── tx_tracker.py       # Transaction analyzer (decode logs into events)
└── __init__.py         # Package entry, re-exports key functions

demo/                   # Demo scripts
├── demo.py             # Run runner loop with minimal topics
└── demo_tx_tracker.py  # Analyze a single transaction
```

## Requirements

- web3
- python-dotenv
- eth-utils
- hexbytes

> **Note:** web3 version **7.0.0 or higher** is required, since the API has changed to use `snake_case` parameters.

## Quick Start

1. Install dependencies (see `requirements.txt`)
2. Set RPC URL
   - Create a `.env` file (reference: `sample.env`)
   ```ini
   RPC_URL=https://your-bsc-rpc-url
   ```
   - It is recommended to use your own RPC_URL (even if its free level)
3. Run demos
   - Real time scan and track transactions
   ```bash
   python -m demo.demo
   ```
   - Example of transaction tracker
   ```bash
   python -m demo.demo_tx_tracker
   ```
   - Directly call runner or tx_tracker
   ```bash
   python -m chainkit.runner
   ```
   or
   ```bash
   python -m chainkit.tx_tracker [0xyourtxhash]
   ```

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.