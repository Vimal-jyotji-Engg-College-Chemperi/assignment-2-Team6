# Suzuki-Kasami Broadcast Algorithm for Distributed Databases

## Overview

This is a modular implementation of the **Suzuki-Kasami token-based algorithm** for achieving mutual exclusion in distributed systems. The algorithm ensures that only one node can access the critical section at any time, which is crucial for maintaining consistency in distributed databases.

## Algorithm Description

The Suzuki-Kasami algorithm is a **token-based mutual exclusion algorithm** that uses:
- **Token**: A unique token that circulates among nodes. Only the node holding the token can enter the critical section.
- **Broadcast Requests**: When a node wants to enter the critical section, it broadcasts a REQUEST message to all other nodes.
- **FIFO Queue**: The token maintains a queue of waiting nodes to ensure fairness.

### Key Features
- **Efficient**: Only one message per critical section access in the best case
- **Fair**: Uses FIFO queue to prevent starvation
- **Distributed**: No central coordinator required
- **Deadlock-free**: Token-based mechanism prevents deadlock

## Project Structure

```
distributed assignment/
├── algorithm.py    # Backend module with SuzukiKasami class implementation
├── app.py         # Runnable demonstration file
└── README.md      # This file
```

### Files Description

#### 1. `algorithm.py` - Backend Module
Contains three main classes:
- **`Token`**: Represents the token with queue and request tracking
- **`Node`**: Represents a node in the distributed system
- **`SuzukiKasami`**: Main algorithm coordinator class

#### 2. `app.py` - Application Runner
Interactive demonstration with multiple scenarios and custom testing mode.

## Installation & Setup

### Prerequisites
- Python 3.7 or higher

### Installation
No external dependencies required. Just clone or download the files.

```bash
cd "d:\distributed assignement"
```

## Usage

### Running the Application

```bash
python app.py
```

### Available Scenarios

The application provides 4 modes:

1. **Basic Operation**: Simple request-enter-exit flow
2. **Multiple Concurrent Requests**: Handling multiple nodes requesting simultaneously
3. **Token Passing Chain**: Sequential token passing demonstration
4. **Interactive Mode**: Custom testing with manual commands

## Detailed Scenario Explanations

### Scenario 1: Basic Operation

**Purpose:** Demonstrates the fundamental workflow of requesting, entering, and exiting the critical section.

**Inputs:**
- 3 nodes in the system
- Node 0 initially has the token

**Operations Performed:**
1. Node 0 enters critical section (already has token)
2. Node 0 exits critical section
3. Node 1 requests critical section
4. Node 1 enters critical section

**Example Output:**
```
>>> Node0 enters critical section
Output: Node0 entered critical section

SYSTEM STATE
Node 0: ✓ HAS TOKEN | IN CS | Req Seq: 0

>>> Node0 exits critical section
Output: Node0 exited critical section

>>> Node1 requests critical section
Output: Node1 broadcasted request (seq=1)
Has token after request: True

>>> Node1 enters critical section
Output: Node1 entered critical section

SYSTEM STATE
Node 0:   No token |      | Req Seq: 0
Node 1: ✓ HAS TOKEN | IN CS | Req Seq: 1
Node 2:   No token |      | Req Seq: 0

Message Log:
  [REQUEST] Node1 broadcasted request (seq=1)
  [TOKEN] Token sent from Node0 to Node1
```

**Key Learning Points:**
- Shows basic token ownership and transfer
- Demonstrates request-enter-exit cycle
- Illustrates automatic token passing when node has it

---

### Scenario 2: Multiple Concurrent Requests

**Purpose:** Shows how the algorithm handles multiple nodes requesting the critical section simultaneously while another node is using it.

**Inputs:**
- 5 nodes in the system
- Node 0 initially has token and is in critical section
- Nodes 1, 2, 3 all request simultaneously

**Operations Performed:**
1. Node 0 is already in critical section
2. Nodes 1, 2, 3 broadcast requests (while Node 0 is busy)
3. Node 0 exits → token goes to first waiting node
4. Shows the token queue mechanism

**Example Output:**
```
Node0 is in critical section

>>> Node1, Node2, Node3 request critical section
  Node1: Node1 broadcasted request (seq=1)
  Node2: Node2 broadcasted request (seq=1)
  Node3: Node3 broadcasted request (seq=1)

SYSTEM STATE
Node 0: ✓ HAS TOKEN | IN CS | Req Seq: 0 Queue: [1, 2, 3]
Node 1:   No token |      | Req Seq: 1
Node 2:   No token |      | Req Seq: 1
Node 3:   No token |      | Req Seq: 1
Node 4:   No token |      | Req Seq: 0

>>> Node0 exits critical section
Output: Node0 exited critical section and sent token to Node1

SYSTEM STATE
Node 0:   No token |      | Req Seq: 0
Node 1: ✓ HAS TOKEN |      | Req Seq: 1 Queue: [2, 3]
Node 2:   No token |      | Req Seq: 1
Node 3:   No token |      | Req Seq: 1
Node 4:   No token |      | Req Seq: 0
```

