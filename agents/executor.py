import os
import re
import subprocess
from pathlib import Path
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from state import RobotAgentState

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "executor_prompt.md"
SYSTEM_INSTRUCTION = PROMPT_PATH.read_text(encoding="utf-8")

def executor_agent(state: RobotAgentState) -> dict:
    llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", temperature=0.1)
    
    # Passing SystemMessage directly prevents LangChain from parsing static {q} in the prompt
    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessage(content=SYSTEM_INSTRUCTION),
        ("user", """Write the simulation script for these parameters:
- Target p0: {p0}
- Target pf: {pf}
- Reference trajectory q_d: {q_ref}
- Reference velocity qd_d: {qd_ref}
- Reference acceleration qdd_d: {qdd_ref}

Previous Attempt Error Logs (if any):
{error_logs}
""")
    ])
    
    current_retries = state.get("retry_count", 0)
    error_logs = state.get("error_message", "None")
    
    # Query Gemini using the correct state dictionary keys
    chain = prompt_template | llm
    response = chain.invoke({
        "p0": state["target_p0"],
        "pf": state["target_pf"],
        "q_ref": state["joint_trajectory"],
        "qd_ref": state["joint_velocities"],
        "qdd_ref": state["joint_accelerations"],
        "error_logs": error_logs
    })
    
    # Convert response content to a single string cleanly
    if isinstance(response.content, list):
        raw_code = "".join(
            item if isinstance(item, str) else item.get("text", "") 
            for item in response.content
        )
    else:
        raw_code = str(response.content)
    
    # Extract Python code block
    match = re.search(r"```python\s*(.*?)\s*```", raw_code, re.DOTALL)
    code = match.group(1) if match else raw_code.strip()

    # Test-execute generated code in an isolated subprocess
    temp_filename = "temp_test_sim.py"
    final_filename = "output_simulation.py"
    
    with open(temp_filename, "w", encoding="utf-8") as f:
        f.write(code)
        
    try:
        result = subprocess.run(
            ["python", temp_filename, "--test"], 
            capture_output=True, 
            text=True, 
            timeout=15
        )
        return_code = result.returncode
        stderr = result.stderr
    except subprocess.TimeoutExpired:
        return_code = -1
        stderr = "Execution timed out during testing."

    # Evaluate execution status
    if return_code == 0:
        os.replace(temp_filename, final_filename)
        return {
            "generated_code": code,
            "output_filename": final_filename,
            "execution_status": "Success",
            "error_message": None,
            "retry_count": current_retries + 1,
            "messages": [f"Executor: Successfully synthesized and verified '{final_filename}'."]
        }
    else:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        return {
            "generated_code": code,
            "execution_status": "Failed",
            "error_message": stderr,
            "retry_count": current_retries + 1,
            "messages": [f"Executor: Attempt {current_retries + 1} failed execution test. Retrying..."]
        }