import streamlit as st
from utils.table_extraction import extract_tables_from_pdf
from utils.summarization import initialize_llm_pipeline, summarize_table
import pandas as pd
import os
import uuid
from mistralai import Mistral
from PyPDF2 import PdfReader  # Added for PDF preview
import base64


def main():
    # Set page configuration
    st.set_page_config(
        page_title="📄 PDF Table Extraction & Summarization",
        layout="wide",
        page_icon="📈",
    )
    
    # Custom CSS for additional styling
    st.markdown("""
        <style>
            /* Main Background */
            .main {
                background-color: #f0f4f7;
            }
            /* Sidebar Styling */
            .sidebar .sidebar-content {
                background-image: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            /* Button Styling */
            .stButton > button {
                color: white;
                background-color: #28a745;
            }
            .stButton > button:hover {
                background-color: #218838;
            }
            /* Header Styling */
            .header {
                font-size: 2.5em;
                font-weight: bold;
                color: #333333;
                text-align: center;
                margin-bottom: 20px;
            }
            /* Subheader Styling */
            .subheader {
                font-size: 1.8em;
                color: #444444;
                margin-top: 20px;
                margin-bottom: 10px;
            }
            /* Section Styling */
            .section {
                background-color: #ffffff;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }
            /* Spinner Styling */
            .stSpinner {
                color: #ff9800;
            }
            /* Success Message Styling */
            .success {
                color: #28a745;
                font-weight: bold;
            }
            /* Error Message Styling */
            .error {
                color: #dc3545;
                font-weight: bold;
            }
            /* Warning Message Styling */
            .warning {
                color: #ffc107;
                font-weight: bold;
            }
            /* Highlighted Text */
            .highlight {
                background-color: #ffff99;
                padding: 2px 4px;
                border-radius: 3px;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<div class="header">📄 PDF Table Extraction and Summarization</div>', unsafe_allow_html=True)
    
    # Sidebar for file upload
    with st.sidebar:
        st.markdown('<h2 style="color: white;">Upload Your PDF</h2>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
        if uploaded_file is not None:
            # Save uploaded file to a unique temporary location
            temp_filename = f"temp_{uuid.uuid4().hex}.pdf"
            with open(temp_filename, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.markdown('<div class="success">✅ PDF Uploaded Successfully!</div>', unsafe_allow_html=True)

    if uploaded_file is not None:
        # ------------------ Preview Section ------------------
        st.markdown('<div class="section"><div class="subheader">📖 PDF Preview</div>', unsafe_allow_html=True)
        try:
            with open(temp_filename, "rb") as f:
                pdf_bytes = f.read()
                base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
                pdf_display = f"""
                    <iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>
                """
                st.markdown(pdf_display, unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div class="error">⚠️ Error previewing PDF: {e}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ------------------ Extracted Tables Section ------------------
        st.markdown('<div class="section"><div class="subheader">📊 Extracted Tables</div>', unsafe_allow_html=True)
        with st.spinner("🔄 Extracting tables from PDF..."):
            try:
                dfs, table_html = extract_tables_from_pdf(temp_filename)
            except Exception as e:
                st.markdown(f'<div class="error">⚠️ Error extracting tables: {e}</div>', unsafe_allow_html=True)
                os.remove(temp_filename)
                return

        if dfs:
            for idx, df in enumerate(dfs):
                with st.expander(f"🔍 View Table {idx + 1}"):
                    st.dataframe(df, use_container_width=True)
        else:
            st.markdown('<div class="warning">⚠️ No tables found in the uploaded PDF.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ------------------ Summarization Section ------------------
        st.markdown('<div class="section"><div class="subheader">📝 Summarization</div>', unsafe_allow_html=True)
        if dfs:
            llm_pipeline = initialize_llm_pipeline()
            # Summarization
            st.header("📝 Summarization")
            try:
                for idx, df in enumerate(dfs):
                    table_text = df.to_string(index=False)
                    summary = summarize_table(llm_pipeline, table_text)
                    st.subheader(f"Summary of Table {idx + 1}")
                    
                    st.write(summary)
            except Exception as e:
                st.markdown(f'<div class="error">⚠️ Error during summarization: {e}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Clean up temporary file after all operations
        try:
            os.remove(temp_filename)
        except Exception as e:
            st.markdown(f'<div class="warning">⚠️ Could not delete temporary file: {e}</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()