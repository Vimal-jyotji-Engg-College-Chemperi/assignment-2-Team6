"""
Suzuki-Kasami Algorithm - Demonstration Application

This is the main runnable file that demonstrates the Suzuki-Kasami
broadcast algorithm for distributed mutual exclusion.

Usage:
    python app.py
"""

from algorithm import SuzukiKasami
import time


def print_separator(char='-', length=60):
    """Print a separator line."""
    print(char * length)


def display_system_state(sk_system: SuzukiKasami):
    """Display the current state of the system."""
    state = sk_system.get_system_state()
    print("\n" + "="*60)
    print("SYSTEM STATE")
    print("="*60)
    print(f"Number of Nodes: {state['num_nodes']}")
    print(f"Total Messages Sent: {state['total_messages']}")
    print(f"Critical Section Accesses: {state['cs_accesses']}")
    print("\nNode Status:")
    print_separator()
    for node_info in state['nodes']:
        token_status = "✓ HAS TOKEN" if node_info['has_token'] else "  No token"
        cs_status = "IN CS" if node_info['in_critical_section'] else "     "
        queue_info = f"Queue: {node_info['token_queue']}" if node_info['token_queue'] else ""
        print(f"  Node {node_info['node_id']}: {token_status} | {cs_status} | "
              f"Req Seq: {node_info['request_sequence']} {queue_info}")
    print_separator()


def display_message_log(sk_system: SuzukiKasami, last_n: int = 10):
    """Display recent messages."""
    messages = sk_system.get_message_log()
    if not messages:
        print("\nNo messages exchanged yet.")
        return
    
    print(f"\nMessage Log (last {last_n}):")
    print_separator()
    for msg in messages[-last_n:]:
        if msg['type'] == 'REQUEST':
            print(f"  [{msg['type']}] Node{msg['from']} broadcasted request (seq={msg['sequence']})")
        elif msg['type'] == 'TOKEN':
            print(f"  [{msg['type']}] Token sent from Node{msg['from']} to Node{msg['to']}")
    print_separator()


def display_cs_log(sk_system: SuzukiKasami):
    """Display critical section access log."""
    log = sk_system.get_cs_access_log()
    if not log:
        print("\nNo critical section accesses yet.")
        return
    
    print("\nCritical Section Access Log:")
    print_separator()
    for entry in log:
        print(f"  Node{entry['node_id']}: {entry['action']} CS")
    print_separator()


def scenario_1_basic_operation():
    """
    Scenario 1: Basic Operation
    Demonstrates basic request, enter, and exit operations.
    """
    print("\n" + "="*60)
    print("SCENARIO 1: Basic Operation")
    print("="*60)
    print("\nInput: 3 nodes, Node0 has initial token")
    print("Operations: Node0 enters CS, exits, Node1 requests and enters")
    
    # Initialize system with 3 nodes, Node0 has token
    sk = SuzukiKasami(num_nodes=3, initial_token_holder=0)
    
    display_system_state(sk)
    
    # Node 0 enters critical section (already has token)
    print("\n>>> Node0 enters critical section")
    result = sk.enter_critical_section(0)
    print(f"Output: {result['message']}")
    
    display_system_state(sk)
    
    # Node 0 exits critical section
    print("\n>>> Node0 exits critical section")
    result = sk.exit_critical_section(0)
    print(f"Output: {result['message']}")
    
    # Node 1 requests critical section
    print("\n>>> Node1 requests critical section")
    result = sk.request_critical_section(1)
    print(f"Output: {result['message']}")
    print(f"Has token after request: {result['has_token']}")
    
    # Node 1 enters critical section
    print("\n>>> Node1 enters critical section")
    result = sk.enter_critical_section(1)
    print(f"Output: {result['message']}")
    
    display_system_state(sk)
    display_message_log(sk)


def scenario_2_multiple_requests():
    """
    Scenario 2: Multiple Concurrent Requests
    Demonstrates handling of multiple nodes requesting CS simultaneously.
    """
    print("\n" + "="*60)
    print("SCENARIO 2: Multiple Concurrent Requests")
    print("="*60)
    print("\nInput: 5 nodes, Node0 has initial token in CS")
    print("Operations: Nodes 1,2,3 request while Node0 is in CS")
    
    # Initialize system with 5 nodes
    sk = SuzukiKasami(num_nodes=5, initial_token_holder=0)
    
    # Node 0 enters CS
    sk.enter_critical_section(0)
    print("\nNode0 is in critical section")
    
    # Multiple nodes request
    print("\n>>> Node1, Node2, Node3 request critical section")
    for node_id in [1, 2, 3]:
        result = sk.request_critical_section(node_id)
        print(f"  Node{node_id}: {result['message']}")
    
    display_system_state(sk)
    
    # Node 0 exits - token should go to next waiting node
    print("\n>>> Node0 exits critical section")
    result = sk.exit_critical_section(0)
    print(f"Output: {result['message']}")
    
    display_system_state(sk)
    display_message_log(sk)


