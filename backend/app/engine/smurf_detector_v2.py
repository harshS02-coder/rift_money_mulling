"""
Enhanced Smurfing Detection Module (v2)
Detects structuring and rapid transaction patterns with temporal analysis.
Improvements:
- Intelligent sliding window analysis
- Transaction frequency/velocity detection
- Structuring pattern detection (intentional thresholds)
- Consolidation pattern detection
- Deviation from normal behavior scoring
"""
from typing import List, Dict, Set, Tuple
from datetime import datetime, timedelta
from app.schemas.transaction import Transaction
from collections import defaultdict
import statistics


class SmurfingDetectorV2:
    """Enhanced smurfing detector with temporal and pattern analysis"""

    def __init__(self, transactions: List[Transaction]):
        self.transactions = transactions
        self.window_hours = 72
        self.account_baselines = None  # Will compute normal behavior

    def detect_smurfing_accounts(self, min_transactions: int = 6) -> List[Dict]:
        """
        Enhanced smurfing detection with multiple pattern recognition:
        - High frequency within 72h window
        - Fan-in/fan-out clustering
        - Structuring patterns (amounts near thresholds)
        - Deviation from baseline behavior
        """
        results = []
        
        # Phase 1: Multiple sliding window analysis
        suspicious_from_windows = self._analyze_sliding_windows(min_transactions)
        
        # Phase 2: Detect structuring patterns
        structuring_patterns = self._detect_structuring_patterns()
        
        # Phase 3: Consolidation pattern detection
        consolidation_patterns = self._detect_consolidation()
        
        # Phase 4: Fan activity analysis
        fan_patterns = self._analyze_fan_patterns(min_in=3, min_out=3)
        
        # Combine and deduplicate results
        all_accounts = set()
        for account in suspicious_from_windows:
            all_accounts.add(account['account_id'])
        for account in structuring_patterns:
            all_accounts.add(account['account_id'])
        for account in consolidation_patterns:
            all_accounts.add(account['account_id'])
        for account in fan_patterns:
            all_accounts.add(account['account_id'])
        
        # Create comprehensive alerts
        for account_id in all_accounts:
            alert = self._create_smurfing_alert(
                account_id,
                suspicious_from_windows,
                structuring_patterns,
                consolidation_patterns,
                fan_patterns
            )
            if alert:
                results.append(alert)
        
        return sorted(results, key=lambda x: x.get('risk_score', 0), reverse=True)

    def _analyze_sliding_windows(self, min_transactions: int = 6) -> List[Dict]:
        """Analyze with overlapping 72-hour windows"""
        account_alerts = defaultdict(list)
        
        if not self.transactions:
            return []
        
        # Sort by timestamp
        sorted_txns = sorted(self.transactions, key=lambda t: t.timestamp)
        
        # For each transaction, create a 72-hour window starting from it
        for start_idx, start_txn in enumerate(sorted_txns):
            window_end = start_txn.timestamp + timedelta(hours=self.window_hours)
            window_txns = [
                t for t in sorted_txns[start_idx:]
                if t.timestamp <= window_end
            ]
            
            if len(window_txns) < min_transactions:
                continue
            
            # Analyze accounts in this window
            window_accounts = self._analyze_window(window_txns, start_txn.timestamp)
            
            for account_data in window_accounts:
                account_id = account_data['account_id']
                account_alerts[account_id].append(account_data)
        
        # Consolidate multiple windows for same account
        consolidated = []
        for account_id, windows in account_alerts.items():
            # Use the window with highest suspicious score
            best_window = max(windows, key=lambda x: x.get('suspicious_score', 0))
            consolidated.append(best_window)
        
        return consolidated

    def _analyze_window(self, transactions: List[Transaction], window_start: datetime) -> List[Dict]:
        """Analyze a specific time window"""
        results = []
        
        # Group by account
        account_txns = defaultdict(list)
        for txn in transactions:
            account_txns[txn.from_account].append(txn)
            account_txns[txn.to_account].append(txn)
        
        for account_id, txns in account_txns.items():
            if len(txns) >= 6:  # Minimum threshold
                # Calculate metrics
                fan_in = len(set(t.from_account for t in txns if t.to_account == account_id))
                fan_out = len(set(t.to_account for t in txns if t.from_account == account_id))
                
                sent = [t for t in txns if t.from_account == account_id]
                received = [t for t in txns if t.to_account == account_id]
                
                # Calculate velocity (transactions per hour)
                if sent:
                    time_span = (max(t.timestamp for t in sent) - min(t.timestamp for t in sent)).total_seconds() / 3600
                    velocity = len(sent) / max(time_span, 1)
                else:
                    velocity = 0
                
                total_amount = sum(t.amount for t in txns)
                
                # Calculate suspicious score
                suspicious_score = self._score_smurfing_behavior(
                    len(txns), fan_in, fan_out, velocity, total_amount
                )
                
                if suspicious_score > 30:  # Threshold for suspicious
                    results.append({
                        'account_id': account_id,
                        'transaction_count': len(txns),
                        'fan_in': fan_in,
                        'fan_out': fan_out,
                        'total_amount': total_amount,
                        'avg_transaction': total_amount / len(txns) if txns else 0,
                        'velocity': velocity,
                        'suspicious_score': suspicious_score,
                        'window_start': window_start.isoformat()
                    })
        
        return results

    def _detect_structuring_patterns(self) -> List[Dict]:
        """
        Detect structuring: intentional breaking of transactions
        below $10k, $5k, or other thresholds
        """
        structuring = []
        
        account_amounts = defaultdict(list)
        for txn in self.transactions:
            account_amounts[txn.from_account].append(txn.amount)
            account_amounts[txn.to_account].append(txn.amount)
        
        common_thresholds = [10000, 5000, 3000, 1000]
        
        for account_id, amounts in account_amounts.items():
            if len(amounts) < 5:
                continue
            
            for threshold in common_thresholds:
                # Count transactions just below threshold
                below_threshold = sum(1 for a in amounts if (threshold * 0.9) < a < threshold)
                total_count = len(amounts)
                
                # If >40% of transactions cluster below threshold, suspicious
                if total_count > 0 and below_threshold / total_count > 0.4:
                    structuring.append({
                        'account_id': account_id,
                        'pattern': 'structuring',
                        'threshold': threshold,
                        'below_threshold_rate': below_threshold / total_count,
                        'suspicious_score': (below_threshold / total_count) * 100
                    })
        
        return structuring

    def _detect_consolidation(self) -> List[Dict]:
        """
        Detect consolidation: many small inbound transactions
        followed by single large outbound
        """
        consolidation = []
        
        account_flows = defaultdict(lambda: {'inbound': [], 'outbound': []})
        for txn in self.transactions:
            account_flows[txn.to_account]['inbound'].append(txn.amount)
            account_flows[txn.from_account]['outbound'].append(txn.amount)
        
        for account_id, flows in account_flows.items():
            inbound = flows['inbound']
            outbound = flows['outbound']
            
            if len(inbound) >= 3 and len(outbound) >= 1:
                total_in = sum(inbound)
                max_out = max(outbound) if outbound else 0
                
                # If single large outbound roughly matches total inbound
                if 0.9 * total_in <= max_out <= 1.1 * total_in:
                    consolidation.append({
                        'account_id': account_id,
                        'pattern': 'consolidation',
                        'inbound_count': len(inbound),
                        'total_inbound': total_in,
                        'max_outbound': max_out,
                        'match_ratio': max_out / total_in if total_in > 0 else 0,
                        'suspicious_score': (len(inbound) / 10) * 100
                    })
        
        return consolidation

    def _analyze_fan_patterns(self, min_in: int = 3, min_out: int = 3) -> List[Dict]:
        """Analyze high fan-in and fan-out patterns"""
        fan_patterns = []
        
        account_connections = defaultdict(lambda: {'sources': set(), 'destinations': set()})
        account_volumes = defaultdict(float)
        
        for txn in self.transactions:
            account_connections[txn.to_account]['sources'].add(txn.from_account)
            account_connections[txn.from_account]['destinations'].add(txn.to_account)
            account_volumes[txn.to_account] += txn.amount
            account_volumes[txn.from_account] += txn.amount
        
        for account_id, connections in account_connections.items():
            fan_in = len(connections['sources'])
            fan_out = len(connections['destinations'])
            volume = account_volumes[account_id]
            
            # High fan activity (3+ sources/destinations)
            if (fan_in >= min_in or fan_out >= min_out) and volume > 20000:
                fan_score = (fan_in + fan_out) * 10
                fan_patterns.append({
                    'account_id': account_id,
                    'pattern': 'high_fan',
                    'fan_in': fan_in,
                    'fan_out': fan_out,
                    'total_volume': volume,
                    'suspicious_score': min(fan_score, 100)
                })
        
        return fan_patterns

    def _score_smurfing_behavior(self, txn_count: int, fan_in: int, 
                                 fan_out: int, velocity: float, amount: float) -> float:
        """
        Score suspicious smurfing behavior (0-100)
        """
        score = 0
        
        # Transaction count factor (more = more suspicious)
        if txn_count >= 10:
            score += 30
        elif txn_count >= 6:
            score += 20
        
        # Fan-in/out factor
        fan_score = min((fan_in + fan_out) * 5, 30)
        score += fan_score
        
        # Velocity factor (rapid-fire transactions)
        if velocity > 1.0:  # More than 1 transaction per hour
            score += 20
        elif velocity > 0.5:
            score += 10
        
        # Amount factor (normalized to $100k baseline)
        if amount > 100000:
            score += min((amount / 100000) * 10, 20)
        
        return min(score, 100)

    def _create_smurfing_alert(self, account_id: str, windows: List[Dict],
                              structuring: List[Dict], consolidation: List[Dict],
                              fan: List[Dict]) -> Dict:
        """Create comprehensive alert combining all patterns"""
        alert = {
            'account_id': account_id,
            'transaction_count': 0,
            'time_window_hours': 72,
            'total_amount': 0.0,
            'fan_in': 0,
            'fan_out': 0,
            'risk_score': 0.0,
            'patterns': [],
            'total_suspicious_score': 0
        }
        
        # Add window data
        for w in windows:
            if w['account_id'] == account_id:
                alert['transaction_count'] = w.get('transaction_count', 0)
                alert['total_amount'] = w.get('total_amount', 0)
                alert['time_window_hours'] = w.get('time_window_hours', 72)
                alert['patterns'].append('high_frequency')
                alert['total_suspicious_score'] = max(alert['total_suspicious_score'], w.get('suspicious_score', 0))
        
        # Add other patterns
        for s in structuring:
            if s['account_id'] == account_id:
                alert['patterns'].append(f"structuring_{s['threshold']}")
                alert['total_suspicious_score'] += s.get('suspicious_score', 0)
        
        for c in consolidation:
            if c['account_id'] == account_id:
                alert['patterns'].append('consolidation')
                alert['total_suspicious_score'] += c.get('suspicious_score', 0)
        
        for f in fan:
            if f['account_id'] == account_id:
                alert['patterns'].append('high_fan')
                alert['fan_in'] = max(alert['fan_in'], f.get('fan_in', 0))
                alert['fan_out'] = max(alert['fan_out'], f.get('fan_out', 0))
                alert['total_amount'] = max(alert['total_amount'], f.get('total_volume', 0))
                alert['total_suspicious_score'] += f.get('suspicious_score', 0)
        
        # If no window data was found, calculate from raw transactions
        if alert['transaction_count'] == 0 and alert['patterns']:
            account_txns = [t for t in self.transactions 
                          if t.from_account == account_id or t.to_account == account_id]
            alert['transaction_count'] = len(account_txns)
            alert['total_amount'] = sum(t.amount for t in account_txns)
        
        # Normalize score
        alert['risk_score'] = min(alert['total_suspicious_score'] / len(alert['patterns']) if alert['patterns'] else 0, 100)
        alert['pattern_count'] = len(alert['patterns'])
        
        return alert if alert['patterns'] else None
