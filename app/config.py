import os
from dotenv import load_dotenv

# Load environment variables (Local development)
load_dotenv()

def get_secret(key):
    # Try environment variable first
    val = os.getenv(key)
    if val:
        return val
    
    # Fallback to streamlit secrets
    try:
        import streamlit as st
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return None

# --- Cricket API Configuration ---
CRICKETDATA_API_KEY = get_secret("CRICKETDATA_API_KEY")
CRICKETDATA_BASE_URL = "https://api.cricapi.com/v1"
GEMINI_API_KEY = get_secret("GEMINI_API_KEY")

# --- System Prompt for Cricket-Only Chatbot ---
CRICKET_SYSTEM_PROMPT = get_secret("CRICKET_SYSTEM_PROMPT")
