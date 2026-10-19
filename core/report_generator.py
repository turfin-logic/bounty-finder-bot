"""
Report Generator
Builds submission-ready bug disclosure reports including impact,
affected lines, PoC template, and the user's Phantom payout wallet.
"""
import sys
import os
from pathlib import Path
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import REPORTS_DIR, WALLETS

class ReportGenerator:
    def __init__(self):
        self.output_dir = REPORTS_DIR

    def generate(self, target, finding_details):
        """
        Generates markdown vulnerability report ready for submission.
        """
        title = finding_details.get("title", "High-Severity Vulnerability Finding")
        severity = finding_details.get("severity", "HIGH")
        contract = finding_details.get("contract", "TargetContract.sol")
        line = finding_details.get("line", "TBD")
        description = finding_details.get("description", "Vulnerability analysis...")
        impact = finding_details.get("impact", "Loss of funds or protocol denial of service.")
        poc = finding_details.get("poc", "// Proof of Concept code here")
        mitigation = finding_details.get("mitigation", "Ensure validation before execution.")
        
        # Payout wallet assignment
        wallet_info = target.get("payout_wallet", {"network": "Ethereum / EVM", "address": WALLETS["ETH"]})

        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        slug = target.get("name", "target").lower().replace(" ", "_").replace("(", "").replace(")", "")
        filename = f"{slug}_{severity.lower()}_report.md"
        filepath = self.output_dir / filename

        content = f"""# Bug Bounty Vulnerability Submission: {title}

**Target Protocol:** {target.get('name')}  
**Platform:** {target.get('platform', 'Cantina / Immunefi')}  
**Target URL:** {target.get('url')}  
**Severity:** [{severity}]  
**Affected Contract:** `{contract}` (Line: {line})  
**Submission Date:** {timestamp}  

---

## 💰 Payout Wallet Information (Phantom)
- **Designated Network:** {wallet_info.get('network')}
- **Payout Address:** `{wallet_info.get('address')}`

---

## 1. Vulnerability Summary
{description}

---

## 2. Vulnerability Details & Root Cause
In `{contract}`, the function logic fails to handle the required security invariants.
Specifically:
```solidity
// Vulnerable snippet reference
{finding_details.get('snippet', '// Refer to contract source')}
```

When this condition occurs under specific market/call states, an attacker or standard protocol user can trigger unexpected reverts or state desynchronization.

---

## 3. Impact Analysis
**Estimated Severity:** **{severity}**  
**Direct Impact:**  
{impact}

- **Funds at Risk:** Up to maximum protocol pool value.
- **Attack Feasibility:** Deterministic execution without special permissions.

---

## 4. Proof of Concept (PoC)
```solidity
{poc}
```

---

## 5. Recommended Mitigation
{mitigation}

---
*Report generated automatically by BountyFinder Bot.*
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return filepath
