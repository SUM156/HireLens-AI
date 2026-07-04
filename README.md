<img width="703" height="506" alt="Screenshot 2026-07-04 111920" src="https://github.com/user-attachments/assets/ed8c0d52-101e-419f-bea1-13301461b2b9" />

# 🎯 ResumeIQ — AI-Powered Resume Analyzer

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![Claude AI](https://img.shields.io/badge/Powered%20by-Claude%20AI-orange?logo=anthropic)
![Tests](https://img.shields.io/badge/Tests-58%20passing-brightgreen)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success)
![ATS](https://img.shields.io/badge/Feature-ATS%20Analysis-purple)

**Analyze any resume in seconds. Get a score, section-by-section AI feedback,
ATS compatibility check, keyword gap analysis, and AI-rewritten bullet points —
all in one terminal command.**

[Features](#-features) • [Architecture](#%EF%B8%8F-architecture) •
[Installation](#-installation) • [Usage](#-usage) •
[How it works](#-how-it-works) • [Roadmap](#-roadmap)

</div>

---

## 🧠 What is ResumeIQ?

ResumeIQ is a command-line AI application that takes your resume (PDF or TXT),
sends it to Claude AI with a carefully engineered expert-recruiter prompt, and
returns a complete, structured analysis:

- An **overall score (0–100)** and letter grade
- An **ATS compatibility score** — how well your resume survives automated
  filtering before a human ever sees it
- **Section-by-section scores** with grade labels (A+ through F)
- **Specific strengths** worth keeping
- **Critical issues** that may be causing automatic rejections
- **ATS keyword gap analysis** — which keywords are present and which are missing
- **AI-rewritten bullet points** — before/after rewrites of your weakest lines
- **Top 3 prioritized next steps** to focus your revisions

> 📅 Day 17 of a 60-Day Python Portfolio Challenge — one production-quality
> project per day.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📄 Multi-format input | Accepts `.pdf` and `.txt` resume files |
| 🤖 Claude AI integration | Uses Anthropic's Claude Sonnet for expert-level analysis |
| 📊 Structured scoring | 7 individual section scores + overall + ATS score |
| 🔤 ATS keyword analysis | Finds present and missing industry keywords |
| ✍️ Bullet point rewriting | AI rewrites your weakest bullets with action verbs + metrics |
| 🎨 Rich terminal UI | Color-coded panels, progress bars, tables — no GUI needed |
| 💾 JSON export | Optionally save the raw analysis to a `.json` file |
| 🧪 58 passing tests | Mocked API tests run instantly, no credits consumed |

---

## 🏗️ Architecture

```
Your Resume (.pdf or .txt)
         │
         ▼
┌─────────────────┐
│   parser.py     │  ← Extracts clean text from PDF (pypdf) or TXT
│                 │    Auto-detects format from file extension.
└────────┬────────┘
         │ clean text string
         ▼
┌─────────────────┐
│   analyzer.py   │  ← Sends resume to Claude AI via Anthropic API.
│                 │    Crafted system prompt forces JSON-only output.
│                 │    Validates response schema before returning.
└────────┬────────┘
         │ raw analysis dict (JSON)
         ▼
┌─────────────────┐
│   scorer.py     │  ← Interprets raw 0-100 scores into letter grades,
│                 │    Rich color strings, and priority ordering.
│                 │    Pure functions — no I/O, trivially testable.
└────────┬────────┘
         │ list of SectionResult dataclasses
         ▼
┌─────────────────┐
│   reporter.py   │  ← Builds and prints the full terminal report.
│                 │    The ONLY module that produces output.
│                 │    Uses Rich panels, tables, columns, and colors.
└─────────────────┘
         │
         ▼
   cli.py (entry point)  ← Handles argparse, error display, JSON export
```

### Why this layered design?

Each layer has exactly one responsibility and one data contract:

- `parser.py` produces a string → knows nothing about AI
- `analyzer.py` takes a string → knows nothing about files or display
- `scorer.py` takes a dict → knows nothing about files, AI, or display
- `reporter.py` takes a dict + list → knows nothing about files or AI

This means every layer is independently testable, swappable, and
maintainable. Changing from `pypdf` to `pdfplumber` for extraction only
touches `parser.py`. Changing from Claude to GPT-4 only touches
`analyzer.py`. The rest of the system is completely unaffected.

---

## 🔬 How it works

### 1. Prompt engineering — why Claude returns perfect JSON every time

The key to reliable AI-powered applications is a well-engineered system
prompt. ResumeIQ uses a detailed system prompt that:

- Assigns Claude a specific persona: *"expert technical recruiter and ATS
  specialist with 15 years of experience at top tech companies"*
- Specifies the exact JSON schema to return, field by field, with data
  types
- Provides a scoring rubric so scores are calibrated consistently
- Instructs Claude to return ONLY the JSON with no preamble text

The user message is simply the resume text. Stable instructions in the
system prompt, variable input in the user turn — standard production API
design.

### 2. Handling imperfect AI output

Even with strict instructions, Claude occasionally wraps JSON in markdown
code fences (` ```json ... ``` `). `_parse_json_response()` in
`analyzer.py` strips these using a regex before calling `json.loads()`,
making the parsing robust against this common variation.

### 3. ATS score — what it means

ATS (Applicant Tracking System) software is used by most large companies to
automatically filter resumes before a human ever reads them. A low ATS score
means your resume may be rejected automatically even if you're a strong
candidate. Common ATS killers: missing keywords, tables/graphics that
confuse parsers, non-standard section headings, and missing contact fields.
ResumeIQ's ATS score specifically checks for these.

### 4. Bullet point rewriting — the most valuable feature

The most common resume mistake is weak bullet points like *"Worked on ML
models"*. ResumeIQ identifies the 2-3 weakest bullets in your resume and
rewrites them using the formula: **action verb + specific context +
quantified impact**. For example:

```
Before: "Worked on machine learning models"
After:  "Built and evaluated 4 ML classification models (Logistic Regression,
         Random Forest, SVM, XGBoost) using scikit-learn, achieving 91%
         accuracy on a 10K-sample dataset"
```

These rewrites are copy-paste ready — you can use them directly.

---

## 📦 Installation

```bash
git clone https://github.com/yourusername/resumeiq
cd resumeiq
pip install -r requirements.txt
```

### Set your API key

ResumeIQ uses the Anthropic API. Get a free key at
[console.anthropic.com](https://console.anthropic.com).

```bash
# macOS / Linux
export ANTHROPIC_API_KEY=your_key_here

# Windows (Command Prompt)
set ANTHROPIC_API_KEY=your_key_here

# Windows (PowerShell)
$env:ANTHROPIC_API_KEY="your_key_here"
```

The free tier is sufficient for dozens of resume analyses.

---

## 🚀 Usage

```bash
# Analyze a PDF resume
python cli.py my_resume.pdf

# Analyze a TXT resume
python cli.py my_resume.txt

# Also save the raw JSON analysis to disk
python cli.py my_resume.pdf --output analysis.json

# Try with the included sample resume
python cli.py sample_resumes/sample_resume.txt
```

### Example output

```
────────────────── ResumeIQ — AI-Powered Resume Analysis ──────────────────

╭─── ⚠️ Resume Score ───╮  ╭──── 🤖 ATS Score ────╮
│ 62/100                │  │ 55/100               │
│ Overall Score         │  │ ATS Compatibility    │
╰───────────────────────╯  ╰──────────────────────╯

╭────────────────────────────── AI Verdict ──────────────────────────────────╮
│ A technically capable AI student whose resume undersells real              │
│ accomplishments due to missing quantification and vague descriptions.      │
╰────────────────────────────────────────────────────────────────────────────╯

📋 Section Scores (lowest first)
┌─────────────────────┬────────────────────────┬───────┐
│ Section             │ Score                  │ Grade │
├─────────────────────┼────────────────────────┼───────┤
│ ⚠️ Professional     │ [██████░░░░░░░░░░░░░░]  │   D   │
│   Summary           │ 30                     │       │
│ ❌ Work Experience  │ [█████████░░░░░░░░░░░]  │   D   │
│                     │ 45                     │       │
...

╭──────────────── 🔍 ATS Keyword Analysis ─────────────────╮
│ Found (8): Python, Machine Learning, TensorFlow, ...      │
│ Missing:   Data Pipeline, Model Deployment, Docker, ...   │
╰───────────────────────────────────────────────────────────╯

  ✍️ Bullet 1
  Before: "Helped with research"
  After:  "Assisted in 2 active research projects at ORIC, contributing
           Python scripts that processed 50K+ records and reduced manual
           reporting time by 60%"
```

---

## 🧪 Running tests

```bash
python -m unittest discover -s tests -v
```

58 tests across 3 files. All Anthropic API calls are mocked using
`unittest.mock.patch` — tests run in under 1 second and consume zero API
credits.

```
test_all_required_keys_present ... ok
test_api_failure_propagates ... ok
test_strips_markdown_json_fences ... ok
...
Ran 58 tests in 0.072s — OK
```

---

## 📁 Project structure

```
resumeiq/
├── src/
│   ├── __init__.py           # Package exports and version
│   ├── parser.py             # PDF/TXT text extraction (auto-detects format)
│   ├── analyzer.py           # Claude AI API integration + JSON parsing
│   ├── scorer.py             # Score → grade/color/emoji interpretation
│   └── reporter.py           # Rich terminal report rendering
├── tests/
│   ├── __init__.py
│   ├── test_parser.py        # File parsing + format detection tests
│   ├── test_analyzer.py      # AI response parsing + schema validation tests
│   └── test_scorer.py        # Grading logic + section interpretation tests
├── sample_resumes/
│   └── sample_resume.txt     # Example resume for demo/testing
├── cli.py                    # Argparse entry point
├── requirements.txt
├── GUIDE.txt                 # Roman Urdu setup guide
└── README.md
```

---

## 🗺️ Roadmap

- [ ] **Web UI** — Flask/FastAPI web interface so users can drag-and-drop resumes
- [ ] **DOCX support** — add `.docx` parsing via `python-docx`
- [ ] **Job description matching** — compare resume against a specific job posting
      and score keyword overlap
- [ ] **Multi-resume comparison** — analyze 2+ versions and highlight improvements
- [ ] **Export to PDF** — generate a formatted PDF of the analysis report
- [ ] **Batch mode** — analyze a folder of resumes and rank them
- [ ] **Industry templates** — specialized scoring rubrics for ML, Software
      Engineering, Data Science, Research roles

---

## 💡 What I learned

- Engineering AI prompts to return reliable structured output (JSON schema
  enforcement via system prompt, regex-based fence stripping for robustness)
- Validating AI API response schemas programmatically before consuming the data
- Building a clean data pipeline with clear layer separation: extract →
  analyze → interpret → display
- Using `dataclass` as a typed data-transfer object between layers (instead of
  raw dicts) to make contracts explicit and catch field-name errors early
- Designing all four layers to be independently unit-testable via dependency
  injection and mocking

---

## 🛠️ Tech stack

| Tool | Purpose |
|---|---|
| `anthropic` (via `requests`) | Claude AI API for resume analysis |
| `pypdf` | PDF text extraction |
| `rich` | Terminal UI: panels, tables, colors, progress bars |
| `argparse` | CLI argument parsing |
| `unittest` + `unittest.mock` | Testing with mocked API calls |
| `dataclasses` | Typed score result objects |
| `json` | Structured AI output parsing |

---

## 📄 License

MIT License — free to use, modify, and share.

---

## 🤝 Contributing

Pull requests welcome! Please run the test suite before submitting:

```bash
python -m unittest discover -s tests -v
```

All new features should include corresponding unit tests.