**Key Learning Points:**
- Demonstrates FIFO queue mechanism
- Shows fairness in token distribution
- Illustrates handling of concurrent requests
- Queue is maintained within the token itself

---

### Scenario 3: Token Passing Chain

**Purpose:** Demonstrates sequential token passing as each node accesses the critical section in order.

**Inputs:**
- 4 nodes in the system
- Each node sequentially: requests → enters → exits

**Operations Performed:**
```
For each node (0, 1, 2, 3):
  - Request critical section
  - Enter critical section
  - Simulate work (0.1 second delay)
  - Exit critical section
  - Pass token to next node
```

**Example Output:**
```
>>> Node0 sequence:
  Enter: Node0 entered critical section
  Exit: Node0 exited critical section

>>> Node1 sequence:
  Request: Node1 broadcasted request (seq=1)
  Enter: Node1 entered critical section
  Exit: Node1 exited critical section and sent token to Node2

>>> Node2 sequence:
  Request: Node2 broadcasted request (seq=1)
  Enter: Node2 entered critical section
  Exit: Node2 exited critical section and sent token to Node3

>>> Node3 sequence:
  Request: Node3 broadcasted request (seq=1)
  Enter: Node3 entered critical section
  Exit: Node3 exited critical section

Critical Section Access Log:
  Node0: ENTER CS
  Node0: EXIT CS
  Node1: ENTER CS
  Node1: EXIT CS
  Node2: ENTER CS
  Node2: EXIT CS
  Node3: ENTER CS
  Node3: EXIT CS

Total Messages: 9 (3 REQUESTs + 6 TOKEN transfers)
```

**Key Learning Points:**
- Shows complete lifecycle of token circulation
- Demonstrates sequential processing
- Illustrates message complexity (REQUEST + TOKEN messages)
- Shows CS access logging

---

### Scenario 4: Interactive Mode

**Purpose:** Allows custom testing with manual control over all operations.

**Inputs (User Provided):**
```
Enter number of nodes (2-10): 4
Enter initial token holder (0-3): 0
```

**Available Commands:**

| Command | Input Format | Description | Example Output |
|---------|-------------|-------------|----------------|
| `r <node_id>` | Request CS | Node broadcasts request to all | `{'success': True, 'has_token': False, 'message': 'Node2 broadcasted request (seq=1)'}` |
| `e <node_id>` | Enter CS | Node attempts to enter critical section | `{'success': True, 'message': 'Node0 entered critical section'}` |
| `x <node_id>` | Exit CS | Node exits CS and passes token | `{'success': True, 'message': 'Node0 exited critical section and sent token to Node2'}` |
| `s` | Show state | Display complete system state | Full system status display |
| `m` | Show messages | Display last 20 messages | Message log with timestamps |
| `l` | Show CS log | Display CS access history | List of all ENTER/EXIT events |
| `q` | Quit | Exit interactive mode | Returns to main menu |

**Example Interactive Session:**
```
Input: 4 nodes, Node0 has initial token

Commands:
  r <node_id> - Request critical section
  e <node_id> - Enter critical section
  x <node_id> - Exit critical section
  s - Show system state
  m - Show message log
  l - Show CS access log
  q - Quit

> e 0
Output: {'success': True, 'message': 'Node0 entered critical section'}

> r 1
Output: {'success': True, 'has_token': False, 'responses': [], 
         'message': 'Node1 broadcasted request (seq=1)'}

> r 2
Output: {'success': True, 'has_token': False, 'responses': [], 
         'message': 'Node2 broadcasted request (seq=1)'}

> s
============================================================
SYSTEM STATE
============================================================
Number of Nodes: 4
Total Messages Sent: 2
Critical Section Accesses: 1

Node Status:
------------------------------------------------------------
  Node 0: ✓ HAS TOKEN | IN CS | Req Seq: 0 Queue: [1, 2]
  Node 1:   No token |      | Req Seq: 1
  Node 2:   No token |      | Req Seq: 1
  Node 3:   No token |      | Req Seq: 0
------------------------------------------------------------

> x 0
Output: {'success': True, 'message': 'Node0 exited critical section and sent token to Node1', 
         'token_sent_to': 1}

> m
Message Log (last 20):
------------------------------------------------------------
  [REQUEST] Node1 broadcasted request (seq=1)
  [REQUEST] Node2 broadcasted request (seq=1)
  [TOKEN] Token sent from Node0 to Node1
------------------------------------------------------------

> q
Exiting interactive mode.
```

**Recommended Test Sequences:**

