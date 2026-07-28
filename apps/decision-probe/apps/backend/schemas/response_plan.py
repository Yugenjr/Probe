from pydantic import BaseModel
from typing import List, Literal

class TaskItem(BaseModel):
    title: str
    priority: Literal["high", "medium", "low"]
    owner: str
    status: Literal["pending", "in_progress", "completed"]

class ResponsePlanResponse(BaseModel):
    tasks: List[TaskItem]
