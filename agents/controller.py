from state import RobotAgentState
from tools.robotics_tools import validate_joint_limits

def controller_agent(state: RobotAgentState) -> dict:
    # Abort step if an error occurred in earlier nodes
    if state.get("error_message"):
        return {"messages": ["Controller: Skipped validation due to previous errors."]}
        
    q_path = state.get("joint_trajectory", [])
    val = validate_joint_limits.invoke({"q_path": q_path})
    
    if not val["valid"]:
        return {
            "error_message": val["reason"], 
            "messages": [f"Controller: Trajectory rejected — {val['reason']}"]
        }
        
    return {"messages": ["Controller: Passed joint limit and safety checks."]}