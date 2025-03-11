import json
from bcf import Block, Blockchain, Transaction

def node_message(self, node, data):
    try:
        message = json.loads(data)
        if message["type"] == "new_block":
            block_data:Block = message["data"]
            self.blockchain.add_block(block_data)
            print(f"Added new block: {block_data['index']}")
            
            # Remove transactions that were included in the new block
            block_transactions = {tx["transaction_id"] for tx in block_data["transactions"]}
            self.blockchain.pending_transactions = [
                tx for tx in self.blockchain.pending_transactions if tx.transaction_id not in block_transactions
            ]
            
            # TODO: Upate blockchain local data
            
        elif message["type"] == "transaction":
            tx_data = message["data"]
            tx_id = tx_data["transaction_id"]

            # Check if transaction already exists in pending_transactions
            if any(tx.transaction_id == tx_id for tx in self.blockchain.pending_transactions):
                print(f"Duplicate transaction {tx_id} ignored.")
                return

            # Cast transaction data as a Transaction object
            existing_transaction = next(
                (tx for tx in self.blockchain.pending_transactions if tx.transaction_id == tx_id), None
            )
            
            # TBD: need validation or not?
            
            if not existing_transaction:
                self.blockchain.pending_transactions.append(tx_data)  # Directly add transaction dict

            print(f"Added new transaction: {tx_id}")
            
            # TODO: Upate blockchain local data
            
        elif message["type"] == "blockchain_request":
            print(f"Received blockchain request.")
            
            blockchain_data = json.dumps({
                "type": "blockchain_response",
                "data": [block.__dict__ for block in self.blockchain.chain]
            })

            self.send_to_node(node, blockchain_data)
            
        elif message["type"] == "blockchain_response":
            print(f"Received blockchain response.")
            blockchain_data:Blockchain = message["data"]
            
            # TODO: Need a collect and compare method
            
            # TODO: Store blockchain local data
            
        elif message["type"] == "peer_list":
            peers = message["data"]
            print(f"Received peer list: {peers}")
            
            # store it into global variables
            
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