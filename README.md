# 🛡️ BountyFinder Bot

> Autonomous Web3 Bug Bounty & Smart Contract Audit Competition Intelligence Engine.

BountyFinder Bot is a zero-login, automated discovery and vulnerability assessment system tailored for Web3 security researchers, whitehats, and DeFi auditors. It mines active on-chain escrow bounty pools, ranks targets by feasibility and payout value, and scans smart contract codebases for critical DeFi invariant violations.

---

## ⚡ Features

- **Zero-Login Deep Mining:** Mines verified on-chain prize pools and audit competitions from Cantina and Immunefi without requiring manual account registration, KYC dashboards, or submission fees.
- **Automated Wallet Assignment:** Maps target blockchain ecosystems directly to designated payout wallets:
  - **Solana:** Auto-assigned for Rust/Anchor programs.
  - **Ethereum / EVM:** Auto-assigned for Solidity pools (Ethereum, Arbitrum, Base, Polygon).
  - **Bitcoin:** Auto-assigned for Taproot/DLC protocols.
- **Actionability Scoring Engine:** Ranks targets (0-100) based on active deadlines, open-source code availability, and pool liquidity.
- **Automated Invariant Scanner:**
  - Clones in-scope smart contract repositories.
  - Detects reentrancy vectors, spot oracle TWAP manipulation risks, division-before-multiplication precision loss, and missing Solana signer checks.
- **Submission Report Generator:** Automatically generates standardized vulnerability reports including severity assessment, root cause analysis, PoC structure, and mitigation guidance.

---

## 🚀 Quick Start

### 1. Requirements
- Python 3.10+
- Git

Install dependencies:
```bash
pip install tabulate
```

### 2. Run Autonomous Mining & Discovery
```bash
python autopilot.py --mine
```
This fetches live competitions and bug bounties, updates `queue/priority_targets.json`, and displays the ranked dashboard.

### 3. View Priority Target Queue
```bash
python autopilot.py --list
```

### 4. Inspect Target Details & Scope
```bash
python autopilot.py --target 1
```

### 5. Run Invariant Vulnerability Scan on a Target
```bash
# Example: Scan Target #1 (e.g. Revert v4lend Uniswap v4 contracts)
python autopilot.py --scan 1

# Example: Scan Target #5 (e.g. Raydium Solana Rust contracts)
python autopilot.py --scan 5
```

### 6. View System Status
```bash
python autopilot.py --status
```

---

## 📁 Project Architecture

```
bounty-finder-bot/
├── autopilot.py                # Main CLI execution engine
├── config.py                   # Global thresholds, paths, and payout wallet configuration
├── .gitignore                  # Clean repository hygiene
├── sources/
│   ├── cantina_miner.py        # Stream miner for Cantina competitions & bounties
│   └── immunefi_miner.py       # Catalog miner for Immunefi Solana & EVM programs
├── core/
│   ├── queue_manager.py        # Deduplication, scoring, and priority queue persistence
│   ├── vulnerability_scanner.py # Static pattern analyzer for Solidity and Rust
│   └── report_generator.py     # Markdown submission report builder
└── queue/
    ├── bounties_discovered.json # Master database of all discovered bounties
    └── priority_targets.json    # Filtered, scored, and ranked actionable targets
```

---

## 🔒 Security & Privacy Notice
This tool is built strictly for defensive code auditing, protocol verification, and authorized whitehat bug bounty research. All target information is derived from public bug bounty disclosures.

---
*Created by turfin-logic*
