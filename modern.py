import streamlit as st
from utils.table_extraction import extract_tables_from_pdf
from utils.summarization import initialize_llm_pipeline, summarize_table
import pandas as pd
import os
import uuid
from PyPDF2 import PdfReader
import base64

def main():
    # Set page configuration
    st.set_page_config(
        page_title="PDF Table Extraction & Summarization",
        layout="wide",
        page_icon="📈",
    )
    
    # Custom CSS for styling
    st.markdown("""
        <style>
            /* Main Page Background */
            body {
                background-color: #f7f9fc;
                font-family: 'Arial', sans-serif;
            }
            /* Sidebar Styling */
            .css-1d391kg {
                background: linear-gradient(to bottom, #4b79a1, #283e51);
                color: white;
            }
            .css-1d391kg h2 {
                color: #ffffff !important;
            }
            /* Upload Button */
            .css-1d391kg .css-1btn {
                background-color: #2c3e50;
                border-radius: 8px;
            }
            /* Header */
            .header {
                font-size: 2.8em;
                color: #2c3e50;
                text-align: center;
                font-weight: 700;
                margin: 20px 0;
            }
            /* Subheader */
            .subheader {
                font-size: 1.8em;
                color: #34495e;
                font-weight: 600;
                margin-bottom: 10px;
            }
            /* Section Card */
            .section {
                background: white;
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
                margin-bottom: 20px;
            }
            /* Buttons */
            .stButton > button {
                color: white;
                background: linear-gradient(135deg, #1d8348, #52be80);
                border-radius: 8px;
                border: none;
                padding: 10px 15px;
                font-size: 16px;
            }
            .stButton > button:hover {
                background: linear-gradient(135deg, #27ae60, #58d68d);
            }
            /* Table Styling */
            .stDataFrame {
                border-radius: 8px;
                border: 1px solid #ddd;
            }
            /* PDF Preview Frame */
            iframe {
                border-radius: 12px;
                border: 2px solid #4b79a1;
            }
            /* Messages */
            .success {
                color: #28a745;
                font-weight: bold;
            }
            .error {
                color: #e74c3c;
                font-weight: bold;
            }
            .warning {
                color: #f39c12;
                font-weight: bold;
            }
        </style>
    """, unsafe_allow_html=True)

    # Header Section
    st.markdown('<div class="header">📄 PDF Table Extraction and Summarization</div>', unsafe_allow_html=True)

    # Sidebar for file upload
    with st.sidebar:
        st.markdown('<h2>Upload Your PDF</h2>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
        if uploaded_file is not None:
            temp_filename = f"temp_{uuid.uuid4().hex}.pdf"
            with open(temp_filename, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.markdown('<div class="success">✅ PDF Uploaded Successfully!</div>', unsafe_allow_html=True)

    # Main Content
    if uploaded_file is not None:
        # PDF Preview Section
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

        # Extracted Tables Section
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

        # Summarization Section
        st.markdown('<div class="section"><div class="subheader">📝 Summarization</div>', unsafe_allow_html=True)
        if dfs:
            try:
                llm_pipeline = initialize_llm_pipeline()
                for idx, df in enumerate(dfs):
                    table_text = df.to_string(index=False)
                    summary = summarize_table(llm_pipeline, table_text)
                    st.subheader(f"Summary of Table {idx + 1}")
                    st.write(summary)
            except Exception as e:
                st.markdown(f'<div class="error">⚠️ Error during summarization: {e}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Clean up temporary file
        try:
            os.remove(temp_filename)
        except Exception as e:
            st.markdown(f'<div class="warning">⚠️ Could not delete temporary file: {e}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()