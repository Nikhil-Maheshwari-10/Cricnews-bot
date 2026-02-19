from litellm import completion
from app.config import GEMINI_API_KEY, CRICKET_SYSTEM_PROMPT, LLM_MODEL
from app.services.cricket_service import get_cricket_context
from app.logger import logger

def generate_cricket_response(user_message, conversation_history):
    """
    Generate response using Gemini model with cricket API data and full conversation history.
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
        
        # Call LLM with dynamic model selection
        llm_response = completion(
            model=LLM_MODEL,
            api_key=GEMINI_API_KEY,
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
