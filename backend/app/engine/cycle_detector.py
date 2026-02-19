"""
Cycle Detection Module
Detects financial rings/cycles of length 3-5 using optimized DFS.
"""
import networkx as nx
from typing import List, Dict, Tuple, Set


class CycleDetector:
    """Detects cycles in transaction graphs"""

    def __init__(self, graph: nx.DiGraph):
        self.graph = graph
        self.cycles = []

    def find_all_cycles(self, max_length: int = 5, min_length: int = 3) -> List[List[str]]:
        """
        Find all simple cycles up to a given length.
        Uses optimized DFS to avoid exponential growth.
        """
        self.cycles = []
        
        for node in self.graph.nodes():
            self._dfs_cycles(node, [node], set([node]), max_length, min_length)

        # Remove duplicate cycles
        unique_cycles = self._deduplicate_cycles()
        return unique_cycles

    def _dfs_cycles(self, start: str, path: List[str], visited: Set[str], 
                    max_length: int, min_length: int) -> None:
        """
        DFS helper to find cycles starting from a node.
        """
        if len(path) > max_length:
            return

        current = path[-1]
        
        for neighbor in self.graph.successors(current):
            if neighbor == start and len(path) >= min_length:
                # Found a cycle back to start
                self.cycles.append(path[:])
            elif neighbor not in visited and len(path) < max_length:
                # Continue DFS
                visited.add(neighbor)
                path.append(neighbor)
                self._dfs_cycles(start, path, visited, max_length, min_length)
                path.pop()
                visited.remove(neighbor)

    def _deduplicate_cycles(self) -> List[List[str]]:
        """Remove duplicate cycles (rotations of the same cycle)"""
        unique = []
        seen_cycles = set()

        for cycle in self.cycles:
            # Create a canonical representation (smallest rotation)
            min_rotation = self._get_canonical_cycle(cycle)
            cycle_tuple = tuple(min_rotation)
            
            if cycle_tuple not in seen_cycles:
                seen_cycles.add(cycle_tuple)
                unique.append(cycle)

        return unique

    def _get_canonical_cycle(self, cycle: List[str]) -> List[str]:
        """Get canonical form of cycle (smallest rotation)"""
        rotations = [cycle[i:] + cycle[:i] for i in range(len(cycle))]
        return min(rotations)

    def get_cycle_metrics(self, cycle: List[str]) -> Dict:
        """Calculate metrics for a detected cycle"""
        edges = [(cycle[i], cycle[(i + 1) % len(cycle)]) for i in range(len(cycle))]
        
        total_amount = 0.0
        transaction_ids = []
        
        for from_acc, to_acc in edges:
            if self.graph.has_edge(from_acc, to_acc):
                edge_data = self.graph[from_acc][to_acc]
                total_amount += edge_data.get("amount", 0)
                transaction_ids.extend(edge_data.get("transaction_ids", []))

        return {
            "length": len(cycle),
            "accounts": cycle,
            "total_amount": total_amount,
            "transaction_ids": transaction_ids,
            "num_transactions": len(transaction_ids)
        }

    def find_cycles_by_length(self, target_length: int) -> List[List[str]]:
        """Find cycles of a specific length"""
        all_cycles = self.find_all_cycles(max_length=target_length, min_length=target_length)
        return [c for c in all_cycles if len(c) == target_length]

    def get_accounts_in_cycles(self) -> Set[str]:
        """Get all accounts involved in any cycle"""
        involved = set()
        for cycle in self.cycles:
            involved.update(cycle)
        return involved

    def get_cycle_participation(self) -> Dict[str, int]:
        """Get count of cycles each account participates in"""
        participation = {}
        for cycle in self.cycles:
            for account in cycle:
                participation[account] = participation.get(account, 0) + 1
        return participation
