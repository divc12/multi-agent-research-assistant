# =============================================================================
# SYNTHESIS AGENT - Uses OpenAI LLM for response generation
# =============================================================================
# This agent uses OpenAI GPT model to synthesize research findings into
# natural, conversational responses tailored to the user's specific question.
# =============================================================================

# --- UNCOMMENT TO USE OPENAI ---
# from openai import OpenAI
# import os
# import json

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# --- END OPENAI SETUP ---

def synthesis_agent(state: dict) -> dict:
    """
    Synthesizes research findings into a user-facing response.
    Uses OpenAI LLM for natural language generation (when uncommented).
    
    Args:
        state: Current research state with findings and query history
        
    Returns:
        Dictionary with final_response and updated messages
    """
    
    # --- TRY OPENAI LLM SYNTHESIS FIRST, FALLBACK TO TEMPLATES ---
    # try:
    #     findings = state.get("research_findings", {})
    #     query = state.get("query", "")
    #     messages = state.get("messages", [])
        
    #     if "error" in findings:
    #         response = "I apologize, but I encountered an error while researching your query. Please try rephrasing your question."
    #     else:
    #         # Build conversation context - handle both dict and tuple formats
    #         conversation_parts = []
    #         for msg in messages[-5:]:
    #             if isinstance(msg, dict):
    #                 conversation_parts.append(f"{msg['role']}: {msg['content']}")
    #             elif isinstance(msg, tuple):
    #                 conversation_parts.append(f"{msg[0]}: {msg[1]}")
    #             else:
    #                 # LangGraph Message object
    #                 role = getattr(msg, 'type', 'unknown')
    #                 content = getattr(msg, 'content', str(msg))
    #                 conversation_parts.append(f"{role}: {content}")
            
    #         conversation_history = "\n".join(conversation_parts)
            
    #         prompt = f"""
    #         Synthesize the research findings into a natural, conversational response.
            
    #         Conversation History:
    #         {conversation_history}
            
    #         Current Query: {query}
            
    #         Research Findings:
    #         {json.dumps(findings, indent=2)}
            
    #         Create a helpful, concise response that:
    #         - Directly answers the user's question
    #         - Uses natural, conversational language
    #         - Cites specific information from the findings
    #         - Is appropriate as a follow-up in the conversation context
            
    #         Response:
    #         """
            
    #         llm_response = client.chat.completions.create(
    #             model="gpt-4o",  # Use GPT-4 for better synthesis
    #             messages=[
    #                 {"role": "system", "content": "You are a helpful research assistant that synthesizes information into clear, accurate responses."},
    #                 {"role": "user", "content": prompt}
    #             ],
    #             temperature=0.7,
    #             max_tokens=500
    #         )
            
    #         response = llm_response.choices[0].message.content.strip()
        
    #     return {
    #         "final_response": response,
    #         "messages": [{"role": "assistant", "content": response}]
    #     }
    # except Exception as e:
    #     # Fallback to template-based synthesis if OpenAI fails
    #     print(f"[INFO] OpenAI unavailable, using template-based synthesis: {e}")
    # --- END OPENAI LLM SYNTHESIS ---
    
    # TEMPLATE-BASED FALLBACK IMPLEMENTATION
    findings = state.get("research_findings", {})
    query = state.get("query", "").lower()
    messages = state.get("messages", [])
    
    # Check if this is a follow-up question (history exists)
    user_messages = []
    for m in messages:
        if isinstance(m, dict) and m.get('role') == 'user':
            user_messages.append(m)
        elif isinstance(m, tuple) and m[0] == "user":
            user_messages.append(m)
        elif hasattr(m, 'type') and getattr(m, 'type') == 'human':
            user_messages.append(m)
    is_followup = len(user_messages) > 1
    
    # Handle error case
    if "error" in findings:
        response = f"I don't have data available for that company. Please try asking about Apple, Tesla, or Microsoft."
    else:
        # Detect data structure: Tavily (has 'answer' & 'sources') vs Mock (has 'company' & specific fields)
        is_tavily_data = "answer" in findings and "sources" in findings
        
        if is_tavily_data:
            # TAVILY DATA STRUCTURE - use AI-generated answer and sources
            answer = findings.get("answer", "").strip()
            sources = findings.get("sources", [])
            
            # Check if answer is empty or too short (poor quality)
            if not answer or len(answer) < 10:
                response = f"I don't have sufficient data available for that query. Please try asking about Apple, Tesla, or Microsoft."
            else:
                # Build response with answer and top sources
                response = answer
                if sources:
                    response += "\n\nSources:"
                    for i, source in enumerate(sources[:3], 1):  # Top 3 sources
                        response += f"\n{i}. {source['title']} - {source['url']}"
        else:
            # MOCK DATA STRUCTURE - use template-based response
            company = findings.get("company", "the company")
            
            # Build contextual response based on specific question type
            if any(word in query for word in ["stock", "price", "trading"]):
                response = f"Regarding {company}: {findings.get('stock_info', 'N/A')}"
            elif any(word in query for word in ["news", "recent", "latest"]):
                response = f"{company} news: {findings.get('recent_news', 'N/A')}"
            elif any(word in query for word in ["development", "future", "working on"]):
                response = f"{company} developments: {findings.get('key_developments', 'N/A')}"
            else:
                # Full summary
                response = f"""
{company} Summary:
- News: {findings.get('recent_news', 'N/A')}
- Stock: {findings.get('stock_info', 'N/A')}
- Developments: {findings.get('key_developments', 'N/A')}
""".strip()

    return {
        "final_response": response,
        "messages": [{"role": "assistant", "content": response}]
    }