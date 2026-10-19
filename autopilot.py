"""
Bounty Finder Bot - Autonomous CLI Engine
Discovers genuine, high-payout Web3 bug bounties and audit contests.
No manual logins or KYC traps.
"""
import sys
import os
import argparse
import logging
import subprocess
from pathlib import Path
from tabulate import tabulate

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from config import WALLETS, PRIORITY_QUEUE_FILE, DISCOVERED_FILE, WORKSPACE_DIR
from sources.cantina_miner import CantinaMiner
from sources.immunefi_miner import ImmunefiMiner
from core.queue_manager import QueueManager
from core.vulnerability_scanner import VulnerabilityScanner
from core.report_generator import ReportGenerator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("BountyFinderBot")

def run_mine():
    print("\n" + "="*70)
    print("[BOUNTY FINDER BOT] INITIATING DEEP WEB3 BOUNTY MINING...")
    print("="*70 + "\n")

    qm = QueueManager()
    all_targets = []

    # 1. Mine Cantina (Live Competitions & Bug Bounties)
    try:
        cantina = CantinaMiner()
        c_targets = cantina.mine()
        all_targets.extend(c_targets)
    except Exception as e:
        logger.error(f"Cantina mining error: {e}")

    # 2. Mine Immunefi (Solana & EVM High-Reward Programs)
    try:
        immunefi = ImmunefiMiner()
        i_targets = immunefi.mine()
        all_targets.extend(i_targets)
    except Exception as e:
        logger.error(f"Immunefi mining error: {e}")

    # 3. Sync & Rank
    stats = qm.sync(all_targets)
    print("\n" + "-"*70)
    print(f"[OK] MINING COMPLETED: {stats['new_count']} New | {stats['priority_count']} Active Priority Targets Ranked.")
    print("-"*70)

    run_list()

def run_list():
    qm = QueueManager()
    queue = qm.priority_queue

    if not queue:
        print("\n[!] No priority targets found. Run with --mine first.")
        return

    table_data = []
    for i, t in enumerate(queue, 1):
        wallet_net = t.get("payout_wallet", {}).get("network", "EVM")
        table_data.append([
            f"#{i}",
            t.get("name", "Unknown")[:28],
            t.get("kind", "Bounty")[:18],
            f"${t.get('reward_pool_usd', 0):,}",
            t.get("chain", "Multi")[:10],
            f"{t.get('actionability_score', 0)}/100",
            wallet_net[:10]
        ])

    headers = ["#", "Protocol Name", "Type", "Reward Pool", "Chain", "Score", "Payout To"]
    print("\n" + tabulate(table_data, headers=headers, tablefmt="grid"))
    print("\n[*] Tip: Run 'python autopilot.py --target 1' to view full scope & submission details.")
    print("[*] Tip: Run 'python autopilot.py --scan 1' to run automated invariant bug scan.\n")

def run_target(target_index):
    qm = QueueManager()
    queue = qm.priority_queue

    try:
        idx = int(target_index) - 1
        target = queue[idx]
    except Exception:
        print(f"[ERROR] Invalid target index: {target_index}. Must be between 1 and {len(queue)}.")
        return

    print("\n" + "="*70)
    print(f"[TARGET INSPECTION] {target.get('name').upper()}")
    print("="*70)
    print(f"• Platform:       {target.get('platform')}")
    print(f"• Type:           {target.get('kind')}")
    print(f"• Reward Pool:    ${target.get('reward_pool_usd', 0):,} {target.get('currency')}")
    print(f"• Chain / Lang:   {target.get('chain')} ({target.get('in_scope_language', 'Solidity/Rust')})")
    print(f"• Action Score:   {target.get('actionability_score')}/100")
    print(f"• Target URL:     {target.get('url')}")
    print(f"• GitHub Repo:    {target.get('github_repo', 'N/A')}")
    print(f"• Assigned Payout Wallet:")
    print(f"    Network: {target.get('payout_wallet', {}).get('network')}")
    print(f"    Address: {target.get('payout_wallet', {}).get('address')}")
    print("="*70 + "\n")

