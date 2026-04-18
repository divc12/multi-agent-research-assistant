"""
Multi-Agent Research Assistant - Main Entry Point

To enable OpenAI and Tavily integrations:
1. Copy .env.example to .env
2. Add your API keys to .env
3. Uncomment integration code in agent files
4. Uncomment the dotenv line below
"""

# --- UNCOMMENT TO LOAD API KEYS FROM .ENV FILE ---
from dotenv import load_dotenv
load_dotenv()
# --- END ENV SETUP ---

from app.graph import build_graph

graph = build_graph()

def run_chat():
    message_history = []

    print("Multi-Agent Research Assistant (type 'exit' to quit)\n")

    while True:
        user_input = input("User: ")

        if user_input.lower() == "exit":
            break

        # RESET state for each new query to avoid contamination
        state = {
            "messages": message_history.copy(),
            "query": user_input,
            "research_attempts": 0,
            "clarity_status": "",
            "research_findings": {},
            "confidence_score": 0,
            "validation_result": "",
            "final_response": ""
        }
        
        state["messages"].append({"role": "user", "content": user_input})  
        
        # RUN GRAPH (can return interrupt OR final result)
        result = graph.invoke(state)

        # =========================
        # CASE 1: INTERRUPT FLOW
        # =========================
        had_interrupt = False
        user_clarification = None
        if "__interrupt__" in result:
            had_interrupt = True
            question = result["__interrupt__"][0].value
            print("Assistant:", question)

            user_clarification = input("User: ")
            
            # Create fresh state with clarification
            state = {
                "messages": state["messages"] + [{"role": "user", "content": user_clarification}],
                "query": user_clarification,
                "research_attempts": 0,
                "clarity_status": "",
                "research_findings": {},
                "confidence_score": 0,
                "validation_result": "",
                "final_response": ""
            }

            # Resume/restart graph with clarified query
            result = graph.invoke(state)

        # =========================
        # CASE 2: FINAL RESPONSE
        # =========================
        if "final_response" in result:
            print("Assistant:", result["final_response"])
            # Save assistant response to persistent history
            # If interrupt occurred, save the clarified input; otherwise save original input
            query_to_save = user_clarification if had_interrupt else user_input
            message_history.append({"role": "user", "content": query_to_save})
            message_history.append({"role": "assistant", "content": result["final_response"]})

        # DO NOT break → allows multi-turn conversation
        print("\n--- ready for next question ---\n")

if __name__ == "__main__":
    run_chat()