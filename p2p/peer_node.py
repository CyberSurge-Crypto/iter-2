#######################################################################################################################
# Author: Maurice Snoeren                                                                                             #
# Version: 0.2 beta (use at your own risk)                                                                            #
#                                                                                                                     #
# MyOwnPeer2PeerNode is an example how to use the p2pnet.Node to implement your own peer-to-peer network node.        #
# 28/06/2021: Added the new developments on id and max_connections
#######################################################################################################################
from p2pnetwork.node import Node

class MyOwnPeer2PeerNode (Node):

    # Python class constructor
    def __init__(self, host, port, id=None, callback=None, max_connections=0):
        super(MyOwnPeer2PeerNode, self).__init__(host, port, id, callback, max_connections)
        print("MyPeer2PeerNode: Started")

    # all the methods below are called when things happen in the network.
    # implement your network node behavior to create the required functionality.

    def outbound_node_connected(self, node):
        print(f"[P2P msg in node ({self.id})] outbound_node_connected to {node.id}")
        
    def inbound_node_connected(self, node):
        print(f"[P2P msg in node ({self.id})] inbound_node_connected to {node.id}")

    def inbound_node_disconnected(self, node):
        print(f"[P2P msg in node ({self.id})] inbound_node_disconnected to {node.id}")

    def outbound_node_disconnected(self, node):
        print(f"[P2P msg in node ({self.id})] outbound_node_disconnected to {node.id}")

    def node_message(self, node, data):
        print(f"[P2P msg in node ({self.id})] node_message from {node.id}: {data}")
        
    def node_disconnect_with_outbound_node(self, node):
        print(f"[P2P msg in node ({self.id})] node wants to disconnect with other outbound node: {node.id}")
        
    def node_request_to_stop(self):
        print(f"[P2P msg in node ({self.id})] node is requested to stop")
        
