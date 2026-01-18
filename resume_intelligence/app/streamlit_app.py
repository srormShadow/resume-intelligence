import streamlit as st
from pathlib import Path
import tempfile

from resume_intelligence.core.document import Document
from resume_intelligence.core.matching.ats_score import compute_ats_score
from resume_intelligence.core.normalizer import normalize_document
from resume_intelligence.core.parser import parse_document
from resume_intelligence.core.matching.matcher import ConceptMatcher
from resume_intelligence.core.semantics.concept import ConceptSource
from resume_intelligence.core.semantics.consolidator import consolidate_concepts
from resume_intelligence.core.semantics.extractor import extract_concepts

st.set_page_config(
    page_title="Resume Intelligence",
    layout="wide",
)

st.title("📄 Resume Intelligence – ATS Match Analyzer")

st.markdown(
    "Upload your **resume** and paste a **job description** to analyze ATS compatibility."
)

# ----------------------------
# Inputs
# ----------------------------
col1, col2 = st.columns(2)

with col1:
    resume_file = st.file_uploader(
        "Upload Resume (PDF or DOCX)",
        type=["pdf", "docx"],
    )

with col2:
    jd_text = st.text_area(
        "Paste Job Description",
        height=300,
        placeholder="Paste the job description here...",
    )

analyze = st.button("🔍 Analyze Resume")

# ----------------------------
# Processing
# ----------------------------
if analyze:
    if not resume_file or not jd_text.strip():
        st.error("Please upload a resume and paste a job description.")
        st.stop()

    with st.spinner("Processing documents..."):
        # Save resume to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(resume_file.name).suffix) as tmp:
            tmp.write(resume_file.read())
            resume_path = Path(tmp.name)

        # Parse documents
        resume_text = parse_document(str(resume_path))
        resume_doc = Document(raw_text=resume_text)
        normalize_document(resume_doc)

        # jd_text = parse_document(str(jd_text))
        jd_doc = Document(raw_text=jd_text)
        normalize_document(jd_doc)

        # Extract & consolidate concepts
        resume_concepts = consolidate_concepts(
            extract_concepts(resume_doc, ConceptSource.RESUME)
        )
        jd_concepts = consolidate_concepts(
            extract_concepts(jd_doc, ConceptSource.JD)
        )

        # Match concepts
        matcher = ConceptMatcher()
        match_results = matcher.match(jd_concepts, resume_concepts)

        # ATS score
        ats_score = compute_ats_score(jd_concepts, match_results)

    # ----------------------------
    # Output
    # ----------------------------
    st.success(f"🎯 ATS Match Score: **{ats_score:.2f}%**")

    def render_section(title, rows, color):
        if not rows:
            return

        st.subheader(title)
        for r in rows:
            st.markdown(
                f"- **{r['jd_concept']}** "
                f"({r['jd_type']}) → "
                f"`{r['matched_resume_concept']}` "
                f"**({r['score']})**"
            )

    colA, colB, colC = st.columns(3)

    with colA:
        render_section("✅ Matched", match_results["matched"], "green")

    with colB:
        render_section("⚠️ Partial", match_results["partial"], "orange")

    with colC:
        render_section("❌ Missing", match_results["missing"], "red")
