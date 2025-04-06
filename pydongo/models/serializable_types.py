from datetime import datetime
from pydantic import BaseModel


class Datetime(BaseModel):
    original_type: str  # Original python type (e.g dateime.date)
    value: datetime
