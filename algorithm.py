"""
Suzuki-Kasami's Broadcast Algorithm for Distributed Mutual Exclusion

This module implements the Suzuki-Kasami token-based algorithm for achieving
mutual exclusion in distributed systems.

Key Concepts:
- Token-based algorithm: Only the node holding the token can enter critical section
- Broadcast mechanism: Nodes broadcast REQUEST messages to all other nodes
- FIFO queue in token: Ensures fairness by tracking waiting nodes
"""

from typing import Dict, List, Set, Optional
from collections import deque
import time


class Token:
    """
    Represents the token circulating in the Suzuki-Kasami algorithm.
    
    Attributes:
        queue (deque): FIFO queue of node IDs waiting for the token
        last_request (Dict[int, int]): Maps node_id to sequence number of last executed request
    """
    
    def __init__(self, num_nodes: int):
        """
        Initialize the token.
        
        Args:
            num_nodes (int): Total number of nodes in the system
        """
        self.queue = deque()  # Queue of waiting nodes
        self.last_request: Dict[int, int] = {i: 0 for i in range(num_nodes)}
    
    def __repr__(self):
        return f"Token(queue={list(self.queue)}, last_request={self.last_request})"


class Node:
    """
    Represents a node in the distributed system using Suzuki-Kasami algorithm.
    
    Each node maintains:
    - request_number: Sequence number array for tracking requests from all nodes
    - has_token: Boolean indicating if this node has the token
    - token: The token object (if possessed)
    - request_sequence: Local sequence number for this node's requests
    """
    
    def __init__(self, node_id: int, num_nodes: int):
        """
        Initialize a node.
        
        Args:
            node_id (int): Unique identifier for this node
            num_nodes (int): Total number of nodes in the system
        """
        self.node_id = node_id
        self.num_nodes = num_nodes
        self.request_number: Dict[int, int] = {i: 0 for i in range(num_nodes)}
        self.has_token = False
        self.token: Optional[Token] = None
        self.request_sequence = 0
        self.in_critical_section = False
        self.pending_requests: Set[int] = set()  # Track which nodes have requested
        
    def request_critical_section(self) -> Dict:
        """
        Request to enter the critical section.
        
        Returns:
            Dict: REQUEST message containing node_id and sequence number
        """
        self.request_sequence += 1
        self.request_number[self.node_id] = self.request_sequence
        
        return {
            'type': 'REQUEST',
            'node_id': self.node_id,
            'sequence': self.request_sequence
        }
    
    def receive_request(self, request: Dict) -> Optional[Token]:
        """
        Process a REQUEST message from another node.
        
        Args:
            request (Dict): REQUEST message with node_id and sequence
            
        Returns:
            Optional[Token]: Token to send if conditions are met, None otherwise
        """
        sender_id = request['node_id']
        sequence = request['sequence']
        
        # Update request number for sender
        self.request_number[sender_id] = max(
            self.request_number[sender_id], 
            sequence
        )
        
        # If this node has the token and is not using it
        if self.has_token and not self.in_critical_section:
            # Check if sender's request hasn't been satisfied
            if self.token and self.token.last_request[sender_id] + 1 == sequence:
                return self._send_token(sender_id)
        else:
            # Track pending request
            self.pending_requests.add(sender_id)
        
        return None
    
    def enter_critical_section(self) -> bool:
        """
        Attempt to enter the critical section.
        
        Returns:
            bool: True if successfully entered, False otherwise
        """
        if self.has_token and not self.in_critical_section:
            self.in_critical_section = True
            return True
        return False
    
    def exit_critical_section(self) -> Optional[Dict]:
        """
        Exit the critical section and potentially send token to next waiting node.
        
        Returns:
            Optional[Dict]: Message containing token and recipient, or None
        """
        if not self.in_critical_section:
            return None
        
        self.in_critical_section = False
        
        # Update token's last_request for this node
        if self.token:
            self.token.last_request[self.node_id] = self.request_number[self.node_id]
            
            # Find nodes that have outstanding requests
            for i in range(self.num_nodes):
                if i != self.node_id:
                    # If node i has a request not yet satisfied
                    if (self.request_number[i] == self.token.last_request[i] + 1 and
                        i not in [item for item in self.token.queue]):
                        self.token.queue.append(i)
            
            # Send token to next waiting node if any
            if self.token.queue:
                next_node = self.token.queue.popleft()
                return self._send_token(next_node)
        
        return None
    
    def _send_token(self, recipient_id: int) -> Token:
        """
        Send the token to another node.
        
        Args:
            recipient_id (int): ID of the node to receive the token
            
        Returns:
            Token: The token being sent
        """
        token_to_send = self.token
        self.token = None
        self.has_token = False
        self.pending_requests.discard(recipient_id)
        return token_to_send
    
    def receive_token(self, token: Token):
        """
        Receive the token from another node.
        
        Args:
            token (Token): The token being received
        """
        self.token = token
        self.has_token = True
    
    def __repr__(self):
        return f"Node{self.node_id}(has_token={self.has_token}, in_cs={self.in_critical_section})"


