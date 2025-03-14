#  Bootstrap Nodes (Predefined Entry Points)
#  1. This method assumes that a bootstrap node
#       is already running on the network.
#       when a new node joins the network,
#       it tries to connect with the bootstrap node
#       to get the list of active nodes on the network.
#  2. The bootstrap node is a centralized and well-known node
#       that is always available on the network.
#  3. After registering with the bootstrap node,
#       the new node knows the whole list of other active nodes.
#  4. When a node terminates, it informs the bootstrap node
#       to remove it from the list of active nodes.
#  5. The Static node does not participate in 
#       the blockchain activity, but only supports p2p connections

from p2pnetwork.node import Node
import json

class StaticNode(Node):
    def __init__(self, host, port, callback=None, max_connections=999):
        super().__init__(host, port, callback=callback, max_connections=max_connections)
        
        # this set's elements are in the form of tuple: (ip, port, node_id)
        self.active_nodes = set()

        # debug usage:
        self.debug_functions = ["run", "on_register", "on_termination"]

    
    def debug_print(self, message):
        """When the debug flag is set to True, all debug messages are printed in the console."""
        if self.debug:
            call_function = message.split(":")[0]

            if call_function in self.debug_functions:
                print("DEBUG (static node): \t" + message + '\n')

    def on_register(self, in_node):
        """Send the list of active nodes to the incoming node."""
        #message = "active_nodes:" + str(self.active_nodes)
        message = json.dumps({"type": "active_nodes", "data": str(self.active_nodes)})
        self.send_to_node(in_node, message)
        self.active_nodes.add((in_node.host, in_node.port, in_node.id))
        self.debug_print("on_register: " + message)

    def on_termination(self, in_node):
        """Remove the node from the list of active nodes."""
        old_active_nodes = str(self.active_nodes)
        self.active_nodes.remove((in_node.host, in_node.port, in_node.id))
        self.debug_print("on_termination: " + old_active_nodes + "->" + str(self.active_nodes))

    def on_node_message(self, in_node, data):
        command = data.split(":")[0]

        if command == "register":
            self.on_register(in_node)

        elif command == "terminate":
            self.on_termination(in_node)

