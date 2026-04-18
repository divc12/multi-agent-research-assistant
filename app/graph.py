"""
Multi-Agent Research Assistant - LangGraph Workflow

SERVICE-TO-NODE MAPPING:
========================

OpenAI LLM Nodes (GPT):
-----------------------
1. clarity_agent      → OpenAI GPT-4o-mini  (Query analysis)
2. validator_agent    → OpenAI GPT-4o-mini  (Research validation)
3. synthesis_agent    → OpenAI GPT-4o       (Response generation)

Tavily Search Node:
-------------------
4. research_agent     → Tavily Search API   (Web research)

Interrupt Node:
---------------
5. clarification_node → Human-in-the-loop   (User clarification)

Note: API integrations are currently commented out in agent files.
      Uncomment to enable live OpenAI and Tavily calls.
"""

from langgraph.graph import StateGraph, END
from langgraph.types import interrupt

from app.state import ResearchState
from app.agents.clarity_agent import clarity_agent
from app.agents.research_agent import research_agent
from app.agents.validator_agent import validator_agent
from app.agents.synthesis_agent import synthesis_agent


# --- Interrupt Node ---
def clarification_node(state):
    user_input = interrupt("Please clarify which company you are referring to:")
    return {"query": user_input}


# --- Routing Functions ---
def route_clarity(state):
    if state["clarity_status"] == "clear":
        return "research"
    return "clarification"


def route_research(state):
    if state["confidence_score"] < 6:
        return "validator"
    return "synthesis"


def route_validator(state):
    if (
        state["validation_result"] == "insufficient"
        and state["research_attempts"] < 3
    ):
        return "research"
    return "synthesis"


# --- Build Graph ---
def build_graph():
    builder = StateGraph(ResearchState)

    builder.add_node("clarity", clarity_agent)
    builder.add_node("research", research_agent)
    builder.add_node("validator", validator_agent)
    builder.add_node("synthesis", synthesis_agent)
    builder.add_node("clarification", clarification_node)

    builder.set_entry_point("clarity")

    builder.add_conditional_edges(
        "clarity",
        route_clarity,
        {
            "research": "research",
            "clarification": "clarification",
        },
    )

    builder.add_edge("clarification", "clarity")

    builder.add_conditional_edges(
        "research",
        route_research,
        {
            "validator": "validator",
            "synthesis": "synthesis",
        },
    )

    builder.add_conditional_edges(
        "validator",
        route_validator,
        {
            "research": "research",
            "synthesis": "synthesis",
        },
    )

    builder.add_edge("synthesis", END)

    return builder.compile()