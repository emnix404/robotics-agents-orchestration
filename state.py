from typing import TypedDict, Annotated, List, Optional
import operator

class RobotAgentState(TypedDict):
    user_prompt: str
    target_p0: List[float]
    target_pf: List[float]
    joint_trajectory: List[List[float]]
    joint_velocities: List[List[float]]
    joint_accelerations: List[List[float]]
    generated_code: str
    output_filename: str
    execution_status: str
    error_message: Optional[str]
    retry_count: int
    messages: Annotated[List[str], operator.add]