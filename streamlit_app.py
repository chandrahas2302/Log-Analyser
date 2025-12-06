import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd
import csv
from io import StringIO
import os 


# Page configuration
st.set_page_config(
    page_title="Log Analyser",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:5000/api"

# Custom CSS
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1rem;
    }
    .analysis-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #0066cc;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("⚙️ Configuration")
# Health check
with st.sidebar:
    analysis_type = st.sidebar.radio(
    "Select Analysis Type",
    ["Apache/Nginx", "Linux System", "Kubernetes"],
    help="Choose the type of logs you want to analyze"
)

analysis_map = {
    "Apache/Nginx": "apache",
    "Linux System": "linux",
    "Kubernetes": "kubernetes"
}

# Main content
st.title("📊 Log Analyser")
st.markdown("Analyze system logs using AI-powered insights")

# Create tabs
tab1, tab2,  = st.tabs(["📝 Direct Input", "📁 File Upload"])

# Tab 1: Direct Input
with tab1:
    st.subheader("Paste Log Content")
    
    st.info(f"Current Mode: **{analysis_type}**")
    
    
    log_input = st.text_area(
        "Enter or paste logs here:",
        height=250,
        placeholder="Paste your logs here...",
        key="direct_input"
    )
    
    if st.button("🔍 Analyze Logs", key="analyze_direct", use_container_width=True):
        if not log_input.strip():
            st.error("❌ Please enter some log content")
        else:
            with st.spinner("🤖 Analyzing logs..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/analyze",
                        json={
                            'log_text': log_input,
                            'analysis_type': analysis_map[analysis_type]
                        },
                        timeout=300
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.last_analysis = result
                        
                        # Display results
                        st.markdown("### 📋 Analysis Results")
                        st.markdown("""
                        <div class="success-box">
                        ✅ Analysis completed successfully
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Log Size", f"{result['log_size']} bytes")
                        with col2:
                            st.metric("Analysis Type", result['analysis_type'].capitalize())
                        with col3:
                            st.metric("Timestamp", result['timestamp'].split('T')[1][:8])
                        
                        st.divider()
                        st.markdown("### 📊 Analysis Output")
                        st.markdown("""
                        <div class="analysis-box">
                        """ + result['analysis'] + """
                        </div>
                        """, unsafe_allow_html=True)
                        
                        csv_buffer = StringIO()
                        csv_writer = csv.writer(csv_buffer)
                        csv_writer.writerow(result.keys())
                        csv_writer.writerow(result.values())

                        st.download_button(
                            label="💾 Download as CSV",
                            data=csv_buffer.getvalue(),
                            file_name=f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                
                except requests.exceptions.Timeout:
                    st.error("⏱️ Request timed out. Please try again.")
                except Exception as e:
                    st.error(f"❌ Connection error: {str(e)}")

# Tab 2: File Upload
with tab2:
    st.subheader("Upload Log File")
    
    uploaded_file = st.file_uploader(
        "Choose a log file",
        type=['txt', 'log'],
        help="Supported formats: .txt, .log"
    )
    
    if uploaded_file is not None:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("File Size", f"{uploaded_file.size / 1024:.2f} KB")
        with col2:
            st.metric("Analysis Type", analysis_type)
        
        if st.button("🔍 Analyze File", key="analyze_file", use_container_width=True):
            with st.spinner("🤖 Processing file..."):
                try:
                    files = {
                        'file': (uploaded_file.name, uploaded_file.getvalue())
                    }
                    data = {
                        'analysis_type': analysis_map[analysis_type]
                    }
                    
                    response = requests.post(
                        f"{API_BASE_URL}/analyze-file",
                        files=files,
                        data=data,
                        timeout=300
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.last_analysis = result
                        
                        st.markdown("""
                        <div class="success-box">
                        ✅ Analysis completed successfully
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Log Size", f"{result['log_size']} bytes")
                        with col2:
                            st.metric("File", result['filename'])
                        with col3:
                            st.metric("Type", result['analysis_type'].capitalize())
                        
                        st.divider()
                        st.markdown("### 📊 Analysis Output")
                        from html import escape
                        safe_analysis = escape(result['analysis'])
                        st.markdown(f"""
                        <div class="analysis-box">
                        <pre>{safe_analysis}</pre>
                        </div>
                        """, unsafe_allow_html=True)
                                                
                        csv_buffer = StringIO()
                        csv_writer = csv.writer(csv_buffer)
                        csv_writer.writerow(result.keys())
                        csv_writer.writerow(result.values())

                        st.download_button(
                            label="💾 Download as CSV",
                            data=csv_buffer.getvalue(),
                            file_name=f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )

                    else:
                        st.error(f"❌ Error: {response.json().get('error', 'Unknown error')}")
                
                except Exception as e:
                    st.error(f"❌ Connection error: {str(e)}")


# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #888; padding: 2rem;'>
    <p>Log Analysis Suite v1.0 | Powered by Ollama & Streamlit</p>
</div>
""", unsafe_allow_html=True)