def run_scan(target_index):
    qm = QueueManager()
    queue = qm.priority_queue

    try:
        idx = int(target_index) - 1
        target = queue[idx]
    except Exception:
        print(f"[ERROR] Invalid target index: {target_index}. Must be between 1 and {len(queue)}.")
        return

    repo_url = target.get("github_repo")
    if not repo_url:
        print(f"[ERROR] No GitHub repository linked for {target.get('name')}.")
        return

    print("\n" + "="*70)
    print(f"[VULNERABILITY SCANNER] TARGET: {target.get('name').upper()}")
    print("="*70)

    # Check local desktop clone first
    desktop_candidate = Path("C:/Users/pc/OneDrive/Desktop") / repo_url.split("/")[-1]
    scan_dir = None

    if desktop_candidate.exists():
        print(f"[+] Found existing local repository: {desktop_candidate}")
        scan_dir = desktop_candidate
    else:
        # Clone into workspace
        target_name = repo_url.split("/")[-1]
        scan_dir = WORKSPACE_DIR / target_name
        if not scan_dir.exists():
            print(f"[+] Cloning {repo_url} into {scan_dir}...")
            try:
                subprocess.run(["git", "clone", "--depth", "1", repo_url, str(scan_dir)], check=True)
            except Exception as e:
                print(f"[ERROR] Git clone failed: {e}")
                return

    scanner = VulnerabilityScanner()
    findings = scanner.scan_directory(scan_dir)

    print("\n" + "-"*70)
    print(f"[SCAN RESULTS] Found {len(findings)} Potential Invariant Violations in {scan_dir.name}:")
    print("-"*70)

    if not findings:
        print("No immediate pattern matches found.")
    else:
        finding_rows = []
        for i, f in enumerate(findings[:15], 1):
            finding_rows.append([
                f"#{i}",
                f.get("severity"),
                f.get("file"),
                f"L{f.get('line')}",
                f.get("title")[:40]
            ])
        print(tabulate(finding_rows, headers=["#", "Severity", "File", "Line", "Vulnerability Pattern"], tablefmt="grid"))
        print(f"\n[*] Total findings identified: {len(findings)} (showing top 15).")
    print("="*70 + "\n")

def run_status():
    qm = QueueManager()
    total_val = sum(t.get("reward_pool_usd", 0) for t in qm.priority_queue)

    print("\n" + "="*70)
    print("[BOUNTY FINDER BOT] SYSTEM STATUS")
    print("="*70)
    print(f"• Total Discovered Programs: {len(qm.discovered)}")
    print(f"• Active Priority Targets:   {len(qm.priority_queue)}")
    print(f"• Total Active Reward Pool:  ${total_val:,} USD")
    print("\n[REGISTERED PHANTOM WALLETS FOR DIRECT PAYOUTS]:")
    for net, addr in WALLETS.items():
        print(f"  [{net.ljust(4)}] : {addr}")
    print("="*70 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Autonomous Bounty Finder Bot")
    parser.add_argument("--mine", action="store_true", help="Mine all live Web3 bounties and audit contests")
    parser.add_argument("--list", action="store_true", help="List all priority targets in queue")
    parser.add_argument("--target", type=int, help="Inspect a specific target by list number (e.g. --target 1)")
    parser.add_argument("--scan", type=int, help="Run invariant vulnerability scanner on a target (e.g. --scan 1)")
    parser.add_argument("--status", action="store_true", help="View system status and registered payout wallets")

    args = parser.parse_args()

    if args.mine:
        run_mine()
    elif args.list:
        run_list()
    elif args.target:
        run_target(args.target)
    elif args.scan:
        run_scan(args.scan)
    elif args.status:
        run_status()
    else:
        # Default behavior: run mine and list
        run_mine()

if __name__ == "__main__":
    main()
