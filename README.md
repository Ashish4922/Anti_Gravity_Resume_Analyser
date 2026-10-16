# ResuMetrics 📄⚡

> **A fast, privacy-first, minimalist Resume Analysis & ATS Engine running 100% locally on localhost.**

ResuMetrics evaluates technical resumes against modern Applicant Tracking System (ATS) parsing standards, quantifies bullet impact, flags passive language, extracts technical skills, and matches qualifications against any target Job Description.

---

## ✨ Features

- **🔒 100% Private & Local**: Zero data leaves your machine. Operates completely on `localhost:8000` with no external API keys or subscriptions required.
- **📁 Multi-Format Ingestion**: Supports drag-and-drop parsing for **PDF**, **DOCX**, and **TXT** resumes, or direct text paste.
- **🎯 ATS Readiness Scoring (0–100)**:
  - Standard section verification (`Summary`, `Experience`, `Education`, `Skills`, `Projects`).
  - Contact information parsing (Email, Phone, LinkedIn, GitHub, Portfolio).
  - Word count and document length validation.
  - Text readability and machine-parsability audits.
- **💡 Quantifiable Impact Detection**:
  - Highlights bullet points with metrics (%, $, volume, latency, user counts).
  - Calculates impact ratio across work experience bullets.
- **⚡ Power Verbs & Tone Analyzer**:
  - Detects strong action verbs (`Architected`, `Spearheaded`, `Scaled`, `Optimized`).
  - Flags weak/passive phrases (`Responsible for`, `Assisted with`, `Helped`).
  - Warns against overused clichés and buzzwords (`Hard worker`, `Team player`, `Out-of-the-box thinker`).
- **🎯 Job Description Alignment & Gap Analysis**:
  - Computes skill overlap and composite compatibility score (0–100%).
  - Identifies **Matching Skills** (green chips) and **Missing Critical Skills** (amber/red tags).
  - Pinpoints missing high-frequency keywords found in the job description.
- **✨ STAR / Google XYZ Bullet Polish**:
  - Automatically identifies weak bullet points and suggests rewrites using the Google formula: *Accomplished [X] as measured by [Y] by doing [Z]*.
- **📊 Minimalist, Distraction-Free UI**:
  - Clean Linear / Vercel-inspired typography and interface.
  - Interactive circular SVG score gauge.
  - Dark / Light mode toggle with saved user preference.
  - One-click PDF printing and JSON analysis export.
  - Built-in **Demo Sample** button for instant one-click testing.

---

## 🚀 Quick Start

### 1. Requirements
- Python 3.9+ (Python 3.10, 3.11, 3.12, 3.13, 3.14 supported)

### 2. Launch on Localhost
You can start the software in one command:

**Option A (Windows batch file):**
Double-click `run.bat` or run:
```cmd
run.bat
```

**Option B (Python directly):**
```bash
python run.py
```

The application will start on **`http://localhost:8000`** and open automatically in your default browser.

---

## 🛠️ Project Structure

```
├── app/
│   ├── __init__.py
│   ├── main.py            # FastAPI web server and REST endpoints
│   ├── analyzer.py        # Core NLP and ATS scoring engine
│   ├── extractor.py       # PDF (pypdf), DOCX, and TXT document extractor
│   ├── job_matcher.py     # Job Description comparison & keyword gap engine
│   ├── taxonomy.py        # 500+ categorized skills, action verbs, and cliches
│   └── samples.py         # Sample Senior Full-Stack resume and target JD
├── static/
│   ├── index.html         # Minimalist responsive single-page UI
│   ├── css/
│   │   └── style.css      # Custom styling, dark/light themes, print layout
│   └── js/
│       └── app.js         # Frontend interactivity, SVG gauge, charts, tabs
├── sample_data/
│   ├── sample_resume.txt  # Ready-to-use sample resume file
│   └── sample_jd.txt      # Ready-to-use target job description
├── test_app.py            # Automated test suite
├── requirements.txt       # Project dependencies
├── run.bat                # Windows launcher script
├── run.py                 # Python server launcher script
└── README.md              # Documentation
```

---

## 🧪 Running Automated Tests

Run the automated test suite with:

```bash
python test_app.py
```

All unit tests verify text extraction, section detection, skill categorization, quantifiable impact analysis, ATS score calculation, and job matching.

---

## 📡 REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Serves the minimalist single-page web app |
| `GET` | `/api/health` | Health check and engine status |
| `GET` | `/api/sample` | Returns pre-loaded sample resume and job description |
| `POST` | `/api/analyze` | Accepts multipart `file` or `resume_text` + optional `job_description` |

---

## 🔒 Privacy & Security Guarantee
- Runs **100% locally** on `127.0.0.1:8000`.
- Does **not** transmit resumes or personal data to any external server or cloud service.
- Safe for confidential, proprietary, or private resumes.
