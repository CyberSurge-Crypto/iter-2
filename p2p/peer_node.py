import ast, json, socket
from p2pnetwork.node import Node
from db import Database
from bcf import Blockchain, Block, Transaction
from bcf import TransactionState
from datetime import datetime

class PeerNode(Node):
    def __init__(self, host, port, max_connections=999, callback=None):
        super().__init__(host, port, max_connections=max_connections, callback=callback)
        
        # Database instance
        self.db = Database("blockchain_db_"+self.id)  # Using a dedicated database folder
        
        # Initialize the blockchain data
        self.blockchain = self.load_blockchain()
        
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

    def load_blockchain(self):
        """Check if blockchain exists locally, load it, otherwise return None."""
        tables = self.db.list_tables()
        
        if "blockchain" in tables:
            print("Blockchain found in local database. Loading...")
            blockchain_data = self.db.read("blockchain")
            return self.convert_to_blockchain(blockchain_data)
        else:
            print("No blockchain found locally. Initializing new blockchain...")
            return None

    def convert_to_blockchain(self, blockchain_data):
        """Convert stored blockchain JSON data back into a Blockchain object."""
        blockchain = Blockchain()
        blockchain.chain = []
        # Load confirmed blocks
        for block_data in blockchain_data["chain"]:
            transactions = [
                Transaction(
                    sender=tx["sender"],
                    receiver=tx["receiver"],
                    amount=tx["amount"],
                    timestamp = datetime.fromisoformat(tx["timestamp"]),
                    state=TransactionState(tx["state"]),
                    signature=tx["signature"]
                ) for tx in block_data["transactions"]
            ]

            block = Block(
                index=int(block_data["index"]),
                transactions=transactions,
                timestamp=block_data["timestamp"],
                previous_hash=block_data["previous_hash"],
                nonce=block_data["nonce"]
            )
            block.hash = block_data["hash"]
            blockchain.chain.append(block)
        # Load pending transactions
        blockchain.pending_transactions = [
            Transaction(
                sender=tx["sender"],
                receiver=tx["receiver"],
                amount=tx["amount"],
                timestamp= datetime.fromisoformat(tx["timestamp"]),
                state=TransactionState(tx["state"]),
                signature=tx["signature"]
            ) for tx in blockchain_data["pending_transactions"]
        ]
        return blockchain

    
    def save_blockchain(self, blockchain):
        """Save the blockchain (including pending transactions) to the database."""
        blockchain_data = {
            "chain": [
                {
                    "index": block.index,
                    "transactions": [
                        {
                            "transaction_id": tx.transaction_id,
                            "timestamp": tx.timestamp.isoformat(),
                            "sender": tx.sender,
                            "receiver": tx.receiver,
                            "amount": tx.amount,
                            "state": tx.state.value,
                            "signature": tx.signature
                        } for tx in block.transactions
                    ],
                    "timestamp": block.timestamp,
                    "previous_hash": block.previous_hash,
                    "nonce": block.nonce,
                    "hash": block.hash
                } for block in blockchain.chain
            ],
            "pending_transactions": [
                {
                    "transaction_id": tx.transaction_id,
                    "timestamp": tx.timestamp.isoformat(),
                    "sender": tx.sender,
                    "receiver": tx.receiver,
                    "amount": tx.amount,
                    "state": tx.state.value,
                    "signature": tx.signature
                } for tx in blockchain.pending_transactions
            ]
        }

        self.db.create_table("blockchain")
        self.db.update("blockchain", [blockchain_data])
        print("Blockchain successfully stored in database!")

        

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
                    print(f"Node {self.id} has connected all peers!")
        except Exception as e:
            self.debug_print(f"on_active_nodes: Error in active nodes: {str(e)}")

        finally:
            self.debug_print(f"on_active_nodes: pulled active user list | {self.nodes_outbound}")
            if len(self.nodes_outbound) > 1:
                target_node = self.nodes_outbound[1]
                print(f"Node {self.id} is fetching blockchain!")
                self.fetch_blockchain(target_node)
                # TODO: Should fetch blockchain from all nodes?
                # TODO: Should we fetch every time we connect to peers?
                
            

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
        message = json.dumps({"type": "broadcast_transaction", "data": txn})
        self.send_to_nodes(message)
        return
    
    def on_broadcast_transaction(self, in_node, txn):
        """Receive the transaction broadcast from another node."""
        self.debug_print(f"on_broadcast_transaction: {str(in_node.id)[:10]} broadcasted a transaction: {txn}.")
        txn_data = Transaction(
                sender=txn["sender"],
                receiver=txn["receiver"],
                amount=txn["amount"],
                timestamp=datetime.fromisoformat(txn["timestamp"]),
                state=TransactionState(txn["state"]),
                signature=txn["signature"]
            )
        
        txn_id = txn_data.transaction_id
        # Check if transaction already exists in pending transactions
        if any(tx.transaction_id == txn_id for tx in self.blockchain.pending_transactions):
            print(f"Duplicate transaction {txn_id} ignored.")
            return
        
        self.blockchain.pending_transactions.append(txn_data)
        self.save_blockchain(self.blockchain)
        print(f"Added new transaction: {txn_id} into database!")
        return
    
    def broadcast_block(self, block):
        """Broadcast the block to all active nodes."""
        message = json.dumps({"type": "broadcast_block", "data": block})
        self.send_to_nodes(message)
        return
    
    def on_broadcast_block(self, in_node, block):
        """Receive the block broadcast from another node."""
        self.debug_print(f"on_broadcast_block: {str(in_node.id)[:10]} broadcasted a block: {block}.")
        # Ensure proper conversion from dict to Block object
        block_data = Block(
            index=block["index"],
            transactions=[Transaction(
                sender=txn["sender"],
                receiver=txn["receiver"],
                amount=txn["amount"],
                timestamp=datetime.fromisoformat(txn["timestamp"]),
                state=TransactionState(txn["state"]),
                signature=txn["signature"]
                ) for txn in block["transactions"]],
            timestamp=block["timestamp"],
            previous_hash=block["previous_hash"],
            nonce=block["nonce"]
        )
        if self.blockchain.add_block(block_data):
            print(f"Added new block: {block_data.index}")

            # Remove transactions that were included in the new block
            block_transactions = {tx.transaction_id for tx in block_data.transactions}
            self.blockchain.pending_transactions = [
                tx for tx in self.blockchain.pending_transactions 
                if tx.transaction_id not in block_transactions
            ]
            
            self.save_blockchain(self.blockchain)
        
        return
    
    def fetch_blockchain(self, out_node):
        """Fetch the blockchain from an active node (if exists)."""
        try:
            message = json.dumps({"type": "fetch_blockchain", "data": self.id})
            self.send_to_node(out_node, message)
        except Exception as e:
            self.debug_print(f"fetch_blockchain: Error fetching blockchain: {str(e)}")
        return

    def on_fetch_blockchain(self, in_node):
        """Send the blockchain to the requesting node."""
        self.debug_print(f"on_fetch_blockchain: {str(in_node.id)[:10]} requested the blockchain.")

        if self.blockchain is not None:
            try:
                # Convert blockchain to JSON format
                blockchain_data = {
                    "chain": [
                        {
                            "index": block.index,
                            "transactions": [
                                {
                                    "transaction_id": tx.transaction_id,
                                    "timestamp": tx.timestamp.isoformat(),
                                    "sender": tx.sender,
                                    "receiver": tx.receiver,
                                    "amount": tx.amount,
                                    "state": tx.state.value,
                                    "signature": tx.signature
                                } for tx in block.transactions
                            ],
                            "timestamp": block.timestamp,
                            "previous_hash": block.previous_hash,
                            "nonce": block.nonce,
                            "hash": block.hash
                        } for block in self.blockchain.chain
                    ],
                    "pending_transactions": [
                        {
                            "transaction_id": tx.transaction_id,
                            "timestamp": tx.timestamp.isoformat(),
                            "sender": tx.sender,
                            "receiver": tx.receiver,
                            "amount": tx.amount,
                            "state": tx.state.value,
                            "signature": tx.signature
                        } for tx in self.blockchain.pending_transactions
                    ]
                }

                # Convert dictionary to JSON string
                blockchain_json = json.dumps(blockchain_data)

                # Send blockchain data to the requesting node
                message = json.dumps({"type": "receive_blockchain", "data": blockchain_json})
                self.send_to_node(in_node, message)
                
                self.debug_print(f"on_fetch_blockchain: blockchain sent!.")
            except Exception as e:
                self.debug_print(f"on_fetch_blockchain: Error serializing blockchain: {str(e)}")

        else:
            self.debug_print("on_fetch_blockchain: No blockchain available to send.")

    
    def on_receive_blockchain(self, in_node, content):
        """Receive the blockchain from another node and compare it with the local one."""
        self.debug_print(f"on_receive_blockchain: {str(self.id)[:10]} received the blockchain.")
        try:
            # Deserialize received blockchain data
            received_blockchain_data = json.loads(content)
            # Convert received data into a Blockchain object
            received_blockchain = self.convert_to_blockchain(received_blockchain_data)
            
            # Compare blockchain lengths
            local_chain_length = len(self.blockchain.chain) if self.blockchain else 0
            received_chain_length = len(received_blockchain.chain)
            
            # Keep the longer blockchain
            if received_chain_length > local_chain_length:
                self.blockchain = received_blockchain
                self.save_blockchain(self.blockchain)  # Store new blockchain in the database
                print("Local blockchain updated with a longer chain from peer.")
            else:
                self.debug_print("Local blockchain is already longer or equal. Ignoring received blockchain.")

        except Exception as e:
            self.debug_print(f"on_receive_blockchain: Error processing received blockchain: {str(e)}")

        
    def on_node_message(self, in_node, data):
        try:
            prompt, content = data["type"], data["data"]

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