import streamlit as st
import os
from rag_engine import load_llm, initialize_vector_store, get_rag_chain
from datetime import datetime

from config import config
from logger_config import shifu_logger

st.set_page_config(page_title="Shifu", layout="wide")

# Custom CSS for white background
st.markdown("""
<style>
    .stApp {
        background-color: #f4f4f5;
    }
    .main {
        background-color: #f4f4f5;
    }
    body {
        color: #18181b;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #18181b !important;
        font-weight: 800 !important;
    }
    p, li, span {
        color: #27272a;
    }
    /* Style the sidebar for a premium feel */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e4e4e7;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource(ttl=300)  
def setup_resources():
    """Setup resources with proper error handling"""
    try:
        shifu_logger.info("Initializing Shifu resources...")
        llm = load_llm()
        vector_store = initialize_vector_store()
        
        if llm and vector_store:
            qa_chain = get_rag_chain(llm, vector_store)
            shifu_logger.info("Resources initialized successfully")
            return llm, qa_chain
        else:
            shifu_logger.error("Failed to initialize resources")
            return None, None
    except Exception as e:
        shifu_logger.critical("Error during resource setup", exception=e)
        return None, None

llm, qa_chain = setup_resources()

if not llm or not qa_chain:
    st.error("Failed to initialize Shifu Engine. Please check configuration and try again.")
    shifu_logger.critical("Application startup failed - missing critical resources")
    st.stop()


st.title("Shifu - The AI Knowledge Agent")
st.markdown("Your personal AI learning coach for **SetuSchool**.")

# Sidebar for Shifu Identity
with st.sidebar:
    st.markdown("### 🤖 About Shifu")
    st.info("Shifu is your intelligent learning companion. Generate expert roadmaps and unlock deep knowledge in minutes.")
    st.markdown("---")
    if st.button("🗑️ Clear All Progress"):
        st.session_state.clear()
        shifu_logger.info("User cleared all session data")
        st.rerun()

# Main Interface: Dedicated to Learning Roadmap
from roadmap_ui import roadmap_page
roadmap_page(llm)

st.markdown("---")
