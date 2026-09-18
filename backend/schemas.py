from pydantic import BaseModel, Field
from typing import Optional, Literal


class Contact(BaseModel):
    email: str
    name: Optional[str] = None
    company: Optional[str] = None


class Job(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    description: Optional[str] = None
    skills: list[str] = Field(default_factory=list)


class AnalysisResult(BaseModel):
    contacts: list[Contact] = Field(default_factory=list)
    job: Optional[Job] = None


class ResumeSelection(BaseModel):
    resume: Literal[
        "AI_ENGINEER",
        "DATA_ANALYST",
        "AML_FRAUD"
    ]

    reason: str

    matched_skills: list[str] = Field(default_factory=list)


class GeneratedEmail(BaseModel):
    subject: str
    body: str