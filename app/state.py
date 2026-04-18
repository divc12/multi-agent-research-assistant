from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class ResearchState(TypedDict):
    messages: Annotated[list, add_messages] # Full conversation history
    query: str # Current user query
    clarity_status: str # "clear" | "needs_clarification"
    research_findings: dict # Research findings for the current query
    confidence_score: float # (0-10) | Confidence score of the research findings
    validation_result: str # "sufficient" | "insufficient" Result of the validation process
    research_attempts: int # Tracks retry count, Number of research attempts made
    final_response: str # Final response to be sent to the user