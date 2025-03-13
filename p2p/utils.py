def node_callback(event, main_node, in_node, data):
    if event == "node_message":
        main_node.on_node_message(in_node, data)

STATIC_NODE_IP = "127.0.0.1"
STATIC_NODE_PORT = 44396