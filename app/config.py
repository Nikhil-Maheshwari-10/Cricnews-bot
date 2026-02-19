import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Cricket API Configuration ---
CRICKETDATA_API_KEY = os.getenv("CRICKETDATA_API_KEY")
CRICKETDATA_BASE_URL = "https://api.cricapi.com/v1"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- System Prompt for Cricket-Only Chatbot ---
CRICKET_SYSTEM_PROMPT = os.getenv("CRICKET_SYSTEM_PROMPT")
