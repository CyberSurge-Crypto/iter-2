import random
from time import sleep
from .peer_node import PeerNode
from .static_node import StaticNode
from .utils import STATIC_NODE_IP, STATIC_NODE_PORT, node_callback


if __name__ == "__main__":
    
    static_node = StaticNode(STATIC_NODE_IP, STATIC_NODE_PORT, node_callback)
    static_node.start()

    peer_nodes = []
    for i in range(4):
        pn = PeerNode("localhost", random.randint(8000, 9000), 
                        max_connections=999, callback=node_callback)
        pn.debug = True
        peer_nodes.append(pn)

    for i in range(4):
        peer_nodes[i].start()
        sleep(0.2)

    for i in range(4):
        peer_nodes[i].register()
        sleep(0.2)

    peer_nodes[2].broadcast_block("block")
    sleep(0.2)

    peer_nodes[3].broadcast_transaction("transaction")
    sleep(0.2)

    for i in range(4):
        peer_nodes[i].terminate()
        peer_nodes[i].stop()
        peer_nodes[i].join()

    static_node.stop()
    static_node.join()
