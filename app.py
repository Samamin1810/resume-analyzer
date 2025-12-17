import streamlit as st
from utils import (
    extract_text_from_pdf,
    clean_text,
    calculate_match,
    recommend_best_role
)

st.set_page_config(
    page_title="Resume Analyzer & Job Role Recommendation",
    layout="centered"
)

st.title("Resume Analyzer & Job Match Tool")
st.write(
    "Analyze resume–job compatibility and optionally discover the most suitable job role."
)

# ---------- SESSION STATE ----------
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False


# ---------- INPUTS ----------
resume_file = st.file_uploader("Upload Resume (PDF only)", type=["pdf"])
job_description = st.text_area("Paste Job Description here", height=200)


# ---------- ANALYZE ----------
if st.button("Analyze Resume"):
    if resume_file is None or job_description.strip() == "":
        st.warning("Please upload a resume and paste a job description.")
    else:
        with st.spinner("Analyzing resume..."):
            resume_text = clean_text(
                extract_text_from_pdf(resume_file)
            )
            jd_text = clean_text(job_description)

            score, matched, missing = calculate_match(resume_text, jd_text)

            st.session_state.score = score
            st.session_state.matched = matched
            st.session_state.missing = missing
            st.session_state.resume_text = resume_text
            st.session_state.analysis_done = True


# ---------- RESULTS ----------
if st.session_state.analysis_done:

    st.success("Analysis Completed")

    st.subheader("Resume–Job Match Score")
    st.metric("Match Percentage", f"{st.session_state.score}%")

    st.subheader("Matching Keywords")
    st.write(
        ", ".join(st.session_state.matched[:30])
        if st.session_state.matched else "No strong matches found."
    )

    st.subheader("Missing Keywords")
    st.write(
        ", ".join(st.session_state.missing[:30])
        if st.session_state.missing else "No major gaps detected."
    )

    st.subheader("Interpretation")
    if st.session_state.score >= 70:
        st.write("Strong alignment. Resume is well suited for this role.")
    elif st.session_state.score >= 40:
        st.write("Moderate alignment. Resume can be improved.")
    else:
        st.write("Low alignment. Consider upskilling or tailoring your resume.")

    st.divider()

    # ---------- OPTIONAL ROLE ----------
    show_role = st.checkbox("Show Best-Fit Job Role Recommendation")

    if show_role:
        best_role, role_score = recommend_best_role(
            st.session_state.resume_text
        )

        if role_score < 20:
            st.warning(
                "No strong role fit detected based on keyword similarity. "
                "Human review may still identify suitable roles."
            )
        else:
            st.subheader("Best-Fit Job Role Recommendation")
            st.info(
                f"**{best_role}**\n\n"
                f"Role alignment confidence: {role_score}%"
            )
