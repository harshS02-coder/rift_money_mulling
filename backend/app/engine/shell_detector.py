"""
Shell Account Detection Module
Identifies accounts with high-value throughput but minimal transaction history.
"""
from typing import List, Dict
from app.schemas.transaction import Transaction


class ShellAccountDetector:
    """Detects shell accounts (pass-through with few transactions)"""

    def __init__(self, transactions: List[Transaction]):
        self.transactions = transactions
        self.account_stats = self._calculate_account_stats()

    def _calculate_account_stats(self) -> Dict[str, Dict]:
        """Calculate statistics for each account"""
        stats = {}
        
        for txn in self.transactions:
            # From account stats
            if txn.from_account not in stats:
                stats[txn.from_account] = {
                    "transactions": [],
                    "total_out": 0,
                    "total_in": 0,
                    "unique_destinations": set(),
                    "unique_sources": set()
                }
            
            stats[txn.from_account]["transactions"].append(txn)
            stats[txn.from_account]["total_out"] += txn.amount
            stats[txn.from_account]["unique_destinations"].add(txn.to_account)
            
            # To account stats
            if txn.to_account not in stats:
                stats[txn.to_account] = {
                    "transactions": [],
                    "total_out": 0,
                    "total_in": 0,
                    "unique_destinations": set(),
                    "unique_sources": set()
                }
            
            stats[txn.to_account]["transactions"].append(txn)
            stats[txn.to_account]["total_in"] += txn.amount
            stats[txn.to_account]["unique_sources"].add(txn.from_account)
        
        return stats

    def detect_shell_accounts(self, max_transactions: int = 5, 
                             min_total_value: float = 50000) -> List[Dict]:
        """
        Detect shell accounts:
        - Very few transactions (1-5)
        - High total throughput (>50k)
        - High average transaction value
        """
        shell_accounts = []
        
        for account_id, stats in self.account_stats.items():
            txn_count = len(stats["transactions"])
            total_throughput = stats["total_in"] + stats["total_out"]
            
            # Check shell account criteria
            if txn_count <= max_transactions and total_throughput >= min_total_value:
                avg_value = total_throughput / txn_count if txn_count > 0 else 0
                
                shell_accounts.append({
                    "account_id": account_id,
                    "total_transactions": txn_count,
                    "total_throughput": total_throughput,
                    "avg_transaction_value": avg_value,
                    "transactions_in": len([t for t in stats["transactions"] 
                                          if t.to_account == account_id]),
                    "transactions_out": len([t for t in stats["transactions"] 
                                           if t.from_account == account_id]),
                    "unique_sources": len(stats["unique_sources"]),
                    "unique_destinations": len(stats["unique_destinations"]),
                    "high_value_ratio": (avg_value / total_throughput) if total_throughput > 0 else 0
                })
        
        # Sort by throughput/transaction ratio
        shell_accounts.sort(key=lambda x: x["avg_transaction_value"], reverse=True)
        
        return shell_accounts

    def detect_pass_through_accounts(self, min_value: float = 100000,
                                    tolerance: float = 0.1) -> List[Dict]:
        """
        Detect pass-through accounts:
        - Receive and immediately forward (similar amounts in/out)
        - Few unique sources/destinations
        """
        pass_through = []
        
        for account_id, stats in self.account_stats.items():
            total_in = stats["total_in"]
            total_out = stats["total_out"]
            
            if total_in > 0 and total_out > 0:
                ratio = total_out / total_in if total_in > 0 else 0
                diff = abs(total_in - total_out)
                
                # Check if amounts are very similar (pass-through indicator)
                if (min_value <= total_in <= min_value * 2 and 
                    min_value <= total_out <= min_value * 2 and
                    0.9 <= ratio <= 1.1 and
                    diff < total_in * tolerance):
                    
                    pass_through.append({
                        "account_id": account_id,
                        "total_in": total_in,
                        "total_out": total_out,
                        "in_out_ratio": ratio,
                        "difference": diff,
                        "unique_sources": len(stats["unique_sources"]),
                        "unique_destinations": len(stats["unique_destinations"]),
                        "transactions_count": len(stats["transactions"]),
                        "likelihood": 1.0 - (diff / total_in if total_in > 0 else 0)
                    })
        
        return pass_through

    def detect_low_activity_high_value(self, percentile: float = 0.9) -> List[Dict]:
        """
        Detect accounts with low activity but high values
        (Indicator of money mule accounts)
        """
        # Calculate percentiles
        all_txn_counts = sorted([len(s["transactions"]) for s in self.account_stats.values()])
        all_values = sorted([s["total_in"] + s["total_out"] for s in self.account_stats.values()])
        
        if not all_txn_counts or not all_values:
            return []
        
        idx_txn = int(len(all_txn_counts) * (1 - percentile))
        idx_val = int(len(all_values) * percentile)
        
        low_txn_threshold = all_txn_counts[max(0, idx_txn)]
        high_val_threshold = all_values[max(0, idx_val)]
        
        suspicious = []
        for account_id, stats in self.account_stats.items():
            txn_count = len(stats["transactions"])
            total_value = stats["total_in"] + stats["total_out"]
            
            if txn_count <= low_txn_threshold and total_value >= high_val_threshold:
                suspicious.append({
                    "account_id": account_id,
                    "total_transactions": txn_count,
                    "total_value": total_value,
                    "avg_per_transaction": total_value / txn_count if txn_count > 0 else 0,
                    "outlier_score": (total_value / high_val_threshold) * 
                                   (1.0 / max(txn_count / low_txn_threshold, 0.1))
                })
        
        return sorted(suspicious, key=lambda x: x["outlier_score"], reverse=True)

    def get_account_risk_profile(self, account_id: str) -> Dict:
        """Get comprehensive risk profile for an account"""
        if account_id not in self.account_stats:
            return None
        
        stats = self.account_stats[account_id]
        total_value = stats["total_in"] + stats["total_out"]
        txn_count = len(stats["transactions"])
        
        return {
            "account_id": account_id,
            "total_transactions": txn_count,
            "total_value": total_value,
            "avg_transaction": total_value / txn_count if txn_count > 0 else 0,
            "unique_sources": len(stats["unique_sources"]),
            "unique_destinations": len(stats["unique_destinations"]),
            "total_in": stats["total_in"],
            "total_out": stats["total_out"],
            "in_out_balance": abs(stats["total_in"] - stats["total_out"])
        }
