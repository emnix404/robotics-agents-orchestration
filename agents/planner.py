from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from state import RobotAgentState
from tools.robotics_tools import calculate_puma560_trajectory

class ExtractCoordinates(BaseModel):
    p0: list[float] = Field(description="Starting 3D Cartesian coordinates [x, y, z]")
    pf: list[float] = Field(description="Target 3D Cartesian coordinates [x, y, z]")

def planner_agent(state: RobotAgentState) -> dict:
    llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", temperature=0)
    structured_llm = llm.with_structured_output(ExtractCoordinates)
    
    prompt = f"Extract start point (p0) and target point (pf) coordinates from: {state['user_prompt']}"
    extracted = structured_llm.invoke(prompt)
    
    res = calculate_puma560_trajectory.invoke({"p0": extracted.p0, "pf": extracted.pf})
    
    if res["status"] == "error":
        return {
            "error_message": res["message"], 
            "messages": [f"Planner: Failed path generation — {res['message']}"]
        }
        
    return {
        "target_p0": extracted.p0,
        "target_pf": extracted.pf,
        "joint_trajectory": res["q"],
        "joint_velocities": res["qd"],
        "joint_accelerations": res["qdd"],
        "messages": [f"Planner: Generated trajectory from p0={extracted.p0} to pf={extracted.pf}."]
    }