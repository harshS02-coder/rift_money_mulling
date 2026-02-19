"""
Smurfing Detection Module
Detects rapid, high-frequency transaction patterns within 72-hour windows.
Tracks fan-in (sources) and fan-out (destinations).
"""
from typing import List, Dict, Set, Tuple
from datetime import datetime, timedelta
from app.schemas.transaction import Transaction


class SmurfingDetector:
    """Detects smurfing (rapid transaction splitting) behavior"""

    def __init__(self, transactions: List[Transaction]):
        self.transactions = transactions
        self.window_hours = 72

    def detect_smurfing_accounts(self, min_transactions: int = 10) -> List[Dict]:
        """
        Detect accounts exhibiting smurfing behavior:
        - 10+ transactions within 72-hour window
        - High fan-in/fan-out (multiple sources/destinations)
        """
        smurfing_accounts = []
        
        # Group transactions by time windows for each account
        time_windows = self._create_time_windows()

        for account_id, windows in time_windows.items():
            for window_data in windows:
                if window_data["transaction_count"] >= min_transactions:
                    metrics = self._calculate_window_metrics(
                        account_id, 
                        window_data,
                        time_windows
                    )
                    smurfing_accounts.append(metrics)

        return smurfing_accounts

    def _create_time_windows(self) -> Dict[str, List[Dict]]:
        """Create 72-hour sliding windows for each account"""
        account_windows = {}
        
        # Sort transactions by timestamp
        sorted_txns = sorted(self.transactions, key=lambda t: t.timestamp)
        
        # For each account, group transactions into 72-hour windows
        for txn in sorted_txns:
            # Process as sender (outgoing)
            if txn.from_account not in account_windows:
                account_windows[txn.from_account] = []
            
            # Check if fits in existing window
            found_window = False
            for window in account_windows[txn.from_account]:
                window_start = window["start_time"]
                window_end = window_start + timedelta(hours=self.window_hours)
                
                if window_start <= txn.timestamp <= window_end:
                    window["transactions"].append(txn)
                    window["transaction_count"] += 1
                    found_window = True
                    break
            
            # Create new window if doesn't fit
            if not found_window:
                account_windows[txn.from_account].append({
                    "start_time": txn.timestamp,
                    "transactions": [txn],
                    "transaction_count": 1
                })

            # Process as receiver (incoming)
            if txn.to_account not in account_windows:
                account_windows[txn.to_account] = []
            
            found_window = False
            for window in account_windows[txn.to_account]:
                window_start = window["start_time"]
                window_end = window_start + timedelta(hours=self.window_hours)
                
                if window_start <= txn.timestamp <= window_end:
                    window["transactions"].append(txn)
                    window["transaction_count"] += 1
                    found_window = True
                    break
            
            if not found_window:
                account_windows[txn.to_account].append({
                    "start_time": txn.timestamp,
                    "transactions": [txn],
                    "transaction_count": 1
                })

        return account_windows

    def _calculate_window_metrics(self, account_id: str, window_data: Dict,
                                  all_windows: Dict) -> Dict:
        """Calculate smurfing metrics for a specific window"""
        transactions = window_data["transactions"]
        
        # Calculate fan-in and fan-out
        fan_in = len(set(txn.from_account for txn in transactions 
                        if txn.to_account == account_id))
        fan_out = len(set(txn.to_account for txn in transactions 
                         if txn.from_account == account_id))
        
        # Calculate total amounts
        total_in = sum(txn.amount for txn in transactions if txn.to_account == account_id)
        total_out = sum(txn.amount for txn in transactions if txn.from_account == account_id)
        
        total_amount = total_in + total_out
        
        return {
            "account_id": account_id,
            "window_start": window_data["start_time"].isoformat(),
            "transaction_count": window_data["transaction_count"],
            "time_window_hours": self.window_hours,
            "total_amount": total_amount,
            "total_in": total_in,
            "total_out": total_out,
            "fan_in": fan_in,
            "fan_out": fan_out,
            "transaction_ids": [t.id for t in transactions],
            "avg_transaction": total_amount / len(transactions) if transactions else 0
        }

    def get_accounts_by_fan_activity(self, min_fan_in: int = 3, 
                                     min_fan_out: int = 3) -> List[Dict]:
        """Get accounts with high fan-in/fan-out in any window"""
        suspicious = []
        
        time_windows = self._create_time_windows()
        
        for account_id, windows in time_windows.items():
            for window_data in windows:
                txns = window_data["transactions"]
                
                fan_in = len(set(txn.from_account for txn in txns 
                               if txn.to_account == account_id))
                fan_out = len(set(txn.to_account for txn in txns 
                                if txn.from_account == account_id))
                
                if fan_in >= min_fan_in or fan_out >= min_fan_out:
                    metrics = self._calculate_window_metrics(account_id, window_data, time_windows)
                    suspicious.append(metrics)

        return suspicious

    def detect_concentration_patterns(self) -> List[Dict]:
        """
        Detect accounts receiving/sending from/to very few sources
        despite high volume (possible money consolidation)
        """
        concentration = []
        
        account_sources = {}  # account -> set of source accounts
        account_destinations = {}  # account -> set of dest accounts
        account_volumes = {}  # account -> total volume
        
        for txn in self.transactions:
            # Track inbound
            if txn.to_account not in account_sources:
                account_sources[txn.to_account] = set()
            account_sources[txn.to_account].add(txn.from_account)
            
            if txn.to_account not in account_volumes:
                account_volumes[txn.to_account] = 0
            account_volumes[txn.to_account] += txn.amount
            
            # Track outbound
            if txn.from_account not in account_destinations:
                account_destinations[txn.from_account] = set()
            account_destinations[txn.from_account].add(txn.to_account)
        
        # Find concentrated accounts
        for account_id, sources in account_sources.items():
            if len(sources) <= 2 and account_volumes.get(account_id, 0) > 50000:
                concentration.append({
                    "account_id": account_id,
                    "unique_sources": len(sources),
                    "sources": list(sources),
                    "total_volume": account_volumes.get(account_id, 0),
                    "pattern": "concentrated_inbound"
                })
        
        for account_id, dests in account_destinations.items():
            if len(dests) <= 2 and account_volumes.get(account_id, 0) > 50000:
                concentration.append({
                    "account_id": account_id,
                    "unique_destinations": len(dests),
                    "destinations": list(dests),
                    "total_volume": account_volumes.get(account_id, 0),
                    "pattern": "concentrated_outbound"
                })

        return concentration
