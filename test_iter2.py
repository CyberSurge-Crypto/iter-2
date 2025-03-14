import time
import random, copy
from p2p import StaticNode
from p2p import PeerNode
from p2p import STATIC_NODE_IP, STATIC_NODE_PORT, node_callback
from bcf import Blockchain, Block, Transaction, User, SYSTEM

def main():
    """Simulate a small P2P blockchain network."""

    # Step 1: Start the static node (bootstrap node)
    static_node = StaticNode(STATIC_NODE_IP, STATIC_NODE_PORT, node_callback)
    static_node.debug = True
    static_node.start()
    print("=== Static node started! ===")

    user1 = User()
    user2 = User()
    
    # blockchain database makeup
    bc_data = Blockchain()
    bc_data.create_genesis_block()
    
    # Give users initial balances
    tx0 = Transaction(sender=SYSTEM, receiver=user1.get_address(), amount=100)
    tx1 = Transaction(sender=SYSTEM, receiver=user2.get_address(), amount=100)
    bc_data.pending_transactions.append(tx0)
    bc_data.pending_transactions.append(tx1)
    bc_data.add_block(bc_data.mine_pending_transactions())
    
    # Create sample transactions
    transaction1 = user1.start_transaction(user2.get_address(), 50)
    transaction2 = user2.start_transaction(user1.get_address(), 30)
    bc_data.pending_transactions.append(transaction1)
    bc_data.pending_transactions.append(transaction2)

    # Mine a new block
    bc_data.add_block(bc_data.mine_pending_transactions())
    
    # Step 2: Start 3 peer nodes
    peer_nodes = []
    for i in range(3):
        peer = PeerNode("localhost", random.randint(8000, 9000), 
                        max_connections=999, callback=node_callback)
        
        peer.blockchain = copy.deepcopy(bc_data)
        
        # Save blockchain to database
        peer.save_blockchain(peer.blockchain)
        print(f"=== Created Peer {i+1}'s database! ===")

        peer.debug = True
        peer_nodes.append(peer)
        peer.start()
        time.sleep(0.5)

    print("=== 3 Peer nodes started! ===")

    # Step 3: Register nodes with the static node
    for peer in peer_nodes:
        peer.register()
        time.sleep(1)

    print("=== All peer nodes registered! ===")

    # Step 4: Simulate a transaction broadcast
    sender_node = peer_nodes[0]
    transaction = user1.start_transaction(user2.get_address(), 5)
    sender_node.blockchain.pending_transactions.append(transaction)
    sender_node.save_blockchain(sender_node.blockchain)
    sender_node.broadcast_transaction(transaction.to_dict())

    print("=== Transaction broadcasted from Node 1! ===")

    time.sleep(2)

    # Step 5: Simulate mining a block on Node 2
    miner_node = peer_nodes[1]
    new_block = miner_node.blockchain.mine_pending_transactions()
    if miner_node.blockchain.add_block(new_block):
        print(f"=== Node 2 mined a new block: {new_block.index} ===")
        print("=== Block broadcasted from Node 2! ===")
        # Step 6: Broadcast the new block
        miner_node.broadcast_block(new_block.to_dict())
        # Update local data
        miner_node.save_blockchain(miner_node.blockchain)

    time.sleep(2)

    # Step 7: Simulate a new node connecting and fetching the blockchain
    print("=== Simulating a new node joining the network... ===")
    
    new_peer = PeerNode("localhost", random.randint(8000, 9000), 
                        max_connections=999, callback=node_callback)
    new_peer.debug = True
    new_peer.start()
    time.sleep(1)

    new_peer.register()  # Register new peer to static node
    time.sleep(1)

    # # Find an existing peer to request blockchain data
    existing_peer = peer_nodes[0]  
    new_peer.fetch_blockchain(existing_peer)

    time.sleep(4)  # Allow time for blockchain to sync


    # Step 9: Shut down the network
    for peer in peer_nodes:
        peer.terminate()
        peer.stop()
        peer.join()

    new_peer.terminate()
    new_peer.stop()
    new_peer.join()

    static_node.stop()
    static_node.join()
    print("=== Network simulation completed! ===")

if __name__ == "__main__":
    main()
