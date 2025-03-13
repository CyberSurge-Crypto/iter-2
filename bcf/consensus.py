import hashlib
from bcf.constant import TransactionState
from bcf.transaction import Transaction

"""
Helper methods for signature and transactions    
"""

def first_confirm(transaction: Transaction) -> None:
    """(The miner) publishes a block and confirm transactions inside"""
    transaction.state = TransactionState.FIRST_CONFIRMED
    return

def fully_confirm(transaction: Transaction) -> None:
    """(The miner that mined the 6th block since the txn) fully
    confirms the transactions inside """
    transaction.state = TransactionState.FULLY_CONFIRMED
    return

def cancel(transaction: Transaction) -> None:
    """(The miner of the txn block, after finding this block rollbacked
    due to block branching) cancels the transaction"""
    transaction.state = TransactionState.CANCELED
    return

def create_signature(txn_msg: str, private_key: str) -> str:
    """Create a signature for a transaction"""
    message_hash = hashlib.sha256(txn_msg.encode()).hexdigest()
    signature = private_key.sign(message_hash)
    return signature

def verify_signature(signature: str, txn_msg: str, public_key: str) -> bool:
    """Verify the signature of a transaction"""
    message_hash = hashlib.sha256(txn_msg.encode()).hexdigest()
    return public_key.verify(signature, message_hash)