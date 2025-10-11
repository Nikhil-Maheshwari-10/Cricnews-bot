import streamlit as st
import os
from litellm import completion
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Logger Setup ---
def setup_logger():
    try:
        import colorlog
        logger = colorlog.getLogger('cricket_chatbot')
        if not logger.hasHandlers():
            handler = colorlog.StreamHandler()
            handler.setFormatter(colorlog.ColoredFormatter(
                '%(log_color)s%(levelname)s:%(name)s:%(reset)s %(message)s',
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'bold_red',
                }
            ))
            logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
    except ImportError:
        logger = logging.getLogger('cricket_chatbot')
        if not logger.hasHandlers():
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(levelname)s:%(name)s: %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
    return logger

logger = setup_logger()

# --- Cricket API Configuration ---
CRICKETDATA_API_KEY = os.getenv("CRICKETDATA_API_KEY")
CRICKETDATA_BASE_URL = "https://api.cricapi.com/v1"

# --- System Prompt for Cricket-Only Chatbot ---
CRICKET_SYSTEM_PROMPT = """You are a friendly cricket news assistant. Your role is to ONLY answer questions related to cricket.

Rules:
1. Only respond to cricket-related questions (matches, players, teams, tournaments, records, news, etc.)
2. If a user asks about anything NOT related to cricket, politely say: "I'm a cricket specialist chatbot and can only answer cricket-related questions. Please ask me about cricket matches, players, teams, or cricket news!"
3. Be conversational, friendly, and informative
4. Use the cricket data provided in the context to give accurate, real-time answers
5. Remember previous questions in the conversation and maintain context
6. If asked about follow-up questions like "what about the previous match?" or "tell me more", refer to the conversation history

Cricket topics you can discuss:
- Live scores and match updates
- Recent match results
- Upcoming fixtures
- Player statistics and records
- Team news and rankings
- Tournament schedules (IPL, World Cup, T20, ODI, Test)
- Cricket history and trivia
- Match predictions and analysis"""

# --- Function to Fetch Live/Current Cricket Matches ---
def fetch_current_matches():
    """
    Fetch current cricket matches using CricketData API
    API Docs: https://cricketdata.org/how-to-use-cricket-data-api.aspx
    """
    try:
        if not CRICKETDATA_API_KEY:
            return "Cricket API key not configured. Please set CRICKETDATA_API_KEY in your .env file."
        
        url = f"{CRICKETDATA_BASE_URL}/currentMatches"
        params = {
            "apikey": CRICKETDATA_API_KEY,
            "offset": 0
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("status") != "success":
                return f"API Error: {data.get('status', 'Unknown error')}"
            
            matches = data.get("data", [])
            
            if not matches:
                return "No current matches found."
            
            matches_info = []
            
            for match in matches[:10]:  # Get top 10 matches
                match_type = match.get("matchType", "Unknown")
                name = match.get("name", "Unknown Match")
                status = match.get("status", "Unknown")
                venue = match.get("venue", "Unknown Venue")
                date = match.get("date", "")
                teams = match.get("teams", [])
                teamInfo = match.get("teamInfo", [])
                score = match.get("score", [])
                
                match_info = f"📍 Match: {name}\n"
                match_info += f"   Type: {match_type}\n"
                match_info += f"   Venue: {venue}\n"
                match_info += f"   Status: {status}\n"
                
                if score:
                    match_info += "   Scores:\n"
                    for s in score:
                        inning = s.get("inning", "")
                        runs = s.get("r", "")
                        wickets = s.get("w", "")
                        overs = s.get("o", "")
                        match_info += f"      {inning}: {runs}/{wickets} ({overs} overs)\n"
                
                matches_info.append(match_info)
            
            return "\n".join(matches_info) if matches_info else "No detailed match information available."
        
        else:
            return f"Failed to fetch cricket data. Status code: {response.status_code}"
            
    except Exception as e:
        logger.error(f"Error fetching cricket matches: {str(e)}")
        return f"Unable to fetch cricket data. Error: {str(e)}"

# --- Function to Fetch Match Info by ID ---
def fetch_match_info(match_id):
    """
    Fetch detailed match information by match ID
    """
    try:
        if not CRICKETDATA_API_KEY:
            return "Cricket API key not configured."
        
        url = f"{CRICKETDATA_BASE_URL}/match_info"
        params = {
            "apikey": CRICKETDATA_API_KEY,
            "id": match_id
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return str(data.get("data", {}))
        
        return "Match details not available."
        
    except Exception as e:
        logger.error(f"Error fetching match details: {str(e)}")
        return "Unable to fetch match details."

# --- Function to Get Cricket Context for LLM ---
def get_cricket_context():
    """
    Fetch comprehensive cricket data to provide as context to LLM
    """
    context_parts = []
    
    # Get current matches
    matches_data = fetch_current_matches()
    context_parts.append(f"=== CURRENT & RECENT MATCHES ===\n{matches_data}")
    
    # Add current date for temporal context
    today = datetime.now().strftime("%Y-%m-%d %A")
    context_parts.append(f"\n=== TODAY'S DATE ===\n{today}")
    
    return "\n\n".join(context_parts)

# --- Function to Generate Cricket Chatbot Response ---
def generate_cricket_response(user_message, conversation_history):
    """
    Generate response using Gemma model with cricket API data and full conversation history.
    
    Args:
        user_message: Current user question
        conversation_history: List of all previous messages in session
    """
    try:
        # Fetch latest cricket data for context
        cricket_context = get_cricket_context()
        
        # Build messages for LLM with FULL conversation history
        messages = []
        
        # Add system prompt with cricket context as first user message
        system_message = f"""{CRICKET_SYSTEM_PROMPT}

=== LIVE CRICKET DATA CONTEXT ===
{cricket_context}

Important: Use the above cricket data to answer questions accurately. Remember the entire conversation history and maintain context across questions."""
        
        messages.append({
            "role": "user",
            "content": system_message
        })
        
        # Add a brief assistant acknowledgment
        messages.append({
            "role": "assistant",
            "content": "I understand. I'll answer only cricket questions using the live data provided and maintain conversation context."
        })
        
        # Add ENTIRE conversation history (this maintains context)
        for msg in conversation_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Call LLM with Gemma model
        llm_response = completion(
            model="gemini/gemini-2.0-flash",
            api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.3,
            messages=messages
        )
        
        response_text = llm_response['choices'][0]['message']['content']
        
        # Log token usage
        usage = llm_response.get("usage", {})
        input_tokens = usage.get("prompt_tokens", "N/A")
        output_tokens = usage.get("completion_tokens", "N/A")
        logger.info(f" Input tokens: {input_tokens}, Output tokens: {output_tokens}")
        
        return response_text
        
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        return "Sorry, I encountered an error. Please try asking your cricket question again!"

# --- Streamlit App Configuration ---
st.set_page_config(
    page_title="Cricket News Chatbot",
    page_icon="🏏",
    layout="wide"
)

# --- App Title ---
st.title("🏏 Cricket News Chatbot")
st.markdown("*Your friendly assistant for all cricket-related questions with live match data!*")

# --- Initialize Session State for Conversation Memory ---
if "messages" not in st.session_state:
    greeting_message = """Hello! 👋 Welcome to the Cricket News Chatbot! 

I'm here to answer all your cricket-related questions with **live match data**. You can ask me about:

🏏 **Live match updates** 
📊 **Recent match results**
📅 **Match details** 

I'll remember our conversation, so feel free to ask follow-up questions!

What would you like to know about cricket today?"""
    
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": greeting_message
        }
    ]

