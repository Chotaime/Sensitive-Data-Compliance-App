import os
import shutil

import streamlit as st
import pandas as pd

# -----------------------------
# Import Utility Functions
# -----------------------------

from utils.parser import read_pdf, read_txt, read_csv
from utils.detector import detect_sensitive_data
from utils.risk import calculate_risk
from utils.summary import generate_summary
from utils.rag import create_vector_store, ask_rag

from utils.mask import (
    mask_email,
    mask_phone,
    mask_pan,
    mask_aadhaar,
    mask_credit_card,
    mask_password,
    mask_api_key,
    mask_employee_id
)

from utils.audit import log_event


# -----------------------------
# Page Configuration
# -----------------------------

st.set_page_config(
    page_title="Sensitive Data Detection & Compliance Assistant",
    page_icon="🔒",
    layout="wide"
)

st.title("🔒 Sensitive Data Detection & Compliance Assistant")

st.write(
    "Upload one or more PDF, TXT or CSV documents to detect sensitive "
    "information, classify risk, generate compliance reports and ask "
    "questions using RAG."
)

st.markdown("### Features")

st.markdown("""
- 🔍 Sensitive Data Detection
- ⚠ Risk Classification
- 📄 AI Compliance Report
- 💬 RAG Question Answering
- 🔐 Data Masking
- 📜 Audit Logging
""")


# ---------------------------------------------------
# Session State
# ---------------------------------------------------

if "vector_dbs" not in st.session_state:
    st.session_state.vector_dbs = {}

if "selected_doc" not in st.session_state:
    st.session_state.selected_doc = None

if "processed_docs" not in st.session_state:
    st.session_state.processed_docs = {}

if "detected_docs" not in st.session_state:
    st.session_state.detected_docs = {}

if "summary_docs" not in st.session_state:
    st.session_state.summary_docs = {}

if "risk_docs" not in st.session_state:
    st.session_state.risk_docs = {}


# ---------------------------------------------------
# Upload Files
# ---------------------------------------------------

uploaded_files = st.file_uploader(
    "Upload Documents",
    type=["pdf", "txt", "csv"],
    accept_multiple_files=True
)


# ---------------------------------------------------
# Process Uploaded Documents
# ---------------------------------------------------

if uploaded_files:

    for uploaded_file in uploaded_files:

        # Skip already processed documents
        if uploaded_file.name in st.session_state.processed_docs:
            continue

        extension = uploaded_file.name.split(".")[-1].lower()

        try:

            # -------------------------
            # Read document
            # -------------------------

            if extension == "pdf":
                text = read_pdf(uploaded_file)

            elif extension == "txt":
                text = read_txt(uploaded_file)

            elif extension == "csv":
                text = read_csv(uploaded_file)

            else:
                continue

            # Save original text
            st.session_state.processed_docs[
                uploaded_file.name
            ] = text

            # -------------------------
            # Audit Log
            # -------------------------

            log_event(
                action="Upload",
                filename=uploaded_file.name,
                details="Document uploaded"
            )

            # -------------------------
            # Create Vector Database
            # -------------------------

            safe_name = uploaded_file.name.replace(".", "_")

            db_path = create_vector_store(
                text,
                safe_name
            )

            st.session_state.vector_dbs[
                uploaded_file.name
            ] = db_path

            # -------------------------
            # Sensitive Detection
            # -------------------------

            detected = detect_sensitive_data(text)

            st.session_state.detected_docs[
                uploaded_file.name
            ] = detected

            total_items = sum(
                len(v)
                for v in detected.values()
            )

            log_event(
                action="Sensitive Detection",
                filename=uploaded_file.name,
                details=f"{total_items} sensitive items detected"
            )

            # -------------------------
            # Risk Analysis
            # -------------------------

            risk_score, risk_level = calculate_risk(
                detected
            )

            st.session_state.risk_docs[
                uploaded_file.name
            ] = (
                risk_score,
                risk_level
            )

            log_event(
                action="Risk Analysis",
                filename=uploaded_file.name,
                details=risk_level
            )

            # -------------------------
            # AI Compliance Report
            # -------------------------

            with st.spinner(
                f"Generating AI report for {uploaded_file.name}..."
            ):

                summary = generate_summary(
                    text,
                    detected,
                    risk_level,
                    risk_score
                )

            st.session_state.summary_docs[
                uploaded_file.name
            ] = summary

            log_event(
                action="Compliance Report",
                filename=uploaded_file.name,
                details="Generated successfully"
            )

        except Exception as e:

            st.error(
                f"Error processing {uploaded_file.name}: {e}"
            )


