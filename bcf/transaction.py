from constant import TransactionState
from datetime import datetime
import hashlib

class Transaction:
    def __init__(self, sender: str, receiver: str, amount: int) -> None:
        self.timestamp = datetime.now()
        self.transaction_id = hashlib.sha256(f"{sender}{receiver}{amount}{self.timestamp}".encode()).hexdigest()
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.state = TransactionState.STARTED
        self.signature = None

    def __str__(self) -> str:
        return str(str(self.transaction_id)) + " " + str(self.timestamp) + " " + str(self.sender) + " " + str(self.receiver) + " " + str(self.amount) + " " + str(self.state)
    
    def to_dict(self) -> dict:
        return {
            "transaction_id": self.transaction_id,
            "timestamp": self.timestamp.isoformat(),
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "state": self.state.value,
            "signature": self.signature
        }
    