class SuzukiKasami:
    """
    Suzuki-Kasami distributed mutual exclusion algorithm implementation.
    
    This class manages multiple nodes and simulates the token-based
    mutual exclusion protocol.
    """
    
    def __init__(self, num_nodes: int, initial_token_holder: int = 0):
        """
        Initialize the Suzuki-Kasami algorithm with multiple nodes.
        
        Args:
            num_nodes (int): Number of nodes in the distributed system
            initial_token_holder (int): ID of node that initially holds the token
        """
        if num_nodes < 2:
            raise ValueError("At least 2 nodes are required")
        if initial_token_holder >= num_nodes or initial_token_holder < 0:
            raise ValueError(f"Initial token holder must be between 0 and {num_nodes-1}")
        
        self.num_nodes = num_nodes
        self.nodes: List[Node] = [Node(i, num_nodes) for i in range(num_nodes)]
        
        # Assign initial token
        initial_token = Token(num_nodes)
        self.nodes[initial_token_holder].receive_token(initial_token)
        
        self.message_log: List[Dict] = []
        self.cs_access_log: List[Dict] = []
    
    def request_critical_section(self, node_id: int) -> Dict:
        """
        Node requests to enter critical section.
        
        Args:
            node_id (int): ID of the requesting node
            
        Returns:
            Dict: Status of the request
        """
        if node_id >= self.num_nodes or node_id < 0:
            return {'success': False, 'error': 'Invalid node ID'}
        
        node = self.nodes[node_id]
        
        # Generate REQUEST message
        request_msg = node.request_critical_section()
        
        # Broadcast to all other nodes
        responses = []
        for i, other_node in enumerate(self.nodes):
            if i != node_id:
                token_received = other_node.receive_request(request_msg)
                if token_received:
                    # Token is being sent to requester
                    node.receive_token(token_received)
                    self.message_log.append({
                        'type': 'TOKEN',
                        'from': i,
                        'to': node_id,
                        'timestamp': time.time()
                    })
                    responses.append(f"Received token from Node{i}")
        
        self.message_log.append({
            'type': 'REQUEST',
            'from': node_id,
            'sequence': request_msg['sequence'],
            'timestamp': time.time()
        })
        
        return {
            'success': True,
            'has_token': node.has_token,
            'responses': responses,
            'message': f"Node{node_id} broadcasted request (seq={request_msg['sequence']})"
        }
    
    def enter_critical_section(self, node_id: int) -> Dict:
        """
        Node attempts to enter critical section.
        
        Args:
            node_id (int): ID of the node
            
        Returns:
            Dict: Success status and message
        """
        if node_id >= self.num_nodes or node_id < 0:
            return {'success': False, 'error': 'Invalid node ID'}
        
        node = self.nodes[node_id]
        success = node.enter_critical_section()
        
        if success:
            entry = {
                'node_id': node_id,
                'action': 'ENTER',
                'timestamp': time.time()
            }
            self.cs_access_log.append(entry)
            return {
                'success': True,
                'message': f"Node{node_id} entered critical section"
            }
        else:
            return {
                'success': False,
                'message': f"Node{node_id} cannot enter (no token or already in CS)"
            }
    
    def exit_critical_section(self, node_id: int) -> Dict:
        """
        Node exits critical section and passes token if needed.
        
        Args:
            node_id (int): ID of the node
            
        Returns:
            Dict: Success status and next token holder info
        """
        if node_id >= self.num_nodes or node_id < 0:
            return {'success': False, 'error': 'Invalid node ID'}
        
        node = self.nodes[node_id]
        token_transfer = node.exit_critical_section()
        
        exit_entry = {
            'node_id': node_id,
            'action': 'EXIT',
            'timestamp': time.time()
        }
        self.cs_access_log.append(exit_entry)
        
        result = {
            'success': True,
            'message': f"Node{node_id} exited critical section"
        }
        
        if token_transfer:
            # Find recipient and send token
            for i, other_node in enumerate(self.nodes):
                if not other_node.has_token and i != node_id:
                    # Check if this node should receive the token
                    if other_node.request_number[i] == token_transfer.last_request[i] + 1:
                        other_node.receive_token(token_transfer)
                        self.message_log.append({
                            'type': 'TOKEN',
                            'from': node_id,
                            'to': i,
                            'timestamp': time.time()
                        })
                        result['token_sent_to'] = i
                        result['message'] += f" and sent token to Node{i}"
                        break
        
        return result
    
    def get_system_state(self) -> Dict:
        """
        Get the current state of the entire system.
        
        Returns:
            Dict: Complete system state including all nodes
        """
        return {
            'num_nodes': self.num_nodes,
            'nodes': [
                {
                    'node_id': node.node_id,
                    'has_token': node.has_token,
                    'in_critical_section': node.in_critical_section,
                    'request_sequence': node.request_sequence,
                    'token_queue': list(node.token.queue) if node.token else None
                }
                for node in self.nodes
            ],
            'total_messages': len(self.message_log),
            'cs_accesses': len(self.cs_access_log)
        }
    
    def get_message_log(self) -> List[Dict]:
        """
        Get the log of all messages exchanged.
        
        Returns:
            List[Dict]: List of all messages
        """
        return self.message_log.copy()
    
    def get_cs_access_log(self) -> List[Dict]:
        """
        Get the log of all critical section accesses.
        
        Returns:
            List[Dict]: List of all CS entries and exits
        """
        return self.cs_access_log.copy()
