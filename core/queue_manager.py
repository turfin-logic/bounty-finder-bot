"""
Queue Manager
Handles deduplication, priority scoring, and queue persistence.
Maps the user's Phantom payout wallets directly to target chains.
"""
import json
import logging
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DISCOVERED_FILE, PRIORITY_QUEUE_FILE, WALLETS

logger = logging.getLogger("QueueManager")

class QueueManager:
    def __init__(self):
        self.discovered = self._load_json(DISCOVERED_FILE, default=[])
        self.priority_queue = self._load_json(PRIORITY_QUEUE_FILE, default=[])

    def _load_json(self, path, default=None):
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error reading {path}: {e}")
        return default if default is not None else []

    def _save_json(self, path, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def attach_wallet(self, chain):
        chain_lower = chain.lower()
        if "solana" in chain_lower:
            return {"network": "Solana", "address": WALLETS["SOL"]}
        elif "bitcoin" in chain_lower or "btc" in chain_lower:
            return {"network": "Bitcoin (Taproot)", "address": WALLETS["BTC"]}
        else:
            return {"network": "Ethereum / EVM", "address": WALLETS["ETH"]}

    def calculate_actionability_score(self, target):
        """
        Score from 0 - 100 based on feasibility & payout speed:
        - Active competition with upcoming deadline: +40 (Guaranteed payout pool)
        - Direct GitHub repo available: +25
        - No KYC required: +20
        - Reward pool > $100k: +15
        """
        score = 0
        if "competition" in target["kind"].lower() or "contest" in target["kind"].lower():
            score += 40
        if target.get("github_repo"):
            score += 25
        if not target.get("requires_kyc", False):
            score += 20
        if target.get("reward_pool_usd", 0) >= 100000:
            score += 15
        return score

    def sync(self, new_targets):
        logger.info(f"Syncing {len(new_targets)} mined targets into queue...")
        
        discovered_map = {t["id"]: t for t in self.discovered}
        new_count = 0
        updated_count = 0

        for target in new_targets:
            tid = target["id"]
            target["payout_wallet"] = self.attach_wallet(target.get("chain", "Ethereum"))
            target["actionability_score"] = self.calculate_actionability_score(target)
            target["last_seen"] = datetime.utcnow().isoformat()

            if tid not in discovered_map:
                discovered_map[tid] = target
                new_count += 1
            else:
                # Update existing target info
                discovered_map[tid].update(target)
                updated_count += 1

        self.discovered = list(discovered_map.values())
        self._save_json(DISCOVERED_FILE, self.discovered)

        # Build priority queue: Filter out invalid, sort by actionability_score then reward
        priority = [t for t in self.discovered if t.get("status") in ["live", "active"]]
        priority.sort(key=lambda x: (x.get("actionability_score", 0), x.get("reward_pool_usd", 0)), reverse=True)
        
        self.priority_queue = priority
        self._save_json(PRIORITY_QUEUE_FILE, self.priority_queue)

        logger.info(f"Sync Complete: {new_count} new, {updated_count} updated. {len(self.priority_queue)} priority targets.")
        return {
            "total_discovered": len(self.discovered),
            "new_count": new_count,
            "priority_count": len(self.priority_queue)
        }

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    qm = QueueManager()
    print("Discovered count:", len(qm.discovered))
    print("Priority count:", len(qm.priority_queue))
