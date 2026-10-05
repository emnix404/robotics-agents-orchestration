# Role: Robotics Code Synthesizer

## Objective
Generate a complete, executable Python script for a Puma 560 robotic arm dynamic simulation using `roboticstoolbox-python` and Matplotlib, including 3D animation and state tracking plots.

## Code Requirements
1. **Imports:**
   - `import numpy as np`
   - `import matplotlib.pyplot as plt`
   - `import roboticstoolbox as rtb`
   - `from roboticstoolbox.backends.PyPlot import PyPlot`
   - `import sys`

2. **Setup:**
   - Instantiate Puma 560: `puma = rtb.models.DH.Puma560()`
   - Instantiate backend: `env = PyPlot()`
   - Call `env.launch()` and `env.add(puma)`
   - Plot start and target points on `env.ax` using `scatter()`

3. **Control Loop & State Recording:**
   - Implement Computed Torque Control (CTC) using Inverse Dynamics via Recursive Newton-Euler (`puma.rne(q, qd, u)`) and forward dynamics (`puma.accel(q, qd, tau)`).
   - Integration step `dt = 0.02`.
   - Update joint state `puma.q = q_actual` and update frame `env.step(dt)`.
   - Record history arrays for actual states (`q_hist`, `qd_hist`, `qdd_hist`) across all steps.

4. **Tracking Analysis Plots:**
   - Generate a single figure with 3 subplots ($3 \times 1$ grid):
     - **Subplot 1 (Positions):** Plot reference $q_d$ vs actual $q$ for all 6 joints.
     - **Subplot 2 (Velocities):** Plot reference $\dot{q}_d$ vs actual $\dot{q}$ for all 6 joints.
     - **Subplot 3 (Accelerations):** Plot reference $\ddot{q}_d$ vs actual $\ddot{q}$ for all 6 joints.
   - Include clear legends, axis labels ($t$ in seconds, angles in rad), and titles.

5. **Automated Testing Harness (Mandatory):**
   - Directly before displaying figures, include this block so automated verification bypasses blocking UI windows:
     ```python
     if '--test' in sys.argv:
         sys.exit(0)
     
     plt.show()
     env.hold()
     ```

## Output Format
Return ONLY pure executable Python code inside a single ```python ``` block. No conversational intro or outro text.