# Store cricket data refresh timestamp
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = datetime.now()

# --- Sidebar for Cricket Data & Controls ---
with st.sidebar:
    st.header("📰 Live Cricket Data")
    
    # Manual refresh button
    if st.button("🔄 Refresh Cricket Data"):
        with st.spinner("Fetching latest cricket data..."):
            cricket_data = fetch_current_matches()
            st.session_state.latest_cricket_data = cricket_data
            st.session_state.last_refresh = datetime.now()
    
    # Display last refresh time
    st.caption(f"Last updated: {st.session_state.last_refresh.strftime('%H:%M:%S')}")
    
    # Display current matches if available
    if "latest_cricket_data" in st.session_state:
        with st.expander("📊 Current Matches", expanded=True):
            st.text(st.session_state.latest_cricket_data)
    
    st.markdown("---")
    
    # Conversation stats
    st.header("💬 Conversation Stats")
    message_count = len([m for m in st.session_state.messages if m["role"] == "user"])
    st.metric("Messages", message_count)
    
    st.markdown("---")
    
    # API Configuration Status
    st.header("⚙️ API Status")
    if CRICKETDATA_API_KEY:
        st.success("✅ CricketData API: Connected")
    else:
        st.error("❌ No API key configured")
        st.info("Get your API key from cricketdata.org")
    
    st.markdown("---")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History"):
        greeting_message = """Hello! 👋 Welcome back to the Cricket News Chatbot!

I'm ready to answer your cricket questions. What would you like to know?"""
        
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": greeting_message
            }
        ]
        st.rerun()

# --- Display Chat Messages with Full History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Input ---
if user_input := st.chat_input("Ask me anything about cricket..."):
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Add user message to conversation history
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    
    # Generate response with FULL conversation context
    with st.chat_message("assistant"):
        with st.spinner("Generating response..."):
            # Pass all messages except the greeting for context
            conversation_context = st.session_state.messages[1:]
            
            response = generate_cricket_response(
                user_input,
                conversation_context
            )
            st.markdown(response)
    
    # Add assistant response to conversation history
    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

