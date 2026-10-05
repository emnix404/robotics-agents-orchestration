import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

from state import RobotAgentState
from agents import planner_agent, controller_agent, executor_agent

load_dotenv()

# Conditional router for self-correcting loop
def check_execution(state: RobotAgentState) -> str:
    if state.get("execution_status") == "Success":
        return "end"
    if state.get("retry_count", 0) >= 3:
        return "end"
    return "retry"

workflow = StateGraph(RobotAgentState)

workflow.add_node("planner", planner_agent)
workflow.add_node("controller", controller_agent)
workflow.add_node("executor", executor_agent)

workflow.add_edge(START, "planner")
workflow.add_edge("planner", "controller")
workflow.add_edge("controller", "executor")

# Self-Correction Loop Edge
workflow.add_conditional_edges(
    "executor",
    check_execution,
    {
        "end": END,
        "retry": "executor"
    }
)

app = workflow.compile()

if __name__ == "__main__":
    initial_input = {
        "user_prompt": "Generate python code so Puma560 moves from p0=[0.4, -0.2, 0.2] to pf=[0.5, 0.3, 0.5]",
        "retry_count": 0,
        "messages": []
    }
    
    output = app.invoke(initial_input)
    
    print("\n--- Execution Log ---")
    for msg in output.get("messages", []):
        print(msg)
        
    if output.get("execution_status") == "Success":
        print(f"\nAI Code Generation Succeeded! File saved to: {output['output_filename']}")
        print("Run simulation using: python output_simulation.py")
    else:
        print(f"\nFailed to generate runnable script after retries.\nError: {output.get('error_message')}")