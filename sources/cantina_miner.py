"""
Cantina Miner
Extracts live smart contract audit competitions and public bug bounties from Cantina.
No login required - parses public data stream.
"""
import re
import json
import urllib.request
import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import USER_AGENT, MIN_BOUNTY_USD

logger = logging.getLogger("CantinaMiner")

class CantinaMiner:
    def __init__(self):
        self.url = "https://cantina.xyz/competitions"
        self.headers = {"User-Agent": USER_AGENT}

    def mine(self):
        logger.info("Fetching Cantina live competitions and bounties...")
        try:
            req = urllib.request.Request(self.url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read().decode("utf-8")
        except Exception as e:
            logger.error(f"Failed to fetch Cantina page: {e}")
            return []

        targets = []
        seen_ids = set()

        # Find all totalRewardPot occurrences
        matches = [m.start() for m in re.finditer(r'totalRewardPot', html)]
        
        for idx in matches:
            chunk = html[max(0, idx - 1000):min(len(html), idx + 1000)]
            
            # Match UUID
            id_m = re.search(r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})', chunk)
            target_id = id_m.group(1) if id_m else None
            if not target_id or target_id in seen_ids:
                continue

            # Match pot: totalRewardPot followed by escaped or unescaped digits
            pot_m = re.search(r'totalRewardPot[^0-9]*([0-9]{4,10})', chunk)
            if not pot_m:
                continue
            
            reward_amount = int(pot_m.group(1))
            if reward_amount < MIN_BOUNTY_USD:
                continue

            # Is competition or bounty?
            is_competition = "public_contest" in chunk or "competitions/" in chunk
            kind = "Competition / Audit Contest" if is_competition else "Bug Bounty"

            # Check status
            status = "live" if "live" in chunk else "active"

            # Extract Name
            # Cantina stores company name or title in escaped format
            name_m = re.findall(r'name\\+[\"\']+:\s*\\+[\"\']+([^\\\"\']+)', chunk)
            handle_m = re.findall(r'handle\\+[\"\']+:\s*\\+[\"\']+([^\\\"\']+)', chunk)
            
            name = None
            if name_m:
                for candidate in name_m:
                    if candidate.lower() not in ["smart contracts", "out of scope", "contracts", "tier 1"]:
                        name = candidate
                        break
            if not name and handle_m:
                name = handle_m[0]
            if not name:
                name = f"Protocol-{target_id[:8]}"

            # Specific known ID enrichments
            if "e275368c" in target_id:
                name = "Revert Finance (Revert v4lend)"
                kind = "Competition / Audit Contest"
            elif "f9df94db" in target_id:
                name = "Uniswap Labs"
            elif "ff945ca2" in target_id:
                name = "Polymarket"
            elif "55316f42" in target_id:
                name = "Coinbase Protocols"
            elif "35a5f0a1" in target_id:
                name = "Morpho Protocol"
            elif "5ffa2a58" in target_id:
                name = "Ondo Perps"
            elif "4d285eee" in target_id:
                name = "Euler Finance"
            elif "83b38645" in target_id:
                name = "dYdX"
            elif "2acbecd1" in target_id:
                name = "Robinhood Web3"

            # URLs
            target_url = f"https://cantina.xyz/competitions/{target_id}" if is_competition else f"https://cantina.xyz/bounties/{target_id}"

            # GitHub repo extraction
            repo_m = re.findall(r'https://github\.com/([a-zA-Z0-9_\-]+/[a-zA-Z0-9_\-]+)', chunk)
            github_repo = f"https://github.com/{repo_m[0]}" if repo_m else None
            if "e275368c" in target_id:
                github_repo = "https://github.com/revert-finance/v4lend"

            # Chain
            chain = "Ethereum / EVM"
            if "solana" in chunk.lower() or "raydium" in name.lower():
                chain = "Solana"
            elif "polygon" in chunk.lower():
                chain = "Polygon"
            elif "arbitrum" in chunk.lower():
                chain = "Arbitrum"

            target = {
                "id": f"cantina_{target_id}",
                "target_uuid": target_id,
                "platform": "Cantina",
                "name": name,
                "kind": kind,
                "reward_pool_usd": reward_amount,
                "currency": "USDC",
                "chain": chain,
                "status": status,
                "url": target_url,
                "github_repo": github_repo,
                "requires_kyc": "kycRequired\\\":true" in chunk or "kycRequired\":true" in chunk
            }

            seen_ids.add(target_id)
            targets.append(target)

        # Sort by reward descending
        targets.sort(key=lambda x: x["reward_pool_usd"], reverse=True)
        logger.info(f"Cantina Miner extracted {len(targets)} verified high-payout opportunities.")
        return targets

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    miner = CantinaMiner()
    results = miner.mine()
    print(f"Total targets mined: {len(results)}")
    for r in results:
        print(f" - [{r['kind']}] {r['name']}: ${r['reward_pool_usd']:,} {r['currency']} ({r['chain']}) -> {r['url']}")
