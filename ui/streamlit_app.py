import streamlit as st
from datetime import datetime
from app.services.cricket_service import fetch_current_matches
from app.services.llm_service import generate_cricket_response
from app.config import CRICKETDATA_API_KEY

def init_session_state():
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

    if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = datetime.now()

def render_sidebar():
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
            st.session_state.messages = []
            init_session_state()
            st.rerun()

def render_chat_interface():
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

def run_app():
    st.set_page_config(
        page_title="Cricket News Chatbot",
        page_icon="🏏",
        layout="wide"
    )

    st.title("🏏 Cricket News Chatbot")
    st.markdown("*Your friendly assistant for all cricket-related questions with live match data!*")

    init_session_state()
    render_sidebar()
    render_chat_interface()