# ---------------------------------------------------
# Select Active Document
# ---------------------------------------------------

if st.session_state.processed_docs:

    selected_doc = st.selectbox(
        "Select Document",
        list(st.session_state.processed_docs.keys())
    )

    st.session_state.selected_doc = selected_doc

    text = st.session_state.processed_docs[selected_doc]

    detected = st.session_state.detected_docs[selected_doc]

    risk_score, risk_level = st.session_state.risk_docs[selected_doc]

    summary = st.session_state.summary_docs[selected_doc]

else:

    selected_doc = None
    text = ""
    detected = {}
    summary = ""
    risk_score = 0
    risk_level = ""
# =====================================================
# Document Preview & Sensitive Data Summary
# =====================================================

left, right = st.columns([2, 1])

# -----------------------------------------------------
# Left Column
# -----------------------------------------------------

with left:

    st.subheader("📄 Document Preview")

    if selected_doc:

        st.text_area(
            "Extracted Text",
            value=text,
            height=450
        )

    else:

        st.info("Upload a document to preview its contents.")

# -----------------------------------------------------
# Right Column
# -----------------------------------------------------

with right:

    st.subheader("🚨 Sensitive Data Summary")

    if selected_doc:

        total_sensitive = sum(
            len(v)
            for v in detected.values()
        )

        st.metric(
            "Total Sensitive Items",
            total_sensitive
        )

        st.divider()

        for key, values in detected.items():

            count = len(values)

            if count > 0:

                st.success(f"{key}: {count}")

            else:

                st.caption(f"{key}: 0")

    else:

        st.info("No document selected.")

# =====================================================
# Risk Classification
# =====================================================

st.divider()

st.subheader("⚠ Risk Classification")

if selected_doc:

    col1, col2 = st.columns([1, 2])

    with col1:

        st.metric(
            "Risk Score",
            risk_score
        )

    with col2:

        if "High" in risk_level:

            st.error(f"🔴 {risk_level}")

        elif "Medium" in risk_level:

            st.warning(f"🟡 {risk_level}")

        else:

            st.success(f"🟢 {risk_level}")

else:

    st.info("Upload a document first.")

# =====================================================
# Sensitive Information Details
# =====================================================

st.divider()

st.subheader("📑 Sensitive Information Details")

show_original = st.checkbox(
    "Show Original Sensitive Data",
    value=False
)

if selected_doc:

    for key, values in detected.items():

        if not values:
            continue

        with st.expander(f"{key} ({len(values)})"):

            for item in values:

                if show_original:

                    st.write(f"• {item}")

                else:

                    if key == "Email":

                        st.write(f"• {mask_email(item)}")

                    elif key == "Phone":

                        st.write(f"• {mask_phone(item)}")

                    elif key == "PAN":

                        st.write(f"• {mask_pan(item)}")

                    elif key == "Aadhaar":

                        st.write(f"• {mask_aadhaar(item)}")

                    elif key == "Credit Card":

                        st.write(f"• {mask_credit_card(item)}")

                    elif key == "Password":

                        st.write(f"• {mask_password(item)}")

                    elif key == "API Key":

                        st.write(f"• {mask_api_key(item)}")

                    elif key == "Employee ID":

                        st.write(f"• {mask_employee_id(item)}")

                    else:

                        st.write(f"• {item}")

