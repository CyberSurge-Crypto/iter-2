from .constant import TransactionState
from datetime import datetime
import hashlib

class Transaction:
    def __init__(self, sender: str, receiver: str, amount: int, timestamp = datetime.now(), state = TransactionState.STARTED, signature = None ) -> None:
        self.timestamp = timestamp
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.state = state
        self.signature = signature
        self.transaction_id = self.get_id()

    def __str__(self) -> str:
        return str(self.transaction_id) + " " + str(self.timestamp) + " " + str(self.sender) + " " + str(self.receiver) + " " + str(self.amount) + " " + str(self.state)
    
    def get_id(self):
        return hashlib.sha256(f"{self.sender}{self.receiver}{self.amount}{self.timestamp}".encode()).hexdigest()
    
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
    