1. **Basic Flow Test:**
   ```
   r 1 → e 1 → x 1 → s
   ```

2. **Concurrent Request Test:**
   ```
   e 0 → r 1 → r 2 → r 3 → s → x 0 → s
   ```

3. **Queue Observation Test:**
   ```
   e 0 → r 1 → r 2 → s → x 0 → e 1 → s → x 1 → s
   ```

**Key Learning Points:**
- Hands-on exploration of algorithm behavior
- Ability to create custom scenarios
- Real-time state observation
- Understanding of queue dynamics and token movement

---

### Scenario Comparison Summary

| Scenario | # Nodes | Complexity | Key Feature | Best For |
|----------|---------|------------|-------------|----------|
| **1. Basic** | 3 | Low | Simple workflow | Understanding basics, First-time users |
| **2. Multiple Requests** | 5 | Medium | Concurrent requests + queue | Understanding fairness, Queue mechanics |
| **3. Token Chain** | 4 | Medium | Sequential passing | Understanding complete flow, Message analysis |
| **4. Interactive** | 2-10 | Variable | Manual control | Custom testing, Deep exploration |

## API Reference

### Class: `SuzukiKasami`

Main class for managing the distributed mutual exclusion algorithm.

#### Constructor

```python
SuzukiKasami(num_nodes: int, initial_token_holder: int = 0)
```

**Inputs:**
- `num_nodes` (int): Number of nodes in the distributed system (minimum 2)
- `initial_token_holder` (int): ID of the node that initially holds the token (default: 0)

**Output:**
- Returns a `SuzukiKasami` instance

**Example:**
```python
from algorithm import SuzukiKasami

# Create system with 5 nodes, Node 0 has initial token
sk = SuzukiKasami(num_nodes=5, initial_token_holder=0)
```

---

#### Method: `request_critical_section()`

```python
request_critical_section(node_id: int) -> Dict
```

**Input:**
- `node_id` (int): ID of the node requesting critical section access

**Output (Dict):**
```python
{
    'success': bool,           # Whether request was valid
    'has_token': bool,         # Whether node received token
    'responses': List[str],    # List of responses from other nodes
    'message': str            # Description of what happened
}
```

**Example:**
```python
result = sk.request_critical_section(1)
# Output: {
#   'success': True,
#   'has_token': True,
#   'responses': ['Received token from Node0'],
#   'message': 'Node1 broadcasted request (seq=1)'
# }
```

---

#### Method: `enter_critical_section()`

```python
enter_critical_section(node_id: int) -> Dict
```

**Input:**
- `node_id` (int): ID of the node attempting to enter critical section

**Output (Dict):**
```python
{
    'success': bool,    # True if successfully entered, False otherwise
    'message': str      # Description of result
}
```

**Example:**
```python
result = sk.enter_critical_section(1)
# Output: {
#   'success': True,
#   'message': 'Node1 entered critical section'
# }
```

**Note:** Node must have the token to successfully enter.

---

#### Method: `exit_critical_section()`

```python
exit_critical_section(node_id: int) -> Dict
```

**Input:**
- `node_id` (int): ID of the node exiting critical section

**Output (Dict):**
```python
{
    'success': bool,           # Whether exit was successful
    'message': str,           # Description of what happened
    'token_sent_to': int      # (Optional) ID of node receiving token
}
```

**Example:**
```python
result = sk.exit_critical_section(1)
# Output: {
#   'success': True,
#   'message': 'Node1 exited critical section and sent token to Node2',
#   'token_sent_to': 2
# }
```

---

#### Method: `get_system_state()`

```python
get_system_state() -> Dict
```

**Input:** None

**Output (Dict):**
```python
{
    'num_nodes': int,              # Total number of nodes
    'nodes': List[Dict],           # State of each node
    'total_messages': int,         # Total messages exchanged
    'cs_accesses': int            # Total CS accesses
}
```

**Node State Structure:**
```python
{
    'node_id': int,                    # Node identifier
    'has_token': bool,                 # Whether node has token
    'in_critical_section': bool,       # Whether in CS
    'request_sequence': int,           # Local request sequence number
    'token_queue': List[int] or None   # Queue in token (if has token)
}
```

**Example:**
```python
state = sk.get_system_state()
# Output: {
#   'num_nodes': 3,
#   'nodes': [
#     {'node_id': 0, 'has_token': False, 'in_critical_section': False, ...},
#     {'node_id': 1, 'has_token': True, 'in_critical_section': True, ...},
#     {'node_id': 2, 'has_token': False, 'in_critical_section': False, ...}
#   ],
#   'total_messages': 5,
#   'cs_accesses': 2
# }
```

---

#### Method: `get_message_log()`

```python
get_message_log() -> List[Dict]
```

**Input:** None

**Output (List[Dict]):** List of all messages exchanged

