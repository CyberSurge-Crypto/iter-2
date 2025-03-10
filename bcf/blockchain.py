# blockchain.py
from typing import List, Optional, Dict
from block import Block
from user import User
from transaction import Transaction
from constant import SYSTEM, DIFFICULTY, TransactionState
import time
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

class Blockchain:
    def __init__(self):
        self.chain: List[Block] = []
        self.user_registry: Dict[str, User] = {}
        # mempool of pending transactions
        self.pending_transactions: List[Transaction] = []

        # make sure there is at least one block in the chain
        self.create_genesis_block()

    def create_genesis_block(self) -> None:
        """Create the genesis block of the blockchain"""
        genesis_transaction = Transaction("genesis", "genesis", 0)
        genesis_block = Block(0, [genesis_transaction], time.time(), "0")
        self.chain.append(genesis_block)

    def register_user(self, user: User) -> None:
        """Register a new user in the blockchain"""
        self.pending_transactions.append(Transaction(SYSTEM, user.address, 100))
        self.user_registry[user.address] = user

    def get_balance(self, address: str) -> int:
        """Get the balance of a user by their address"""
        balance = 0
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.sender == address:
                    balance -= transaction.amount
                if transaction.receiver == address:
                    balance += transaction.amount
        return balance

    def get_last_block(self) -> Block:
        """Get the last block in the chain"""
        return self.chain[-1]

    def add_block(self, block: Block) -> bool:
        """Validate and add a new block to the chain"""
        if not self.validate_block(block):
            return False
            
        # Update transaction states
        for tx in block.transactions:
            tx.state = TransactionState.FULLY_CONFIRMED
            
        self.chain.append(block)
        return True

    def validate_block(self, block: Block) -> bool:
        """Comprehensive block validation"""
        # Basic block structure validation
        if block.index != len(self.chain):
            return False
            
        if block.previous_hash != self.get_last_block().hash:
            return False
            
        if block.compute_hash() != block.hash:
            return False
            
        # Proof-of-Work validation
        if not block.hash.startswith('0'*DIFFICULTY):
            return False
            
        # Transaction validation
        for tx in block.transactions:
            if tx.sender == SYSTEM:
                continue
            if not self.validate_transaction(tx):
                return False
            if tx.state != TransactionState.SIGNED:
                return False
                
        return True
    
    """
    Below is the methods that interacts with transactions
    """
    def verify_transaction_signature(self, tx: Transaction) -> bool:
        """Cryptographic signature verification"""
        if tx.sender not in self.user_registry:
            return False
            
        try:
            public_key = self.user_registry[tx.sender]._public_key
            message = f"{tx.sender}{tx.receiver}{tx.amount}{tx.timestamp}"
            
            public_key.verify(
                bytes.fromhex(tx.signature),
                message.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception as e:
            print(f"Signature verification failed: {str(e)}")
            return False

    def validate_transaction(self, transaction: Transaction) -> bool:
        """ Validate that the sender has enough balance for this transaction """
        if (transaction.sender is None):
            return False
        
        if (transaction.sender == SYSTEM):
            return True
        
        if not self.verify_transaction_signature(transaction):
            return False

        sender_balance = self.get_balance(transaction.sender)
        pending_spent = sum(
            pt.amount for pt in self.pending_transactions 
            if pt.sender == transaction.sender
        )
        
        return sender_balance - pending_spent >= transaction.amount
    
    def prove_transaction(self, transaction: Transaction) -> None:
        """Allow full-node users to prove the transaction (and notify the miners)"""
        if self.verify(transaction) and self.validate(transaction):
            transaction.state = TransactionState.SIGNED
        else:
            transaction.state = TransactionState.FAILED
        return

    def get_public_key_for_address(self, address: str) -> Optional[str]:
        """Get the public key for a given address"""
        user = next((user for user in self.users if user.address == address), None)
        return user.get_public_key() if user else None

    def mine_pending_transactions(self) -> None:
        """Mine all pending transactions into a new block"""
        if not self.pending_transactions:
            return
            
        new_block = Block(
            index=len(self.chain),
            transactions=self.pending_transactions,
            timestamp=time.time(),
            previous_hash=self.get_last_block().hash
        )
        
        new_block.mine(DIFFICULTY)
        self.add_block(new_block)
        self.pending_transactions = []