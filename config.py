"""
Bounty Finder Bot - Configuration
Global settings, wallet addresses, and filtering thresholds
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# User's Verified Phantom Payout Wallets
WALLETS = {
    "ETH": "0xe87b614ed54a14e61da996bdaed81e02045ba991",
    "BTC": "bc1p3wf3xk57jz59n6ajv5e3vwphlzqlhdepszeyh3yw0rw8uzxxphdsyakaed",
    "SOL": "9DFpYkzcWrCwiqWkrSDmU8KmCbf2yoJvVrdq8grBqFx9"
}

# Filtering Rules
MIN_BOUNTY_USD = 5000          # Ignore micro/dust bounties (< $5,000)
SUPPORTED_CHAINS = ["Solana", "Ethereum", "Arbitrum", "Base", "Polygon", "Multi-chain"]

# Storage Paths
QUEUE_DIR = BASE_DIR / "queue"
QUEUE_DIR.mkdir(exist_ok=True)

DISCOVERED_FILE = QUEUE_DIR / "bounties_discovered.json"
PRIORITY_QUEUE_FILE = QUEUE_DIR / "priority_targets.json"
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

WORKSPACE_DIR = BASE_DIR / "targets_workspace"
WORKSPACE_DIR.mkdir(exist_ok=True)

# User-Agent for ethical, high-reliability mining
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
