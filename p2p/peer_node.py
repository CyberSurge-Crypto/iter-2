import socket
import ast
from p2pnetwork.node import Node

class PeerNode(Node):
    def __init__(self, host, port, max_connections=999, callback=None):
        super().__init__(host, port, max_connections=max_connections, callback=callback)

        # debug usage:
        self.debug_functions = ["connect_with_node"
            "on_register", "on_termination", "on_active_nodes", 
            "on_new_node_connect", "on_fetch_blockchain", 
            "on_receive_blockchain", "on_broadcast_transaction", 
            "on_broadcast_block"
            ]

        # Static node connection
        self.STATIC_BOOTSTRAP_NODE_IP = "127.0.0.1"
        self.STATIC_BOOTSTRAP_NODE_PORT = 44396
        self.static_node_connection = None
        
        # Active nodes
        self.active_nodes = ["run", "register", "terminate", "on_active_nodes"]   

    # TODO: Override the init_server() function to set a non blocking mode?

    """ ------------------------------------------------------------------------------- """
    """ P2P functions.                                                                  """
    """ ------------------------------------------------------------------------------- """
    
    def debug_print(self, message):
        """When the debug flag is set to True, all debug messages are printed in the console.
            To let your debug print show up, add the function name to the debug_functions list,
            and start your log with `function: {your message}`.
        """
        if self.debug:
            call_function = message.split(":")[0]
            if call_function in self.debug_functions or "error" in message.lower():
                print("DEBUG (" + str(self.id)[:10] + "): \t" + message + '\n')
            # else:
            #     print("DEBUG (" + str(self.id)[:10] + "): \t" +call_function + '\n')

    def connect_to_static_node(self):
        # connect to the static node
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.STATIC_BOOTSTRAP_NODE_IP, self.STATIC_BOOTSTRAP_NODE_PORT))
            sock.send((self.id + ":" + str(self.port)).encode('utf-8'))
            connected_node_id = sock.recv(4096).decode('utf-8')

            thread_client = self.create_new_connection(
                sock, connected_node_id, self.STATIC_BOOTSTRAP_NODE_IP, self.STATIC_BOOTSTRAP_NODE_PORT)
            thread_client.start()
            
            self.static_node_connection = thread_client

            self.nodes_outbound.append(thread_client)
            self.outbound_node_connected(thread_client)
            return True
        
        except Exception as e:
            self.debug_print(f"connect_to_static_node: Error connecting to static node: {str(e)}")
            return False
    
    def disconnect_to_static_node(self):
        # disconnect from the static node
        if self.static_node_connection is not None:
            self.static_node_connection.stop()
            self.static_node_connection.join()
            self.node_disconnected(self.static_node_connection)
            self.outbound_node_disconnected(self.static_node_connection)
            self.static_node_connection = None
        
        return

    def on_active_nodes(self, in_node, str_node_set):
        """Connect to the active nodes in the list."""
        node_set = ast.literal_eval(str_node_set)
        try:
            if len(node_set) > 0:
                for node_tuple in node_set:
                    node_host = str(node_tuple[0])
                    node_port = int(node_tuple[1])
                    self.connect_with_node(node_host, node_port, reconnect=False)
        except Exception as e:
            self.debug_print(f"on_active_nodes: Error in active nodes: {str(e)}")

        finally:
            self.debug_print(f"on_active_nodes: pulled active user list | {self.nodes_outbound}")
            if len(self.nodes_outbound) > 1:
                target_node = self.nodes_outbound[1]
                self.fetch_blockchain(target_node)

    """ ------------------------------------------------------------------------------- """
    """ Interaction with the static node.                                               """
    """ ------------------------------------------------------------------------------- """

    def register(self):
        """Register this node to the static node's list of active nodes."""
        self.connect_to_static_node()

        # send a message to the static node to register this node
        register_message = "register:" + self.id
        self.send_to_node(self.static_node_connection, register_message)

        self.disconnect_to_static_node()
        return

    def terminate(self):
        """Inform the static node to remove this node from the list of active nodes."""
        
        # connect to the static node
        self.connect_to_static_node()

        # send a message to the static node to remove this node
        terminate_message = "terminate:" + self.id
        self.send_to_node(self.static_node_connection, terminate_message)

        # terminate this node
        self.disconnect_to_static_node()
        self.stop()
        self.join()
        return

    """ ------------------------------------------------------------------------------- """
    """ Interaction with other active peer nodes.                                       """
    """ ------------------------------------------------------------------------------- """

    ## !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    ## TODO: Insert your Blockchain code here.
    ## !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    def broadcast_transaction(self, txn):
        """Broadcast the transaction to all active nodes."""
        self.send_to_nodes("broadcast_transaction:" + txn)
        return
    
    def on_broadcast_transaction(self, in_node, txn):
        """Receive the transaction broadcast from another node."""
        self.debug_print(f"on_broadcast_transaction: {str(in_node.id)[:10]} broadcasted a transaction: {txn}.")
        return
    
    def broadcast_block(self, block):
        """Broadcast the block to all active nodes."""
        self.send_to_nodes("broadcast_block:" + block)
        return
    
    def on_broadcast_block(self, in_node, block):
        """Receive the block broadcast from another node."""
        self.debug_print(f"on_broadcast_block: {str(in_node.id)[:10]} broadcasted a block: {block}.")
        return
    
    def fetch_blockchain(self, out_node):
        """Fetch the blockchain from an active node (if exists)."""
        try:
            fetch_message = "fetch_blockchain:" + self.id
            self.send_to_node(out_node, fetch_message)
        except Exception as e:
            self.debug_print(f"fetch_blockchain: Error fetching blockchain: {str(e)}")
        return

    def on_fetch_blockchain(self, in_node):
        """Send the blockchain to the requesting node."""
        self.debug_print(f"on_fetch_blockchain: {str(in_node.id)[:10]} requested the blockchain.")

        self.send_to_node(in_node, "receive_blockchain:" + "sample-blockchain")    
        return
    
    def on_receive_blockchain(self, in_node, content):
        """Receive the blockchain from another node."""
        self.debug_print(f"on_receive_blockchain: {str(in_node.id)[:10]} sent the blockchain: {content}.")
        return
        
    def on_node_message(self, in_node, data):
        try:
            prompt = data.split(":")[0]
            content = data.split(":")[1]

            if prompt == "active_nodes":
                self.on_active_nodes(in_node, content)

            elif prompt == "fetch_blockchain":
                self.on_fetch_blockchain(in_node)

            elif prompt == "receive_blockchain":
                self.on_receive_blockchain(in_node, content)

            elif prompt == "broadcast_transaction":
                self.on_broadcast_transaction(in_node, content)

            elif prompt == "broadcast_block":
                self.on_broadcast_block(in_node, content)
        
        except Exception as e:
            self.debug_print(f"Error in on_node_message: {str(e)}")