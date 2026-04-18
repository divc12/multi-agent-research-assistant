# =============================================================================
# VALIDATOR AGENT - Uses OpenAI LLM for research quality validation
# =============================================================================
# This agent uses OpenAI GPT model to validate if the research findings
# adequately answer the user's query with sufficient depth and relevance.
# =============================================================================

from config import STRICT_VALIDATION_MODE, STRICT_CONFIDENCE_THRESHOLD, NORMAL_CONFIDENCE_THRESHOLD

# --- UNCOMMENT TO USE OPENAI ---
# from openai import OpenAI
# import os
# import json

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# --- END OPENAI SETUP ---

def validator_agent(state: dict) -> dict:
    """
    Validates if research findings adequately answer the user's query.
    Uses OpenAI LLM for intelligent validation (when uncommented).
    
    Cross-checks findings against the original query to ensure:
    - Relevant information is present
    - Key fields matching query intent are populated
    - Confidence score meets minimum threshold
    
    Args:
        state: Current research state containing query, findings, and confidence
        
    Returns:
        Dictionary with validation_result and updated research_attempts
    """
    
    # --- TRY OPENAI LLM VALIDATION FIRST, FALLBACK TO RULES ---
    # attempts = state.get("research_attempts", 0) + 1
    
    # try:
    #     query = state.get("query", "")
    #     findings = state.get("research_findings", {})
    #     confidence = state.get("confidence_score", 0)
        
    #     if "error" in findings:
    #         return {
    #             "validation_result": "insufficient",
    #             "research_attempts": attempts
    #         }
        
    #     # Use LLM to validate research quality
    #     prompt = f"""
    #     Validate if the research findings adequately answer the user's query.
        
    #     User Query: {query}
        
    #     Research Findings:
    #     {json.dumps(findings, indent=2)}
        
    #     Confidence Score: {confidence}/10
        
    #     Determine if the findings are:
    #     - "sufficient": Provides relevant, comprehensive answer to the query
    #     - "insufficient": Missing key information or not relevant enough
        
    #     Respond with ONLY one word: "sufficient" or "insufficient"
    #     """
        
    #     response = client.chat.completions.create(
    #         model="gpt-4o-mini",
    #         messages=[
    #             {"role": "system", "content": "You are a research quality validator. Respond with only 'sufficient' or 'insufficient'."},
    #             {"role": "user", "content": prompt}
    #         ],
    #         temperature=0.3,
    #         max_tokens=10
    #     )
        
    #     validation_result = response.choices[0].message.content.strip().lower()
    #     return {
    #         "validation_result": validation_result,
    #         "research_attempts": attempts
    #     }
    # except Exception as e:
    #     # Fallback to rule-based validation if OpenAI fails
    #     print(f"[INFO] OpenAI unavailable, using rule-based validation: {e}")
    # --- END OPENAI LLM VALIDATION ---
    
    # RULE-BASED FALLBACK IMPLEMENTATION
    attempts = state.get("research_attempts", 0) + 1
    query = state.get("query", "").lower()
    findings = state.get("research_findings", {})
    confidence = state.get("confidence_score", 0)
    
    # If error in findings, mark as insufficient
    if "error" in findings:
        return {
            "validation_result": "insufficient",
            "research_attempts": attempts
        }
    
    # Base confidence check - use dynamic threshold based on mode
    threshold = STRICT_CONFIDENCE_THRESHOLD if STRICT_VALIDATION_MODE else NORMAL_CONFIDENCE_THRESHOLD
    if confidence < threshold:
        print(f"[VALIDATOR] Confidence {confidence} < {threshold} ({'STRICT' if STRICT_VALIDATION_MODE else 'NORMAL'} mode)")
        return {
            "validation_result": "insufficient",
            "research_attempts": attempts
        }
    
    # Cross-check findings against query intent
    # Identify what the user is asking about
    is_asking_stock = any(word in query for word in ["stock", "price", "trading", "share"])
    is_asking_news = any(word in query for word in ["news", "recent", "latest", "happening"])
    is_asking_development = any(word in query for word in ["development", "future", "working", "building"])
    
    # Check if relevant fields are present and non-empty
    missing_info = []
    
    if is_asking_stock and not findings.get("stock_info"):
        missing_info.append("stock_info")
    
    if is_asking_news and not findings.get("recent_news"):
        missing_info.append("recent_news")
    
    if is_asking_development and not findings.get("key_developments"):
        missing_info.append("key_developments")
    
    # For general queries, ensure at least 2 of the 3 key fields are present
    if not (is_asking_stock or is_asking_news or is_asking_development):
        available_fields = sum([
            bool(findings.get("recent_news")),
            bool(findings.get("stock_info")),
            bool(findings.get("key_developments"))
        ])
        if available_fields < 2:
            missing_info.append("general_info")
    
    # Mark as insufficient if key information is missing
    if missing_info:
        return {
            "validation_result": "insufficient",
            "research_attempts": attempts
        }
    
    # All checks passed
    return {
        "validation_result": "sufficient",
        "research_attempts": attempts
    }