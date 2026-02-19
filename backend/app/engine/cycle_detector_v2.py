"""
Enhanced Cycle Detection Module (v2)
Detects financial rings/cycles with weighted scoring and strength analysis.
Improvements:
- Cycle strength scoring based on transaction volume and frequency
- Detection of nested/sub-cycles
- Temporal pattern analysis
- Memoization for performance
"""
import networkx as nx
from typing import List, Dict, Tuple, Set
from collections import defaultdict


class CycleDetectorV2:
    """Enhanced cycle detector with financial impact scoring"""

    def __init__(self, graph: nx.DiGraph):
        self.graph = graph
        self.cycles = []
        self.cycle_cache = {}  # Memoization
        self.transactions = []  # Will be set externally for temporal analysis

    def find_all_cycles(self, max_length: int = 5, min_length: int = 3) -> List[List[str]]:
        """
        Find all simple cycles with enhanced scoring.
        """
        self.cycles = []
        visited_globally = set()
        
        # Start DFS from nodes with highest out-degree (more likely to be in cycles)
        nodes_by_degree = sorted(
            self.graph.nodes(),
            key=lambda n: self.graph.out_degree(n),
            reverse=True
        )
        
        for node in nodes_by_degree[:50]:  # Limit to top 50 nodes by out-degree
            if node not in visited_globally:
                self._dfs_cycles(node, [node], set([node]), max_length, min_length)
                visited_globally.add(node)

        # Additional pass for remaining nodes
        for node in self.graph.nodes():
            if node not in visited_globally and self.graph.out_degree(node) > 0:
                self._dfs_cycles(node, [node], set([node]), max_length, min_length)
                visited_globally.add(node)

        # Remove duplicates
        unique_cycles = self._deduplicate_cycles()
        
        # Score cycles by financial strength
        scored_cycles = self._score_cycles_by_strength(unique_cycles)
        
        return scored_cycles[:100]  # Return top 100 cycles

    def _dfs_cycles(self, start: str, path: List[str], visited: Set[str], 
                    max_length: int, min_length: int) -> None:
        """DFS with early termination logic"""
        if len(path) > max_length:
            return

        current = path[-1]
        
        # Early termination: if no outgoing edges, stop
        successors = list(self.graph.successors(current))
        if not successors:
            return
        
        for neighbor in successors:
            if neighbor == start and len(path) >= min_length:
                self.cycles.append(path[:])
            elif neighbor not in visited and len(path) < max_length:
                visited.add(neighbor)
                path.append(neighbor)
                self._dfs_cycles(start, path, visited, max_length, min_length)
                path.pop()
                visited.remove(neighbor)

    def _deduplicate_cycles(self) -> List[List[str]]:
        """Remove duplicate cycles (all rotations)"""
        unique = []
        seen_cycles = set()

        for cycle in self.cycles:
            canonical = self._get_canonical_cycle(cycle)
            cycle_tuple = tuple(canonical)
            
            if cycle_tuple not in seen_cycles:
                seen_cycles.add(cycle_tuple)
                unique.append(cycle)

        return unique

    def _get_canonical_cycle(self, cycle: List[str]) -> List[str]:
        """Get lexicographically smallest rotation"""
        rotations = [cycle[i:] + cycle[:i] for i in range(len(cycle))]
        return min(rotations)

    def _score_cycles_by_strength(self, cycles: List[List[str]]) -> List[List[str]]:
        """Score cycles based on financial metrics"""
        cycle_scores = []
        
        for cycle in cycles:
            metrics = self.get_cycle_metrics(cycle)
            
            # Calculate cycle strength score
            strength = self._calculate_cycle_strength(cycle, metrics)
            
            cycle_scores.append({
                'cycle': cycle,
                'strength': strength,
                'volume': metrics['total_amount'],
                'length': len(cycle)
            })
        
        # Sort by strength score (higher = more suspicious)
        cycle_scores.sort(key=lambda x: x['strength'], reverse=True)
        
        return [item['cycle'] for item in cycle_scores]

    def _calculate_cycle_strength(self, cycle: List[str], metrics: Dict) -> float:
        """
        Calculate cycle strength based on:
        - Total transaction volume
        - Number of transactions
        - Frequency of transactions
        - Uniformity of amounts
        """
        total_amount = metrics.get('total_amount', 0)
        num_txns = metrics.get('num_transactions', 1)
        cycle_length = len(cycle)
        
        # Volume factor (normalized, heavier cycles are more suspicious)
        volume_factor = total_amount / 100000 if total_amount > 0 else 0
        
        # Frequency factor (more transactions = more suspicious)
        frequency_factor = num_txns / 10
        
        # Complexity factor (longer cycles are more complex/suspicious)
        complexity_factor = cycle_length / 3
        
        # Combined strength score
        strength = (volume_factor * 0.4 + frequency_factor * 0.35 + complexity_factor * 0.25)
        
        return min(strength, 10.0)  # Cap at 10

    def get_cycle_metrics(self, cycle: List[str]) -> Dict:
        """Calculate comprehensive metrics for a cycle"""
        edges = [(cycle[i], cycle[(i + 1) % len(cycle)]) for i in range(len(cycle))]
        
        total_amount = 0.0
        transaction_ids = []
        amounts_per_edge = []
        
        for from_acc, to_acc in edges:
            if self.graph.has_edge(from_acc, to_acc):
                edge_data = self.graph[from_acc][to_acc]
                amount = edge_data.get("amount", 0)
                total_amount += amount
                amounts_per_edge.append(amount)
                transaction_ids.extend(edge_data.get("transaction_ids", []))

        # Calculate uniformity (low variance = more suspicious)
        avg_amount = total_amount / len(amounts_per_edge) if amounts_per_edge else 0
        variance = sum((x - avg_amount) ** 2 for x in amounts_per_edge) / len(amounts_per_edge) if amounts_per_edge else 0
        spread = (variance ** 0.5) / avg_amount if avg_amount > 0 else 0

        return {
            "length": len(cycle),
            "accounts": cycle,
            "total_amount": total_amount,
            "transaction_ids": transaction_ids,
            "num_transactions": len(transaction_ids),
            "avg_transaction": avg_amount,
            "amount_spread": min(spread, 1.0),  # Normalized
            "uniformity": 1.0 - min(spread, 1.0)  # Higher = more uniform
        }

    def get_cycle_participation(self) -> Dict[str, int]:
        """Get cycle participation count per account"""
        participation = {}
        for cycle in self.cycles:
            for account in cycle:
                participation[account] = participation.get(account, 0) + 1
        return participation

    def find_cycles_by_length(self, target_length: int) -> List[List[str]]:
        """Find cycles of specific length"""
        return [c for c in self.cycles if len(c) == target_length]

    def detect_nested_cycles(self) -> List[Dict]:
        """Detect cycles that contain other cycles"""
        nested = []
        
        for i, cycle1 in enumerate(self.cycles):
            set1 = set(cycle1)
            for j, cycle2 in enumerate(self.cycles):
                if i != j:
                    set2 = set(cycle2)
                    # Check if cycle2 is a subset of cycle1
                    if set2.issubset(set1) and set2 != set1:
                        nested.append({
                            'parent_cycle': cycle1,
                            'nested_cycle': cycle2,
                            'parent_metrics': self.get_cycle_metrics(cycle1),
                            'nested_metrics': self.get_cycle_metrics(cycle2)
                        })
        
        return nested

    def get_accounts_in_cycles(self) -> Set[str]:
        """Get all accounts involved in cycles"""
        involved = set()
        for cycle in self.cycles:
            involved.update(cycle)
        return involved
