"""
Enhanced Shell Account Detection Module (v2)
Identifies accounts with suspicious characteristics of shell/mule accounts.
Improvements:
- Temporal dormancy analysis (inactive then active)
- Transaction velocity/timing patterns
- Network centrality analysis
- Perfect pass-through detection
- Behavioral anomaly scoring
- One-way vs bidirectional flow analysis
"""
from typing import List, Dict, Set
from app.schemas.transaction import Transaction
from datetime import datetime, timedelta
from collections import defaultdict
import statistics


class ShellAccountDetectorV2:
    """Enhanced shell account detector with multi-dimensional analysis"""

    def __init__(self, transactions: List[Transaction]):
        self.transactions = transactions
        self.account_stats = self._calculate_comprehensive_stats()

    def _calculate_comprehensive_stats(self) -> Dict[str, Dict]:
        """Calculate multi-dimensional statistics for each account"""
        stats = {}
        
        for txn in self.transactions:
            # Initialize account if not seen
            for account in [txn.from_account, txn.to_account]:
                if account not in stats:
                    stats[account] = {
                        'transactions': [],
                        'total_out': 0,
                        'total_in': 0,
                        'unique_destinations': set(),
                        'unique_sources': set(),
                        'timestamps': [],
                        'amounts': [],
                        'outbound': [],
                        'inbound': []
                    }
            
            # Record transaction
            stats[txn.from_account]['transactions'].append(txn)
            stats[txn.from_account]['outbound'].append(txn)
            stats[txn.from_account]['total_out'] += txn.amount
            stats[txn.from_account]['unique_destinations'].add(txn.to_account)
            stats[txn.from_account]['timestamps'].append(txn.timestamp)
            stats[txn.from_account]['amounts'].append(txn.amount)
            
            stats[txn.to_account]['transactions'].append(txn)
            stats[txn.to_account]['inbound'].append(txn)
            stats[txn.to_account]['total_in'] += txn.amount
            stats[txn.to_account]['unique_sources'].add(txn.from_account)
            stats[txn.to_account]['timestamps'].append(txn.timestamp)
            stats[txn.to_account]['amounts'].append(txn.amount)
        
        return stats

    def detect_shell_accounts(self, max_transactions: int = 5, 
                             min_total_value: float = 50000) -> List[Dict]:
        """
        Enhanced shell account detection with multi-factor scoring.
        """
        shell_accounts = []
        
        for account_id, stats in self.account_stats.items():
            txn_count = len(stats['transactions'])
            total_throughput = stats['total_in'] + stats['total_out']
            
            # Phase 1: Basic threshold check
            if txn_count <= max_transactions and total_throughput >= min_total_value:
                
                # Phase 2: Calculate multi-factor risk score
                risk_profile = self._calculate_account_risk_profile(account_id, stats)
                
                if risk_profile['shell_score'] > 40:  # Threshold for shell account
                    shell_accounts.append(risk_profile)
        
        # Sort by shell score (higher = more likely shell account)
        return sorted(shell_accounts, key=lambda x: x['shell_score'], reverse=True)

    def _calculate_account_risk_profile(self, account_id: str, stats: Dict) -> Dict:
        """Calculate comprehensive risk profile"""
        txn_count = len(stats['transactions'])
        total_in = stats['total_in']
        total_out = stats['total_out']
        total_throughput = total_in + total_out
        
        # Factor 1: Transaction value concentration
        avg_value = total_throughput / txn_count if txn_count > 0 else 0
        high_value_score = min((avg_value / 10000) * 20, 20)
        
        # Factor 2: Pass-through indicator (in ≈ out)
        pass_through_score = self._score_pass_through(total_in, total_out)
        
        # Factor 3: Limited connections (few sources/destinations)
        connection_score = self._score_connection_pattern(
            len(stats['unique_sources']),
            len(stats['unique_destinations']),
            txn_count
        )
        
        # Factor 4: Temporal dormancy (inactive then active)
        dormancy_score = self._score_temporal_pattern(stats['timestamps'])
        
        # Factor 5: Flow directionality (suspicious if purely in->out)
        directionality_score = self._score_flow_direction(
            len(stats['inbound']),
            len(stats['outbound']),
            txn_count
        )
        
        # Factor 6: Amount uniformity (suspicious if very uniform)
        uniformity_score = self._score_amount_uniformity(stats['amounts'])
        
        # Composite shell account score
        shell_score = (
            high_value_score * 0.20 +
            pass_through_score * 0.25 +
            connection_score * 0.20 +
            dormancy_score * 0.15 +
            directionality_score * 0.15 +
            uniformity_score * 0.05
        )
        
        return {
            'account_id': account_id,
            'total_transactions': txn_count,
            'total_throughput': total_throughput,
            'total_in': total_in,
            'total_out': total_out,
            'avg_transaction_value': avg_value,
            'unique_sources': len(stats['unique_sources']),
            'unique_destinations': len(stats['unique_destinations']),
            'in_out_ratio': total_out / total_in if total_in > 0 else 0,
            'in_out_difference': abs(total_in - total_out),
            'inbound_count': len(stats['inbound']),
            'outbound_count': len(stats['outbound']),
            'high_value_score': high_value_score,
            'pass_through_score': pass_through_score,
            'connection_score': connection_score,
            'dormancy_score': dormancy_score,
            'directionality_score': directionality_score,
            'uniformity_score': uniformity_score,
            'shell_score': min(shell_score, 100),
            'risk_level': self._get_risk_level(shell_score)
        }

    def _score_pass_through(self, total_in: float, total_out: float) -> float:
        """Score likelihood of pass-through account (in ≈ out)"""
        if total_in == 0 or total_out == 0:
            return 0
        
        ratio = min(total_out, total_in) / max(total_out, total_in)
        diff = abs(total_in - total_out)
        max_val = max(total_in, total_out)
        
        # Nearly perfect match is suspicious
        if ratio > 0.95 and diff < max_val * 0.05:
            return 25  # Perfect pass-through
        elif ratio > 0.90:
            return 15
        elif ratio > 0.85:
            return 8
        
        return 0

    def _score_connection_pattern(self, unique_sources: int, unique_destinations: int, 
                                  txn_count: int) -> float:
        """Score suspicious connection patterns"""
        score = 0
        
        # Few sources for many transactions (consolidation indicator)
        if unique_sources == 1 and txn_count >= 3:
            score += 10
        elif unique_sources <= 2 and txn_count >= 5:
            score += 8
        
        # Few destinations for many transactions (distribution indicator)
        if unique_destinations == 1 and txn_count >= 3:
            score += 10
        elif unique_destinations <= 2 and txn_count >= 5:
            score += 8
        
        # Connector pattern (similar sources and destinations)
        total_connections = unique_sources + unique_destinations
        if total_connections <= 3 and txn_count >= 4:
            score += 7
        
        return min(score, 20)

    def _score_temporal_pattern(self, timestamps: List[datetime]) -> float:
        """Detect dormant then active pattern"""
        if len(timestamps) < 3:
            return 0
        
        sorted_times = sorted(timestamps)
        time_gaps = [
            (sorted_times[i+1] - sorted_times[i]).total_seconds() / 3600
            for i in range(len(sorted_times) - 1)
        ]
        
        if not time_gaps:
            return 0
        
        # Look for large gap followed by rapid activity
        max_gap = max(time_gaps)
        avg_gap = statistics.mean(time_gaps)
        
        # Large dormancy period (>7 days) followed by activity
        if max_gap > 168:  # 7 days
            # After dormancy, were transactions rapid?
            gap_idx = time_gaps.index(max_gap)
            subsequent_gaps = time_gaps[gap_idx+1:] if gap_idx + 1 < len(time_gaps) else []
            
            if subsequent_gaps and statistics.mean(subsequent_gaps) < 24:  # Rapid activity
                return 15
        
        # Clustered activity (low variance in timing)
        if avg_gap > 0:
            variance = statistics.variance(time_gaps) if len(time_gaps) > 1 else 0
            cv = (variance ** 0.5) / avg_gap if avg_gap > 0 else 0
            
            if cv < 0.5:  # Very uniform/clustered timing
                return 12
        
        return 0

    def _score_flow_direction(self, inbound_count: int, outbound_count: int, 
                             total_count: int) -> float:
        """Score suspicious flow directionality"""
        score = 0
        
        # Purely input or purely output (one-way flow)
        if inbound_count == 0 and outbound_count > 2:
            return 12  # Source account
        elif outbound_count == 0 and inbound_count > 2:
            return 12  # Sink account
        
        # Very unbalanced (90%+ one direction)
        if total_count > 0:
            in_ratio = inbound_count / total_count
            out_ratio = outbound_count / total_count
            
            if in_ratio > 0.9 or out_ratio > 0.9:
                score += 8
        
        return score

    def _score_amount_uniformity(self, amounts: List[float]) -> float:
        """Score suspicious amount uniformity"""
        if len(amounts) < 3:
            return 0
        
        if not amounts or sum(amounts) == 0:
            return 0
        
        mean_val = statistics.mean(amounts)
        variance = statistics.variance(amounts) if len(amounts) > 1 else 0
        std_dev = variance ** 0.5
        
        # Coefficient of variation
        cv = std_dev / mean_val if mean_val > 0 else 0
        
        # Very uniform amounts (CV < 0.2) is suspicious
        if cv < 0.2:
            return 5  # Nearly identical amounts
        elif cv < 0.4:
            return 3
        
        return 0

    def detect_pass_through_accounts(self, tolerance: float = 0.05) -> List[Dict]:
        """Detect pure pass-through accounts (in = out)"""
        pass_through = []
        
        for account_id, stats in self.account_stats.items():
            total_in = stats['total_in']
            total_out = stats['total_out']
            
            if total_in > 0 and total_out > 0:
                ratio = min(total_out, total_in) / max(total_out, total_in)
                diff = abs(total_in - total_out)
                max_val = max(total_in, total_out)
                
                # Near-perfect pass-through (95%+ match)
                if ratio > 0.95 and diff < max_val * tolerance:
                    pass_through.append({
                        'account_id': account_id,
                        'total_in': total_in,
                        'total_out': total_out,
                        'match_ratio': ratio,
                        'difference': diff,
                        'transaction_count': len(stats['transactions']),
                        'unique_sources': len(stats['unique_sources']),
                        'unique_destinations': len(stats['unique_destinations']),
                        'pass_through_likelihood': min((ratio - 0.95) * 20, 1.0)
                    })
        
        return sorted(pass_through, key=lambda x: x['pass_through_likelihood'], reverse=True)

    def detect_velocity_anomalies(self) -> List[Dict]:
        """Detect accounts with unusual transaction velocity"""
        anomalies = []
        
        for account_id, stats in self.account_stats.items():
            timestamps = stats['timestamps']
            
            if len(timestamps) < 3:
                continue
            
            sorted_times = sorted(timestamps)
            total_span = (sorted_times[-1] - sorted_times[0]).total_seconds() / 3600  # hours
            
            if total_span == 0:
                continue
            
            # Calculate velocity
            txn_velocity = len(timestamps) / total_span if total_span > 0 else 0
            
            # Anomalously high velocity (>2 transactions per hour)
            if txn_velocity > 2:
                anomalies.append({
                    'account_id': account_id,
                    'velocity': txn_velocity,
                    'transaction_count': len(timestamps),
                    'time_span_hours': total_span,
                    'anomaly_level': min(txn_velocity / 2, 1.0)  # Normalized
                })
        
        return sorted(anomalies, key=lambda x: x['velocity'], reverse=True)

    def _get_risk_level(self, score: float) -> str:
        """Convert score to risk level"""
        if score >= 80:
            return 'CRITICAL'
        elif score >= 60:
            return 'HIGH'
        elif score >= 40:
            return 'MEDIUM'
        else:
            return 'LOW'

    def get_comprehensive_profile(self, account_id: str) -> Dict:
        """Get complete risk profile for an account"""
        if account_id not in self.account_stats:
            return None
        
        stats = self.account_stats[account_id]
        profile = self._calculate_account_risk_profile(account_id, stats)
        
        # Add pass-through status
        pass_through_accounts = self.detect_pass_through_accounts()
        is_pass_through = any(p['account_id'] == account_id for p in pass_through_accounts)
        profile['is_pass_through'] = is_pass_through
        
        # Add velocity analysis
        velocity_anomalies = self.detect_velocity_anomalies()
        velocity_data = next((v for v in velocity_anomalies if v['account_id'] == account_id), None)
        if velocity_data:
            profile['velocity'] = velocity_data['velocity']
            profile['velocity_anomaly'] = velocity_data['anomaly_level']
        
        return profile
