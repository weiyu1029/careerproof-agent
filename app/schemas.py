from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field


class CareerProofRequest(BaseModel):
    target_role: str = Field(description="Target job title or role family.")
    company: str = Field(default="Unknown company")
    industry: str | None = Field(default=None)
    job_description: str = Field(description="Raw job description.")
    candidate_profile: str = Field(description="Candidate experience summary or resume text.")
    goal: str = Field(default="interview_strategy")
