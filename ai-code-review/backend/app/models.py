"""
Shared data models for the AI Code Review & Security Analysis Agent.

Every module (submission, agents, knowledge base) reads/writes these shapes
so the pipeline stays consistent as we add more pieces in later milestones.
"""

from pydantic import BaseModel
from enum import Enum
from datetime import datetime


class Language(str, Enum):
    PYTHON = "python"
    JAVA = "java"


class SubmissionMethod(str, Enum):
    PASTE = "paste"
    UPLOAD = "upload"


class CodeSubmission(BaseModel):
    id: str
    language: Language
    method: SubmissionMethod
    raw_code: str
    filename: str | None = None
    submitted_at: datetime
    is_valid_syntax: bool
    syntax_errors: list[str] = []


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Finding(BaseModel):
    id: str
    submission_id: str
    agent_source: str
    category: str
    severity: Severity
    line_start: int
    line_end: int
    description: str
    remediation: str | None = None
    fixed_code_snippet: str | None = None


class KnowledgeChunk(BaseModel):
    id: str
    source_doc: str
    text: str
    metadata: dict
