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
from datetime import datetime
import os

graph = build_graph()

def save_conversation_log(message_history, log_dir="conversation_logs"):
    """
    Saves conversation history to a timestamped text file.
    
    Args:
        message_history: List of message dictionaries with 'role' and 'content'
        log_dir: Directory to store conversation logs
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Generate timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"conversation_{timestamp}.txt"
    filepath = os.path.join(log_dir, filename)
    
    # Write conversation to file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("Multi-Agent Research Assistant - Conversation Log\n")
        f.write(f"Session Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        for i, msg in enumerate(message_history, 1):
            role = msg.get("role", "unknown").capitalize()
            content = msg.get("content", "")
            f.write(f"[{i}] {role}:\n{content}\n\n")
            f.write("-" * 80 + "\n\n")
        
        f.write("=" * 80 + "\n")
        f.write(f"End of conversation - Total messages: {len(message_history)}\n")
        f.write("=" * 80 + "\n")
    
    return filepath

def run_chat():
    message_history = []

    print("Multi-Agent Research Assistant (type 'exit' to quit)")
    print("💾 Conversation will be automatically saved to conversation_logs/\n")

    while True:
        user_input = input("User: ")

        if user_input.lower() == "exit":
            # Save conversation log before exiting
            if message_history:
                log_file = save_conversation_log(message_history)
                print(f"\n✅ Conversation saved to: {log_file}")
            else:
                print("\n💬 No conversation to save (no messages exchanged)")
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