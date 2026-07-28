from pydantic import BaseModel

class KnowledgeResponse(BaseModel):
    problem: str
    solution: str
    prevention: str
