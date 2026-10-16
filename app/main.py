"""FastAPI backend server for local resume analysis and ATS evaluation.
"""

import os
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.extractor import DocumentExtractor
from app.analyzer import ResumeAnalyzer
from app.job_matcher import JobMatcher
from app.samples import SAMPLE_RESUME, SAMPLE_JD

app = FastAPI(
    title="Resume Analyzer & ATS Engine",
    description="Local host resume parser, ATS evaluator, and job description matcher.",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Mount static directory for frontend assets
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def serve_index():
    """Serve the single page minimal UI."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Resume Analyzer API is running. UI not found in static/."}


@app.get("/api/health")
async def health_check():
    """Health status endpoint."""
    return {
        "status": "healthy",
        "service": "Resume Analyzer & ATS Engine",
        "mode": "localhost"
    }


@app.get("/api/sample")
async def get_sample():
    """Return pre-loaded sample resume and job description for testing."""
    return {
        "sample_resume": SAMPLE_RESUME,
        "sample_jd": SAMPLE_JD
    }


@app.post("/api/analyze")
async def analyze_resume(
    file: Optional[UploadFile] = File(None),
    resume_text: Optional[str] = Form(None),
    job_description: Optional[str] = Form(None)
):
    """
    Analyze resume from either an uploaded file (PDF, DOCX, TXT) or raw pasted text,
    optionally matching against a target job description.
    """
    extracted_text = ""
    metadata = {"format": "TXT", "page_count": 1, "is_scanned": False}

    try:
        if file and file.filename:
            file_bytes = await file.read()
            if not file_bytes:
                raise HTTPException(status_code=400, detail="Uploaded file is empty.")
            
            extracted = DocumentExtractor.extract_from_bytes(file_bytes, file.filename)
            extracted_text = extracted.get("text", "")
            metadata = {
                "format": extracted.get("format", "UNKNOWN"),
                "page_count": extracted.get("page_count", 1),
                "is_scanned": extracted.get("is_scanned", False),
                "filename": file.filename
            }
        elif resume_text and resume_text.strip():
            extracted_text = resume_text.strip()
            word_count = len(extracted_text.split())
            metadata = {
                "format": "Text Input",
                "page_count": max(1, round(word_count / 450)),
                "is_scanned": False,
                "filename": "Pasted_Resume.txt"
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Please upload a resume file (PDF, DOCX, TXT) or paste resume text."
            )

        if not extracted_text.strip():
            raise HTTPException(
                status_code=422,
                detail="Could not extract any readable text. If this is a PDF, ensure it's not a scanned image."
            )

        # Run core ATS & content analysis
        analyzer = ResumeAnalyzer(text=extracted_text, metadata=metadata)
        analysis_result = analyzer.analyze()

        # Run job description matching if provided
        job_match_result = None
        if job_description and job_description.strip():
            matcher = JobMatcher(
                resume_text=extracted_text,
                resume_skills=analysis_result["skills"]["all_skills"],
                jd_text=job_description
            )
            job_match_result = matcher.match()

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "filename": metadata.get("filename", "Resume"),
                "analysis": analysis_result,
                "job_match": job_match_result,
                "raw_text_preview": extracted_text[:1200]
            }
        )

    except HTTPException:
        raise
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(exc)}
        )
