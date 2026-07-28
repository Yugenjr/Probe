from pydantic import BaseModel
from typing import List, Literal

class CommunicationItem(BaseModel):
    channel: Literal["slack", "email", "status_page"]
    message: str

class CommunicationResponse(BaseModel):
    updates: List[CommunicationItem]
