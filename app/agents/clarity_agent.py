# =============================================================================
# CLARITY AGENT - Uses OpenAI LLM for query analysis
# =============================================================================
# This agent uses OpenAI GPT model to analyze user queries and determine
# if they are specific enough to proceed with research or need clarification.
# =============================================================================

# --- UNCOMMENT TO USE OPENAI ---
# from openai import OpenAI
# import os

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# --- END OPENAI SETUP ---

def clarity_agent(state: dict) -> dict:
    """
    Determines if the user's query is specific enough to proceed with research.
    Uses OpenAI LLM to analyze query clarity (when uncommented).
    
    Args:
        state: Current research state containing query and message history
        
    Returns:
        Dictionary with clarity_status: "clear" or "needs_clarification"
    """
    
    # --- TRY OPENAI LLM FIRST, FALLBACK TO RULES ---
    # try:
    #     query = state["query"]
    #     messages = state.get("messages", [])
        
    #     # Build conversation context for LLM - handle both dict and tuple formats
    #     conversation_parts = []
    #     for msg in messages[-5:]:  # Last 5 messages
    #         if isinstance(msg, dict):
    #             conversation_parts.append(f"{msg['role']}: {msg['content']}")
    #         elif isinstance(msg, tuple):
    #             conversation_parts.append(f"{msg[0]}: {msg[1]}")
    #         else:
    #             # LangGraph Message object
    #             role = getattr(msg, 'type', 'unknown')
    #             content = getattr(msg, 'content', str(msg))
    #             conversation_parts.append(f"{role}: {content}")
        
    #     conversation_history = "\n".join(conversation_parts)
        
    #     prompt = f"""
    #     Analyze if the following query is specific enough to research.
        
    #     Conversation History:
    #     {conversation_history}
        
    #     Current Query: {query}
        
    #     Determine if the query is:
    #     - "clear": Has enough specifics (company name, clear topic)
    #     - "needs_clarification": Too vague or ambiguous
        
    #     Respond with ONLY one word: "clear" or "needs_clarification"
    #     """
        
    #     response = client.chat.completions.create(
    #         model="gpt-4o-mini",
    #         messages=[
    #             {"role": "system", "content": "You are a query analysis assistant. Respond with only 'clear' or 'needs_clarification'."},
    #             {"role": "user", "content": prompt}
    #         ],
    #         temperature=0.3,
    #         max_tokens=10
    #     )
        
    #     clarity_status = response.choices[0].message.content.strip().lower()
    #     return {"clarity_status": clarity_status}
    # except Exception as e:
    #     # Fallback to rule-based implementation if OpenAI fails
    #     print(f"[INFO] OpenAI unavailable, using rule-based clarity check: {e}")
    # --- END OPENAI LLM INTEGRATION ---
    
    # RULE-BASED FALLBACK IMPLEMENTATION
    query = state["query"].lower()
    messages = state.get("messages", [])

    # Known companies (mock data) + common companies for validation testing
    companies = ["apple", "tesla", "microsoft", "google", "amazon", "meta", "netflix", "facebook"]
    
    # List of vague phrases that require clarification ONLY if no context keywords present
    vague_phrases = ["tell me more", "more info", "tell me", "continue", "go on"]
    
    # Context keywords that indicate the query has specific intent
    context_keywords = [
        "stock", "price", "trading", "share",  # Stock-related
        "news", "recent", "latest", "happening",  # News-related
        "development", "future", "working", "building",  # Development-related
        "their", "its", "that",  # Pronouns referring to previous context
    ]

    # Check current query for company names
    has_company_in_query = any(company in query for company in companies)
    
    # Check if query has contextual keywords
    has_context_keywords = any(keyword in query for keyword in context_keywords)
    
    # Check if query is truly vague (no company, no context keywords, and contains vague phrases or too short)
    is_truly_vague = (
        not has_company_in_query and 
        not has_context_keywords and
        (any(phrase in query for phrase in vague_phrases) or len(query.strip()) <= 5)
    )
    
    # If query is truly vague, require clarification
    if is_truly_vague:
        return {"clarity_status": "needs_clarification"}
    
    # Check if previous messages mentioned a company (for follow-up questions)
    mentioned_company = None
    if not has_company_in_query and messages:
        # Look through message history for previously mentioned companies
        for msg in reversed(messages):
            # Handle dict, tuple, and Message object formats
            if isinstance(msg, dict):
                content = msg.get('content', '')
            elif isinstance(msg, tuple):
                role, content = msg
            else:
                # Message object from LangGraph
                content = getattr(msg, 'content', str(msg))
            
            content_lower = content.lower() if content else ""
            for company in companies:
                if company in content_lower:
                    mentioned_company = company
                    break
            if mentioned_company:
                break
    
    # Clear if: has company in query OR has context from history (but not vague)
    if has_company_in_query or mentioned_company:
        return {"clarity_status": "clear"}
    
    return {"clarity_status": "needs_clarification"}