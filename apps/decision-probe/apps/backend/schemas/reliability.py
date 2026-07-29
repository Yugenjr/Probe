from pydantic import BaseModel

class ReliabilityResponse(BaseModel):
    overall_reliability: int
    healthy_services: int
    warning_services: int
    critical_services: int
    summary: str
    generated_at: str = ""
