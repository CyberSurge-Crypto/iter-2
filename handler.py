import json
from bcf import Block, Blockchain, Transaction

def node_message(self, node, data):
    try:
        message = json.loads(data)
        msg_type = message.get("type")
        msg_data = message.get("data")

        if msg_type == "new_block":
            # Ensure proper conversion from dict to Block object
            block_data = Block(
                index=msg_data["index"],
                transactions=[Transaction(**tx) for tx in msg_data["transactions"]],
                timestamp=msg_data["timestamp"],
                previous_hash=msg_data["previous_hash"],
                nonce=msg_data["nonce"]
            )

            if self.blockchain.add_block(block_data):
                print(f"Added new block: {block_data.index}")

                # Remove transactions that were included in the new block
                block_transactions = {tx.transaction_id for tx in block_data.transactions}
                self.blockchain.pending_transactions = [
                    tx for tx in self.blockchain.pending_transactions 
                    if tx.transaction_id not in block_transactions
                ]
                
                # TODO: Update blockchain local data

        elif msg_type == "transaction":
            # Ensure proper conversion from dict to Transaction object
            tx_data = Transaction(**msg_data)
            tx_id = tx_data.transaction_id

            # Check if transaction already exists in pending transactions
            if any(tx.transaction_id == tx_id for tx in self.blockchain.pending_transactions):
                print(f"Duplicate transaction {tx_id} ignored.")
                return

            self.blockchain.pending_transactions.append(tx_data)
            print(f"Added new transaction: {tx_id}")

            # TODO: Update blockchain local data

        elif msg_type == "blockchain_request":
            print(f"Received blockchain request.")

            blockchain_data = json.dumps({
                "type": "blockchain_response",
                "data": [block.__dict__ for block in self.blockchain.chain]
            })

            self.send_to_node(node, blockchain_data)

        elif msg_type == "blockchain_response":
            print(f"Received blockchain response.")
            
            # Convert received blockchain data to actual Blockchain object
            received_chain = [
                Block(
                    index=b["index"],
                    transactions=[Transaction(**tx) for tx in b["transactions"]],
                    timestamp=b["timestamp"],
                    previous_hash=b["previous_hash"],
                    nonce=b["nonce"]
                )
                for b in msg_data
            ]

            # TODO: Implement blockchain comparison and syncing mechanism

        elif msg_type == "peer_list":
            peers = msg_data
            print(f"Received peer list: {peers}")

            # TODO: Store peer list in global variables

        else:
            print(f"Unknown message type: {msg_type}")

    except Exception as e:
        print(f"Error processing message: {e}")


def broadcast_transaction(self, transaction: Transaction):
    """Broadcast a new transaction to all peers"""
    message = json.dumps({
        "type": "transaction",
        "data": transaction.to_dict()
    })
    self.send_to_nodes(message)

def broadcast_new_block(self, block: Block):
    """Broadcast a new block to all peers"""
    message = json.dumps({
        "type": "new_block",
        "data": block.__dict__
    })
    self.send_to_nodes(message)

def request_peer_list(self):
    """Ask connected peers for their known peers"""
    message = json.dumps({"type": "peer_list", "data": list(self.peers)})
    self.send_to_nodes(message)
    
def request_blockchain(self):
    """request blockchain"""
    message = json.dumps({"type": "blockchain_request", "data":{}})
    self.send_to_nodes(message)