import streamlit as st
import os

from src.parser import parse_resume
from src.analyzer import analyze_resume
from src.scorer import interpret_section_scores

st.set_page_config(page_title="ResumeIQ", layout="wide")

st.title("🎯 ResumeIQ - AI Resume Analyzer")

uploaded_file = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"])

if uploaded_file is not None:

    # ✅ FIX 1: correct extension handle
    file_name = uploaded_file.name
    file_ext = os.path.splitext(file_name)[1]

    # safety check
    if file_ext not in [".pdf", ".txt"]:
        st.error("Only PDF or TXT files allowed")
        st.stop()

    # create proper temp file WITH extension
    temp_path = f"temp_resume{file_ext}"

    with open(temp_path, "wb") as f:
        f.write(uploaded_file.read())

    st.info("Parsing resume...")

    try:
        resume_text = parse_resume(temp_path)
    except Exception as e:
        st.error(f"Parse error: {e}")
        st.stop()

    st.success(f"Extracted {len(resume_text)} characters")

    if st.button("Analyze Resume"):

        st.info("Running AI analysis...")

        try:
            analysis = analyze_resume(resume_text)
            sections = interpret_section_scores(analysis)
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.stop()

        st.subheader("📊 Overall Score")
        st.metric("Score", f"{analysis['overall_score']}/100")

        st.subheader("🤖 ATS Score")
        st.metric("ATS", f"{analysis['ats_score']}/100")

        st.subheader("🎯 Verdict")
        st.write(analysis["one_line_verdict"])

        st.subheader("💪 Strengths")
        st.write(analysis["strengths"])

        st.subheader("🚨 Critical Issues")
        st.write(analysis["critical_issues"])

        st.subheader("📋 Section Scores")
        st.json(analysis["section_scores"])

        st.subheader("✨ Improved Bullets")
        st.json(analysis["improved_bullets"])