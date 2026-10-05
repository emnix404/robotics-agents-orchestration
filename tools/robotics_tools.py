import numpy as np
import roboticstoolbox as rtb
from spatialmath import SE3
from langchain_core.tools import tool

@tool
def calculate_puma560_trajectory(p0: list, pf: list, steps: int = 100) -> dict:
    """Computes dynamic joint trajectory references (q, qd, qdd) for Puma 560."""
    try:
        puma = rtb.models.DH.Puma560()
        T0 = SE3(p0[0], p0[1], p0[2])
        Tf = SE3(pf[0], pf[1], pf[2])
        
        ik_start = puma.ikine_LM(T0)
        ik_end = puma.ikine_LM(Tf)
        
        if not (ik_start.success and ik_end.success):
            return {"status": "error", "message": "IK failed to converge for start or end pose."}
            
        traj = rtb.jtraj(ik_start.q, ik_end.q, steps)
        
        return {
            "status": "success",
            "q": traj.q.tolist(),
            "qd": traj.qd.tolist(),
            "qdd": traj.qdd.tolist()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@tool
def validate_joint_limits(q_path: list) -> dict:
    """Checks if joint trajectory exceeds Puma 560 mechanical limits."""
    puma = rtb.models.DH.Puma560()
    limits = puma.qlim
    q_arr = np.array(q_path)
    
    for j in range(6):
        if np.any(q_arr[:, j] < limits[0, j]) or np.any(q_arr[:, j] > limits[1, j]):
            return {"valid": False, "reason": f"Joint {j+1} limit exceeded."}
            
    return {"valid": True, "reason": "All trajectory steps within safety bounds."}