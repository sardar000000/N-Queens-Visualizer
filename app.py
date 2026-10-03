from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from src.solver import solve_n_queens
from src.exporters import stats_json, trace_csv, solution_csv

BASE = Path(__file__).parent
CSS = (BASE / "assets" / "custom.css").read_text(encoding="utf-8")

st.set_page_config(
    page_title="QUEEN-VISION | N-Queens Visualizer",
    page_icon="♛",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(CSS, unsafe_allow_html=True)

# ---------- Session state ----------
defaults = {
    "solved": False,
    "stats": None,
    "events": [],
    "solutions": [],
    "cursor": 0,
    "solution_index": 0,
    "n": 8,
    "mode": "All solutions",
    "trace_limit": 120_000,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---------- Helpers ----------
def metric_card(label, value):
    return f"""
    <div class="metric-card">
      <div class="metric-label">{label}</div>
      <div class="metric-value">{value}</div>
    </div>
    """

def event_board(event, n, show_conflicts=True):
    board = event["board"]
    candidate = (event["row"], event["col"])
    conflict_cells = set()

    if show_conflicts and event["action"] == "CONFLICT":
        conflict_cells.add(candidate)

    cells = []
    for r in range(n):
        for c in range(n):
            klass = "light" if (r + c) % 2 == 0 else "dark"
            if (r, c) in conflict_cells:
                klass += " conflict"
            if (r, c) == candidate and event["action"] in ("PLACE", "BACKTRACK"):
                klass += " last"
            if board[r] == c:
                queen = "♛"
                cells.append(
                    f'<div class="sq {klass}"><span class="queen">{queen}</span>'
                    f'<span class="coord">{r+1},{c+1}</span></div>'
                )
            else:
                cells.append(
                    f'<div class="sq {klass}"><span class="coord">{r+1},{c+1}</span></div>'
                )
    return (
        f'<div class="board-wrap"><div class="chessboard" style="--n:{n}">'
        + "".join(cells)
        + "</div></div>"
    )

def solution_board(solution, n):
    cells = []
    for r in range(n):
        for c in range(n):
            klass = "light" if (r+c)%2 == 0 else "dark"
            queen = "♛" if solution[r] == c else ""
            cells.append(
                f'<div class="sq {klass}"><span class="queen">{queen}</span>'
                f'<span class="coord">{r+1},{c+1}</span></div>'
            )
    return f'<div class="board-wrap"><div class="chessboard" style="--n:{n}">' + "".join(cells) + "</div></div>"

# ---------- Header ----------
st.markdown("""
<div class="qv-hero">
  <div class="qv-title">♛ QUEEN-VISION</div>
  <div class="qv-subtitle">N-Queens Backtracking Visualizer • Algorithm-Centric Hackathon Prototype</div>
  <span class="qv-pill">BACKTRACKING • CONFLICTS • SOLUTIONS • EXECUTION STATISTICS</span>
</div>
""", unsafe_allow_html=True)

# ---------- Sidebar ----------
with st.sidebar:
    st.header("⚙️ Simulation Controls")
    n = st.slider("Board size (N)", min_value=4, max_value=12, value=st.session_state.n)
    mode = st.radio("Solve mode", ["First solution", "All solutions"], index=1 if st.session_state.mode == "All solutions" else 0)
    trace_limit = st.number_input(
        "Maximum trace events",
        min_value=1000,
        max_value=500000,
        value=int(st.session_state.trace_limit),
        step=1000,
        help="The trace is capped so large all-solution searches remain responsive."
    )
    show_conflicts = st.checkbox("Highlight conflicts", True)

    st.divider()
    st.subheader("🚀 Run")
    if st.button("Generate / Solve", type="primary", use_container_width=True):
        with st.spinner("Running backtracking and recording decisions..."):
            solutions, events, stats = solve_n_queens(
                n=n,
                find_all=(mode == "All solutions"),
                trace_limit=int(trace_limit),
            )
        st.session_state.n = n
        st.session_state.mode = mode
        st.session_state.trace_limit = int(trace_limit)
        st.session_state.solutions = solutions
        st.session_state.events = events
        st.session_state.stats = stats
        st.session_state.cursor = 0
        st.session_state.solution_index = 0
        st.session_state.solved = True
        st.rerun()

    if st.button("Reset", use_container_width=True):
        for key, value in defaults.items():
            st.session_state[key] = value
        st.rerun()

    st.divider()
    st.caption("Recommended demo: N=8 • All solutions")
    st.caption("For a fast visual trace, use N=4 or N=5.")

# ---------- Main ----------
if not st.session_state.solved:
    st.info("Configure the board in the sidebar and click **Generate / Solve** to start the visualizer.")
    st.markdown("""
    ### What this prototype demonstrates
    - **Decision visibility:** every placement, conflict and backtrack can be replayed.
    - **Constraint checking:** each candidate is tested against columns and diagonals.
    - **Backtracking:** invalid branches are undone so the search can continue.
    - **Evidence:** solution count, search nodes and execution statistics are captured.
    """)
    st.stop()

stats = st.session_state.stats
events = st.session_state.events
solutions = st.session_state.solutions
n = stats["n"]

# Metrics
mcols = st.columns(6)
metrics = [
    ("Solutions", stats["solutions"]),
    ("Placements", stats["placements"]),
    ("Conflicts", stats["conflicts"]),
    ("Backtracks", stats["backtracks"]),
    ("Search nodes", stats["nodes"]),
    ("Time", f'{stats["execution_seconds"]:.5f}s'),
]
for col, (label, value) in zip(mcols, metrics):
    col.markdown(metric_card(label, value), unsafe_allow_html=True)

if stats["trace_truncated"]:
    st.warning("The visualization trace reached its configured limit. Search statistics and solutions are still complete.")

tab_live, tab_solutions, tab_metrics, tab_algorithm = st.tabs(
    ["🎬 Live Visualizer", "♛ Solutions", "📊 Metrics", "🧠 Algorithm"]
)

# ---------- Live visualizer ----------
with tab_live:
    if not events:
        st.warning("No events recorded.")
    else:
        max_cursor = len(events) - 1
        c1, c2, c3, c4 = st.columns([1,1,2,1])
        if c1.button("⏮ Start", use_container_width=True):
            st.session_state.cursor = 0
            st.rerun()
        if c2.button("◀ Step", use_container_width=True):
            st.session_state.cursor = max(0, st.session_state.cursor - 1)
            st.rerun()
        if c3.button("▶ Step", use_container_width=True):
            st.session_state.cursor = min(max_cursor, st.session_state.cursor + 1)
            st.rerun()
        if c4.button("⏭ End", use_container_width=True):
            st.session_state.cursor = max_cursor
            st.rerun()

        cursor = st.session_state.cursor
        event = events[cursor]
        st.progress((cursor + 1) / len(events), text=f"Step {cursor+1} / {len(events)}")

        left, right = st.columns([1.35, 1])
        with left:
            st.markdown(event_board(event, n, show_conflicts), unsafe_allow_html=True)
            st.markdown(
                f"<div class='legend'><b>{event['action']}</b> — {event['message']}</div>",
                unsafe_allow_html=True,
            )
        with right:
            st.markdown("### Current decision")
            st.markdown(f"**Action:** `{event['action']}`")
            st.markdown(f"**Row:** `{event['row'] + 1 if event['row'] >= 0 else '—'}`")
            st.markdown(f"**Column:** `{event['col'] + 1 if event['col'] >= 0 else '—'}`")
            st.markdown(f"**Recursion depth:** `{event['depth']}`")
            st.markdown(f"**Message:** {event['message']}")

            st.markdown("### Event log")
            start = max(0, cursor - 9)
            recent = list(reversed(events[start:cursor+1]))
            for e in recent:
                st.markdown(
                    f"<div class='event'><strong>#{e['step']} {e['action']}</strong><br>{e['message']}</div>",
                    unsafe_allow_html=True,
                )

# ---------- Solutions ----------
with tab_solutions:
    if not solutions:
        st.warning("No solution found for this N.")
    else:
        idx = st.selectbox(
            "Select solution",
            range(len(solutions)),
            index=min(st.session_state.solution_index, len(solutions)-1),
            format_func=lambda x: f"Solution #{x+1}",
        )
        st.session_state.solution_index = idx
        sol = solutions[idx]
        st.markdown(solution_board(sol, n), unsafe_allow_html=True)

        cols = st.columns([1,1,2])
        cols[0].metric("Solution", f"#{idx+1}")
        cols[1].metric("Queens", n)
        cols[2].download_button(
            "⬇ Download solution CSV",
            data=solution_csv(sol),
            file_name=f"nqueens_{n}_solution_{idx+1}.csv",
            mime="text/csv",
            use_container_width=True,
        )

        with st.expander("Queen positions"):
            st.code(" | ".join(f"R{r+1} → C{c+1}" for r, c in enumerate(sol)))

# ---------- Metrics ----------
with tab_metrics:
    left, right = st.columns(2)
    with left:
        st.markdown("### Execution summary")
        metric_df = pd.DataFrame({
            "Metric": [
                "Board size",
                "Mode",
                "Solutions",
                "Placements",
                "Conflicts",
                "Backtracks",
                "Search nodes",
                "Maximum depth",
                "Trace events",
                "Execution time (s)",
            ],
            "Value": [
                stats["n"], stats["mode"], stats["solutions"], stats["placements"],
                stats["conflicts"], stats["backtracks"], stats["nodes"],
                stats["max_depth"], stats["trace_events"], f'{stats["execution_seconds"]:.6f}',
            ],
        })
        st.dataframe(metric_df, hide_index=True, use_container_width=True)

        st.download_button(
            "⬇ Download statistics JSON",
            data=stats_json(stats),
            file_name=f"nqueens_{n}_statistics.json",
            mime="application/json",
        )
        st.download_button(
            "⬇ Download trace CSV",
            data=trace_csv(events),
            file_name=f"nqueens_{n}_trace.csv",
            mime="text/csv",
        )

    with right:
        st.markdown("### Search activity")
        df = pd.DataFrame(events)
        if not df.empty:
            depth_series = df.groupby("step")["depth"].first()
            st.line_chart(depth_series, height=280)
            action_counts = df["action"].value_counts().rename_axis("action").reset_index(name="count")
            st.bar_chart(action_counts.set_index("action"), height=280)

# ---------- Algorithm ----------
with tab_algorithm:
    st.markdown("## Backtracking algorithm")
    st.markdown("""
**Goal:** place N queens on an N×N chessboard so that no two queens attack each other.

### Decision process

1. Start at row 1.
2. Try each column in the current row.
3. Check whether the column and both diagonals are free.
4. If safe, place a queen and move to the next row.
5. If a branch reaches a complete board, record the solution.
6. If the branch cannot continue, undo the previous placement and try the next candidate.
7. Repeat until the requested solution mode is complete.

### Constraints checked

- **Column:** `col`
- **Main diagonal:** `row - col`
- **Anti-diagonal:** `row + col`

### Complexity

For the core backtracking search, the commonly used worst-case bound is **O(N!)** time. The recursive board state uses **O(N)** auxiliary space, excluding stored solutions and the optional visualization trace.

### Why the visualizer matters

The app does not only display the final board. It exposes the algorithm's decisions: **PLACE → CONFLICT → BACKTRACK → SOLUTION**. This makes the search tree and constraint checks understandable during a hackathon demonstration.
""")

    st.markdown("### Pseudocode")
    st.code("""BACKTRACK(row):
    if row == N:
        record solution
        return

    for col in 0 ... N-1:
        if SAFE(row, col):
            place queen
            BACKTRACK(row + 1)
            remove queen       # backtrack
""", language="text")

    st.markdown("### Safe-position rule")
    st.code("""SAFE(row, col) =
    col is unused
    AND (row - col) diagonal is unused
    AND (row + col) diagonal is unused
""", language="text")

st.caption("QUEEN-VISION • N-Queens Visualizer • Backtracking • Hackathon prototype")