else:

    st.info("No document selected.")

# =====================================================
# AI Compliance Report
# =====================================================

st.divider()

st.subheader("📋 AI Compliance Report")

if selected_doc:

    st.markdown(summary)

else:

    st.info("Upload a document to generate an AI compliance report.")
# =====================================================
# RAG Question Answering
# =====================================================

st.divider()

st.subheader("💬 Ask Questions About the Selected Document")

question = st.text_input(
    "Ask anything about the selected document"
)

col1, col2 = st.columns(2)

with col1:

    ask_button = st.button(
        "🔍 Ask AI",
        use_container_width=True
    )

with col2:

    clear_button = st.button(
        "🗑 Clear All Databases",
        use_container_width=True
    )

# -----------------------------------------------------
# Ask AI
# -----------------------------------------------------

if ask_button:

    if selected_doc is None:

        st.warning(
            "Please upload and select a document first."
        )

    elif question.strip() == "":

        st.warning(
            "Please enter a question."
        )

    else:

        try:

            db_path = st.session_state.vector_dbs[
                selected_doc
            ]

            with st.spinner(
                "Searching document..."
            ):

                answer = ask_rag(
                    question,
                    db_path
                )

            st.success("Answer")

            st.write(answer)

            # -------------------------
            # Audit Log
            # -------------------------

            log_event(
                action="RAG Query",
                filename=selected_doc,
                details=question
            )

        except Exception as e:

            st.error(f"RAG Error : {e}")

# =====================================================
# Clear Vector Databases
# =====================================================

if clear_button:

    try:

        if os.path.exists("vector_db"):

            shutil.rmtree("vector_db")

        st.session_state.vector_dbs.clear()
        st.session_state.processed_docs.clear()
        st.session_state.detected_docs.clear()
        st.session_state.summary_docs.clear()
        st.session_state.risk_docs.clear()

        log_event(
            action="Database",
            filename="",
            details="Vector database cleared"
        )

        st.success(
            "Vector databases cleared successfully."
        )

        st.rerun()

    except Exception as e:

        st.error(e)

# =====================================================
# Uploaded Documents
# =====================================================

st.divider()

st.subheader("📂 Uploaded Documents")

if st.session_state.processed_docs:

    for i, doc in enumerate(
        st.session_state.processed_docs.keys(),
        start=1
    ):

        if doc == selected_doc:

            st.success(
                f"{i}. {doc} (Selected)"
            )

        else:

            st.write(
                f"{i}. {doc}"
            )

else:

    st.info("No uploaded documents.")

# =====================================================
# Audit Log Viewer
# =====================================================

st.divider()

st.subheader("📜 Audit Log")

if os.path.exists("audit_log.csv"):

    df = pd.read_csv("audit_log.csv")

    st.dataframe(
        df,
        use_container_width=True
    )

else:

    st.info("No audit logs available.")

# =====================================================
# Example Questions
# =====================================================

st.divider()

st.subheader("💡 Example Questions")

st.markdown("""
- What sensitive data exists in this document?

- Summarize this document.

- How many email addresses are present?

- How many phone numbers are present?

- What is the PAN number?

- What is the Aadhaar number?

- Does this document contain confidential information?

- What compliance risks are identified?

- List all detected sensitive information.
""")

# =====================================================
# Footer
# =====================================================

st.divider()

st.markdown(
"""
<div style="text-align:center">

### 🔒 Sensitive Data Detection & Compliance Assistant

Built using

**Streamlit • Gemini 2.5 Flash • LangChain • ChromaDB • Sentence Transformers**

#### Features

✅ Sensitive Data Detection

✅ Risk Classification

✅ AI Compliance Report

✅ RAG Question Answering

✅ Data Masking

✅ Multi-document Support

✅ Audit Logging

</div>
""",
unsafe_allow_html=True
)