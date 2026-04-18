# =============================================================================
# RESEARCH AGENT - Uses Tavily Search API for web research
# =============================================================================
# This agent uses Tavily Search API to conduct real-time web searches and
# gather information about companies, stocks, news, and developments.
# =============================================================================

from data.mock_data import MOCK_RESEARCH
from config import (
    STRICT_VALIDATION_MODE,
    TAVILY_SEARCH_DOMAINS,
    MIN_ANSWER_LENGTH,
    COMPANY_KEYWORDS,
    STRICT_CONFIDENCE_THRESHOLD,
    NORMAL_CONFIDENCE_THRESHOLD
)

# --- UNCOMMENT TO USE TAVILY SEARCH ---
from tavily import TavilyClient
import os

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
# --- END TAVILY SETUP ---

def research_agent(state: dict) -> dict:
    """
    Retrieves company information using Tavily Search API (when uncommented).
    Falls back to mock data for demonstration.
    
    Args:
        state: Current research state containing query and message history
        
    Returns:
        Dictionary with research_findings and confidence_score
    """
    
    # --- TRY TAVILY SEARCH FIRST, FALLBACK TO MOCK DATA ---
    try:
        query = state["query"]
        messages = state.get("messages", [])
        
        # Build enhanced search query from context - handle both dict and tuple formats
        conversation_parts = []
        for msg in messages[-3:]:
            if isinstance(msg, dict):
                if msg.get('role') == 'user':
                    conversation_parts.append(msg.get('content', ''))
            elif isinstance(msg, tuple):
                role, content = msg
                if role == 'user':
                    conversation_parts.append(content)
            else:
                # LangGraph Message object
                if getattr(msg, 'type', '') == 'human':
                    conversation_parts.append(getattr(msg, 'content', ''))
        
        conversation_context = "\n".join(conversation_parts)
        
        # Perform Tavily search
        search_query = f"{query} {conversation_context}".strip()
        
        # Tavily search with company-focused domain restrictions
        search_response = tavily_client.search(
            query=search_query,
            search_depth="advanced",  # "basic" or "advanced"
            max_results=5,
            include_answer=True,  # Get AI-generated answer
            include_raw_content=False,
            include_domains=TAVILY_SEARCH_DOMAINS,  # Focus on business news
            exclude_domains=[]   # Optional: exclude specific domains
        )
        
        # Extract findings from Tavily response
        findings = {
            "answer": search_response.get("answer", ""),
            "sources": [
                {
                    "title": result["title"],
                    "url": result["url"],
                    "content": result["content"],
                    "score": result.get("score", 0)
                }
                for result in search_response.get("results", [])
            ],
            "query": search_query
        }
        
        # Calculate confidence based on result quality
        num_results = len(findings["sources"])
        avg_score = sum(s["score"] for s in findings["sources"]) / max(num_results, 1)
        confidence = min(10, (num_results * avg_score * 10))
        
        # Check if Tavily answer is empty or too short (poor quality)
        answer = findings.get("answer", "").strip()
        if not answer or len(answer) < MIN_ANSWER_LENGTH:
            # Treat as low confidence to trigger validation retry
            confidence = min(confidence, 3)
        
        # Check if results are actually about a company (not random topics)
        answer_lower = answer.lower()
        has_company_keywords = any(keyword in answer_lower for keyword in COMPANY_KEYWORDS)
        
        if not has_company_keywords:
            # Results don't seem company-related, reduce confidence
            print(f"[INFO] Results may not be company-related for: {query}")
            confidence = min(confidence, 3)
        
        # STRICT VALIDATION MODE (for Test Case 5.1 demonstration)
        if STRICT_VALIDATION_MODE:
            # In strict mode, require higher confidence threshold
            if confidence < STRICT_CONFIDENCE_THRESHOLD:
                print(f"[STRICT MODE] Confidence {confidence} < {STRICT_CONFIDENCE_THRESHOLD}, will trigger validation retry")
                confidence = 3  # Force low confidence to trigger retry loop
        
        return {
            "research_findings": findings,
            "confidence_score": confidence
        }
    except Exception as e:
        # Fallback to mock data if Tavily fails
        print(f"[INFO] Tavily unavailable, using mock data: {e}")
    # --- END TAVILY SEARCH INTEGRATION ---
    
    # MOCK DATA FALLBACK IMPLEMENTATION
    query = state["query"].lower()
    messages = state.get("messages", [])

    # First, try to find company in current query
    target_company = None
    for company, data in MOCK_RESEARCH.items():
        if company.lower() in query:
            target_company = company
            break
    
    # If company found, return it immediately
    if target_company:
        data = MOCK_RESEARCH[target_company]
        return {
            "research_findings": {**data, "company": target_company},
            "confidence_score": data["confidence"]
        }
    
    # Company not found in query - check if this is a follow-up with implicit references
    # Only check history for queries with pronouns like "their", "that", etc.
    # Use word boundaries to avoid false matches (e.g., "it" in "with")
    query_words = query.split()
    implicit_references = ["their", "its", "that", "this", "them", "it"]
    # Also check for multi-word phrases
    has_implicit_reference = (
        any(ref in query_words for ref in implicit_references) or
        "the company" in query
    )
    
    # If query has implicit references, check message history for company context
    if has_implicit_reference and messages:
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
            for company in MOCK_RESEARCH.keys():
                if company.lower() in content_lower:
                    target_company = company
                    break
            if target_company:
                break
    
    # Return data for the identified company from history
    if target_company:
        data = MOCK_RESEARCH[target_company]
        return {
            "research_findings": {**data, "company": target_company},
            "confidence_score": data["confidence"]
        }

    # No company found - return error
    return {
        "research_findings": {"error": "Data not available"},
        "confidence_score": 3
    }