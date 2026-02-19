"""
Graph Builder Module
Constructs NetworkX directed graphs from transaction data.
"""
import networkx as nx
from typing import List, Dict, Tuple, Set
from datetime import datetime
from app.schemas.transaction import Transaction


class GraphBuilder:
    """Builds and manages transaction graphs"""

    def __init__(self):
        self.graph = nx.DiGraph()
        self.transactions = []
        self.account_data = {}

    def build_graph(self, transactions: List[Transaction]) -> nx.DiGraph:
        """
        Build a directed graph from transactions.
        
        Nodes: Account IDs
        Edges: Directed transactions (from_account -> to_account)
        Edge weights: Transaction amounts
        """
        self.graph = nx.DiGraph()
        self.transactions = transactions
        self.account_data = {}

        for txn in transactions:
            # Add nodes
            if txn.from_account not in self.graph:
                self.graph.add_node(txn.from_account)
                self.account_data[txn.from_account] = {
                    "in_degree": 0,
                    "out_degree": 0,
                    "total_in": 0.0,
                    "total_out": 0.0,
                    "txn_count": 0
                }
            
            if txn.to_account not in self.graph:
                self.graph.add_node(txn.to_account)
                self.account_data[txn.to_account] = {
                    "in_degree": 0,
                    "out_degree": 0,
                    "total_in": 0.0,
                    "total_out": 0.0,
                    "txn_count": 0
                }

            # Add edge with transaction details
            if self.graph.has_edge(txn.from_account, txn.to_account):
                # Append to existing edge data
                edge_data = self.graph[txn.from_account][txn.to_account]
                edge_data["amount"] += txn.amount
                edge_data["transaction_ids"].append(txn.id)
                edge_data["count"] += 1
            else:
                # Create new edge
                self.graph.add_edge(
                    txn.from_account,
                    txn.to_account,
                    amount=txn.amount,
                    transaction_ids=[txn.id],
                    count=1,
                    timestamp=txn.timestamp
                )

            # Update account data
            self.account_data[txn.from_account]["out_degree"] += 1
            self.account_data[txn.from_account]["total_out"] += txn.amount
            self.account_data[txn.from_account]["txn_count"] += 1

            self.account_data[txn.to_account]["in_degree"] += 1
            self.account_data[txn.to_account]["total_in"] += txn.amount
            self.account_data[txn.to_account]["txn_count"] += 1

        return self.graph

    def get_graph(self) -> nx.DiGraph:
        """Return the current graph"""
        return self.graph

    def get_account_stats(self, account_id: str) -> Dict:
        """Get statistics for an account"""
        return self.account_data.get(account_id, {})

    def get_all_accounts(self) -> Set[str]:
        """Get all account nodes"""
        return set(self.graph.nodes())

    def get_outgoing_edges(self, account_id: str) -> List[Tuple[str, Dict]]:
        """Get all outgoing transactions from an account"""
        if account_id not in self.graph:
            return []
        return [(to_account, self.graph[account_id][to_account]) 
                for to_account in self.graph.successors(account_id)]

    def get_incoming_edges(self, account_id: str) -> List[Tuple[str, Dict]]:
        """Get all incoming transactions to an account"""
        if account_id not in self.graph:
            return []
        return [(from_account, self.graph[from_account][account_id]) 
                for from_account in self.graph.predecessors(account_id)]

    def get_neighbors(self, account_id: str, depth: int = 1) -> Set[str]:
        """Get all neighbors within specified depth"""
        neighbors = set()
        visited = set()
        queue = [(account_id, 0)]

        while queue:
            current, current_depth = queue.pop(0)
            if current in visited or current_depth > depth:
                continue
            visited.add(current)
            neighbors.add(current)

            for next_node in self.graph.successors(current):
                if next_node not in visited and current_depth < depth:
                    queue.append((next_node, current_depth + 1))

        neighbors.discard(account_id)
        return neighbors