def scenario_3_token_passing():
    """
    Scenario 3: Token Passing Chain
    Demonstrates sequential token passing through multiple nodes.
    """
    print("\n" + "="*60)
    print("SCENARIO 3: Token Passing Chain")
    print("="*60)
    print("\nInput: 4 nodes, sequential CS access")
    print("Operations: Each node requests, enters, exits in sequence")
    
    sk = SuzukiKasami(num_nodes=4, initial_token_holder=0)
    
    # Sequential access pattern
    for node_id in range(4):
        print(f"\n>>> Node{node_id} sequence:")
        
        if node_id > 0:
            # Request CS
            result = sk.request_critical_section(node_id)
            print(f"  Request: {result['message']}")
        
        # Enter CS
        result = sk.enter_critical_section(node_id)
        print(f"  Enter: {result['message']}")
        
        # Simulate work in CS
        time.sleep(0.1)
        
        # Exit CS
        result = sk.exit_critical_section(node_id)
        print(f"  Exit: {result['message']}")
    
    display_system_state(sk)
    display_cs_log(sk)
    display_message_log(sk)


def interactive_mode():
    """
    Interactive mode for custom testing.
    """
    print("\n" + "="*60)
    print("INTERACTIVE MODE")
    print("="*60)
    
    try:
        num_nodes = int(input("\nEnter number of nodes (2-10): "))
        if num_nodes < 2 or num_nodes > 10:
            print("Invalid number of nodes. Using default: 3")
            num_nodes = 3
        
        initial_holder = int(input(f"Enter initial token holder (0-{num_nodes-1}): "))
        if initial_holder < 0 or initial_holder >= num_nodes:
            print("Invalid node ID. Using default: 0")
            initial_holder = 0
    except ValueError:
        print("Invalid input. Using defaults: 3 nodes, token at Node0")
        num_nodes = 3
        initial_holder = 0
    
    print(f"\nInput: {num_nodes} nodes, Node{initial_holder} has initial token")
    sk = SuzukiKasami(num_nodes=num_nodes, initial_token_holder=initial_holder)
    
    display_system_state(sk)
    
    print("\nCommands:")
    print("  r <node_id> - Request critical section")
    print("  e <node_id> - Enter critical section")
    print("  x <node_id> - Exit critical section")
    print("  s - Show system state")
    print("  m - Show message log")
    print("  l - Show CS access log")
    print("  q - Quit")
    
    while True:
        try:
            command = input("\n> ").strip().split()
            if not command:
                continue
            
            cmd = command[0].lower()
            
            if cmd == 'q':
                print("Exiting interactive mode.")
                break
            
            elif cmd == 's':
                display_system_state(sk)
            
            elif cmd == 'm':
                display_message_log(sk, last_n=20)
            
            elif cmd == 'l':
                display_cs_log(sk)
            
            elif cmd in ['r', 'e', 'x']:
                if len(command) < 2:
                    print("Please specify node ID")
                    continue
                
                try:
                    node_id = int(command[1])
                    
                    if cmd == 'r':
                        result = sk.request_critical_section(node_id)
                        print(f"Output: {result}")
                    
                    elif cmd == 'e':
                        result = sk.enter_critical_section(node_id)
                        print(f"Output: {result}")
                    
                    elif cmd == 'x':
                        result = sk.exit_critical_section(node_id)
                        print(f"Output: {result}")
                
                except ValueError:
                    print("Invalid node ID")
            
            else:
                print("Unknown command")
        
        except KeyboardInterrupt:
            print("\nExiting interactive mode.")
            break
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Main entry point for the application."""
    print("="*60)
    print("SUZUKI-KASAMI BROADCAST ALGORITHM")
    print("Distributed Mutual Exclusion Demonstration")
    print("="*60)
    
    while True:
        print("\n\nSelect a scenario:")
        print("  1. Basic Operation")
        print("  2. Multiple Concurrent Requests")
        print("  3. Token Passing Chain")
        print("  4. Interactive Mode")
        print("  5. Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '1':
            scenario_1_basic_operation()
        
        elif choice == '2':
            scenario_2_multiple_requests()
        
        elif choice == '3':
            scenario_3_token_passing()
        
        elif choice == '4':
            interactive_mode()
        
        elif choice == '5':
            print("\nExiting application. Goodbye!")
            break
        
        else:
            print("Invalid choice. Please select 1-5.")


if __name__ == "__main__":
    main()
