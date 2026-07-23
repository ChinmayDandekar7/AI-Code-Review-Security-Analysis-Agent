"""
API endpoints for Milestone 2: running the multi-agent analysis pipeline
against a previously submitted CodeSubmission.
"""

from fastapi import APIRouter, HTTPException

from ..models import AnalysisResult
from ..submission.router import SUBMISSIONS
from .orchestrator import run_analysis_pipeline

router = APIRouter(prefix="/analysis", tags=["analysis"])

# In-memory store, same pattern as SUBMISSIONS in the submission module.
ANALYSIS_RESULTS: dict[str, AnalysisResult] = {}


@router.post("/{submission_id}", response_model=AnalysisResult)
async def analyze_submission(submission_id: str):
    submission = SUBMISSIONS.get(submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found.")

    if not submission.is_valid_syntax:
        raise HTTPException(
            status_code=400,
            detail="Cannot analyze code with syntax errors. Fix syntax first.",
        )

    result, duration_ms = await run_analysis_pipeline(
        submission_id, submission.raw_code, submission.language.value
    )
    ANALYSIS_RESULTS[submission_id] = result
    return result


@router.get("/{submission_id}", response_model=AnalysisResult)
async def get_analysis(submission_id: str):
    result = ANALYSIS_RESULTS.get(submission_id)
    if not result:
        raise HTTPException(status_code=404, detail="No analysis found for this submission.")
    return result
