# QUEEN-VISION — N-Queens Visualizer

A hackathon-ready, algorithm-centric visualization of the **N-Queens problem using Backtracking**.

## Features

- Interactive chessboard visualization
- N = 4 to 12
- First-solution and all-solutions modes
- Step-by-step backtracking trace
- Conflict highlighting
- Current candidate / last action highlighting
- Solution counter and solution gallery
- Execution statistics:
  - solutions
  - placements
  - conflicts
  - backtracks
  - search nodes
  - maximum recursion depth
  - execution time
- Algorithm event log
- Trace timeline and depth chart
- Download statistics as JSON
- Download trace as CSV
- Download current solution as CSV
- Responsive premium Streamlit interface
- Algorithm explanation and complexity section

## Run

### Windows
```bash
run.bat
```

### macOS / Linux
```bash
chmod +x run.sh
./run.sh
```

### Manual
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Project Structure

```text
QUEEN_VISION_N_Queens_Hackathon/
├── app.py
├── requirements.txt
├── README.md
├── LICENSE
├── run.bat
├── run.sh
├── src/
│   ├── __init__.py
│   ├── solver.py
│   └── exporters.py
└── assets/
    └── custom.css
```

## Algorithm

For each row, the solver tries every column.

A placement is safe when:
- no queen is already in the same column;
- no queen is on the same `row - column` diagonal;
- no queen is on the same `row + column` diagonal.

If a candidate is safe, the queen is placed and the solver recursively moves to the next row. If the branch cannot produce a valid completion, the placement is undone and the solver backtracks.

Worst-case time complexity is commonly expressed as **O(N!)**, with **O(N)** auxiliary recursion/state space for the core solver, excluding stored solutions and visualization trace data.

## Hackathon Demo Flow

1. Open the app.
2. Choose N = 4 or N = 8.
3. Select `All solutions` for a complete statistics demo.
4. Click `Generate / Solve`.
5. Use `Step` to move through decisions.
6. Use the solution selector to inspect solutions.
7. Open `Metrics` and `Algorithm` tabs.
8. Download the statistics/trace for evidence.

## Source alignment

The project implements the uploaded hackathon statement for **Problem 10: N-Queens Visualizer**, whose core algorithm is Backtracking and whose suggested technologies include Python, Streamlit and JavaScript.