**Message Structure:**
```python
# REQUEST message
{
    'type': 'REQUEST',
    'from': int,           # Requesting node ID
    'sequence': int,       # Sequence number
    'timestamp': float     # Unix timestamp
}

# TOKEN transfer message
{
    'type': 'TOKEN',
    'from': int,          # Sending node ID
    'to': int,            # Receiving node ID
    'timestamp': float    # Unix timestamp
}
```

---

#### Method: `get_cs_access_log()`

```python
get_cs_access_log() -> List[Dict]
```

**Input:** None

**Output (List[Dict]):** List of all critical section accesses

**Log Entry Structure:**
```python
{
    'node_id': int,        # Node ID
    'action': str,         # 'ENTER' or 'EXIT'
    'timestamp': float     # Unix timestamp
}
```

---

## Complete Usage Example

```python
from algorithm import SuzukiKasami

# Initialize system with 3 nodes
sk = SuzukiKasami(num_nodes=3, initial_token_holder=0)

# Node 0 enters CS (already has token)
result = sk.enter_critical_section(0)
print(result)
# Output: {'success': True, 'message': 'Node0 entered critical section'}

# Node 0 exits CS
result = sk.exit_critical_section(0)
print(result)
# Output: {'success': True, 'message': 'Node0 exited critical section'}

# Node 1 requests CS
result = sk.request_critical_section(1)
print(result)
# Output: {'success': True, 'has_token': True, 'responses': [...], 'message': '...'}

# Node 1 enters CS
result = sk.enter_critical_section(1)
print(result)
# Output: {'success': True, 'message': 'Node1 entered critical section'}

# Check system state
state = sk.get_system_state()
print(state)
# Output: Complete system state with all node information

# Get message log
messages = sk.get_message_log()
print(messages)
# Output: List of all REQUEST and TOKEN messages

# Node 1 exits CS
result = sk.exit_critical_section(1)
print(result)
```

## Interactive Mode Commands

When running in interactive mode, use these commands:

| Command | Description | Example |
|---------|-------------|---------|
| `r <node_id>` | Request critical section | `r 1` |
| `e <node_id>` | Enter critical section | `e 1` |
| `x <node_id>` | Exit critical section | `x 1` |
| `s` | Show system state | `s` |
| `m` | Show message log | `m` |
| `l` | Show CS access log | `l` |
| `q` | Quit interactive mode | `q` |

### Interactive Mode Example Session

```
> r 1
Output: {'success': True, 'has_token': True, ...}

> e 1
Output: {'success': True, 'message': 'Node1 entered critical section'}

> s
[System state displayed]

> x 1
Output: {'success': True, 'message': 'Node1 exited critical section'}

> q
Exiting interactive mode.
```

## Algorithm Flow

1. **Initialization**
   - Create `n` nodes
   - Assign initial token to one node

2. **Requesting Critical Section**
   - Node increments its sequence number
   - Broadcasts REQUEST(node_id, sequence) to all nodes
   - Waits for token (if doesn't have it)

3. **Receiving Request**
   - Update request number for sender
   - If has token and not in CS, send token to requester
   - Otherwise, note the pending request

4. **Entering Critical Section**
   - Node must have the token
   - Sets in_critical_section flag

5. **Exiting Critical Section**
   - Update token's last_request for this node
   - Check for pending requests and update token queue
   - Send token to next waiting node (if any)

## Error Handling

The implementation includes validation for:
- Invalid node IDs
- Minimum number of nodes (at least 2)
- Invalid initial token holder
- Attempting to enter CS without token

All methods return structured dictionaries with `success` flags and error messages when applicable.

## Use Cases

This implementation is suitable for:
- **Distributed Databases**: Ensuring exclusive access to shared data
- **Distributed File Systems**: Coordinating file access
- **Resource Management**: Managing shared resources in distributed systems
- **Educational Purposes**: Understanding distributed mutual exclusion algorithms

## Advantages

1. **Low Message Complexity**: Only `O(n)` messages per critical section request
2. **Fair**: FIFO queue ensures no starvation
3. **No Deadlock**: Token-based approach prevents deadlock
4. **Efficient**: Token carries queue information, reducing coordination overhead

## Limitations

1. **Token Loss**: System fails if token is lost (requires recovery mechanism)
2. **Network Reliability**: Assumes reliable message delivery
3. **Scalability**: Broadcast approach may not scale well for very large systems

## Future Enhancements

- Add token recovery mechanism
- Implement fault tolerance
- Add network simulation with delays
- Visualize token movement
- Add performance metrics

## References

- Suzuki, I., & Kasami, T. (1985). "A distributed mutual exclusion algorithm." ACM Transactions on Computer Systems (TOCS), 3(4), 344-349.

## License

Educational implementation for distributed systems learning.

## Author

This implementation demonstrates the Suzuki-Kasami algorithm for educational purposes in distributed database systems.
