"""
Multi-agent orchestration.

Runs the Code Analysis Agent and Security Vulnerability Agent concurrently
(not sequentially) using asyncio.to_thread for each -- both agents are
CPU-bound synchronous analysis (AST parsing, regex scanning), so wrapping
each in a thread and gathering them is what makes them genuinely run in
parallel rather than one blocking the other.

Outputs from both agents are merged into a single, uniformly-shaped list
of Finding objects.
"""

import asyncio
import time
from datetime import datetime
from uuid import uuid4

from ..models import Finding, Severity, AnalysisResult
from .code_analysis_python import analyze_python as analyze_python_quality
from .code_analysis_java import analyze_java as analyze_java_quality
from .security_python import analyze_python_security
from .security_java import analyze_java_security


def _to_finding(raw, submission_id: str, agent_source: str) -> Finding:
    return Finding(
        id=str(uuid4()),
        submission_id=submission_id,
        agent_source=agent_source,
        category=raw.category,
        severity=Severity(raw.severity),
        line_start=raw.line_start,
        line_end=raw.line_end,
        description=raw.description,
        remediation=raw.remediation,
    )


def _run_code_analysis(code: str, language: str) -> list:
    if language == "python":
        return analyze_python_quality(code)
    elif language == "java":
        return analyze_java_quality(code)
    return []


def _run_security_analysis(code: str, language: str) -> list:
    if language == "python":
        return analyze_python_security(code)
    elif language == "java":
        return analyze_java_security(code)
    return []


async def run_analysis_pipeline(submission_id: str, code: str, language: str) -> tuple[AnalysisResult, float]:
    """
    Runs Code Analysis and Security Vulnerability agents in parallel via
    separate threads, merges their findings, and returns an AnalysisResult
    plus the wall-clock duration in milliseconds (kept separate since
    AnalysisResult itself doesn't carry timing -- that's router/logging
    concern, not domain data).
    """
    start = time.perf_counter()

    code_analysis_task = asyncio.to_thread(_run_code_analysis, code, language)
    security_task = asyncio.to_thread(_run_security_analysis, code, language)

    raw_code_findings, raw_security_findings = await asyncio.gather(
        code_analysis_task, security_task
    )

    findings = [
        _to_finding(r, submission_id, "code_analysis_agent") for r in raw_code_findings
    ] + [
        _to_finding(r, submission_id, "security_vulnerability_agent") for r in raw_security_findings
    ]

    # Sort by severity (most severe first), then by line number.
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    findings.sort(key=lambda f: (severity_order[f.severity.value], f.line_start))

    summary = {sev: 0 for sev in ("critical", "high", "medium", "low", "info")}
    for f in findings:
        summary[f.severity.value] += 1
    summary["total"] = len(findings)

    duration_ms = round((time.perf_counter() - start) * 1000, 2)

    result = AnalysisResult(
        submission_id=submission_id,
        analyzed_at=datetime.utcnow(),
        findings=findings,
        summary=summary,
        duration_ms=duration_ms,
    )
    return result, duration_ms
