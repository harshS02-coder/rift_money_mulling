from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Transaction(BaseModel):
    """Schema for individual transactions"""
    id: str = Field(..., description="Transaction ID")
    from_account: str = Field(..., description="Source account")
    to_account: str = Field(..., description="Destination account")
    amount: float = Field(..., gt=0, description="Transaction amount")
    timestamp: datetime = Field(..., description="Transaction timestamp")
    description: Optional[str] = Field(None, description="Optional transaction description")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "TXN001",
                "from_account": "ACC001",
                "to_account": "ACC002",
                "amount": 5000.00,
                "timestamp": "2025-12-15T10:30:00",
                "description": "Payment transfer"
            }
        }


class TransactionRequest(BaseModel):
    """Request schema for transaction batch uploads"""
    transactions: list[Transaction] = Field(..., description="List of transactions")

    class Config:
        json_schema_extra = {
            "example": {
                "transactions": [
                    {
                        "id": "TXN001",
                        "from_account": "ACC001",
                        "to_account": "ACC002",
                        "amount": 5000.00,
                        "timestamp": "2025-12-15T10:30:00"
                    }
                ]
            }
        }
