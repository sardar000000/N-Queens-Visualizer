from __future__ import annotations

from dataclasses import dataclass, asdict
from time import perf_counter
from typing import Dict, List, Optional, Tuple


@dataclass
class Event:
    step: int
    action: str
    row: int
    col: int
    board: List[int]
    depth: int
    message: str

    def to_dict(self) -> Dict:
        return asdict(self)


class NQueensSolver:
    """Backtracking N-Queens solver with a replayable visualization trace."""

    def __init__(self, n: int, find_all: bool = True, trace_limit: int = 120_000):
        if not 4 <= n <= 12:
            raise ValueError("N must be between 4 and 12.")
        self.n = n
        self.find_all = find_all
        self.trace_limit = max(1_000, trace_limit)

        self.board = [-1] * n
        self.columns = set()
        self.diag_down = set()  # row - col
        self.diag_up = set()    # row + col

        self.solutions: List[List[int]] = []
        self.events: List[Event] = []
        self.placements = 0
        self.conflicts = 0
        self.backtracks = 0
        self.nodes = 0
        self.max_depth = 0
        self.truncated_trace = False

    def _record(self, action: str, row: int, col: int, depth: int, message: str):
        if len(self.events) >= self.trace_limit:
            self.truncated_trace = True
            return
        self.events.append(
            Event(
                step=len(self.events) + 1,
                action=action,
                row=row,
                col=col,
                board=self.board.copy(),
                depth=depth,
                message=message,
            )
        )

    def is_safe(self, row: int, col: int) -> bool:
        return (
            col not in self.columns
            and (row - col) not in self.diag_down
            and (row + col) not in self.diag_up
        )

    def _search(self, row: int) -> bool:
        self.max_depth = max(self.max_depth, row)
        if row == self.n:
            self.solutions.append(self.board.copy())
            self._record(
                "SOLUTION",
                row - 1,
                self.board[row - 1],
                row,
                f"Solution #{len(self.solutions)} found."
            )
            return not self.find_all

        found_one = False
        for col in range(self.n):
            self.nodes += 1
            if not self.is_safe(row, col):
                self.conflicts += 1
                self._record(
                    "CONFLICT",
                    row,
                    col,
                    row,
                    f"Conflict at row {row + 1}, column {col + 1}."
                )
                continue

            self.board[row] = col
            self.columns.add(col)
            self.diag_down.add(row - col)
            self.diag_up.add(row + col)
            self.placements += 1
            self._record(
                "PLACE",
                row,
                col,
                row + 1,
                f"Placed queen at row {row + 1}, column {col + 1}."
            )

            found_one = self._search(row + 1) or found_one

            if self.find_all and row < self.n:
                # Continue searching for remaining solutions.
                pass

            self.board[row] = -1
            self.columns.remove(col)
            self.diag_down.remove(row - col)
            self.diag_up.remove(row + col)

            self.backtracks += 1
            self._record(
                "BACKTRACK",
                row,
                col,
                row,
                f"Undo row {row + 1}, column {col + 1} and backtrack."
            )

            if found_one and not self.find_all:
                return True

        return found_one

    def solve(self) -> Dict:
        start = perf_counter()
        self._record("START", -1, -1, 0, f"Starting backtracking for N={self.n}.")
        self._search(0)
        elapsed = perf_counter() - start
        self._record(
            "FINISH",
            -1,
            -1,
            0,
            f"Search finished with {len(self.solutions)} solution(s)."
        )
        return {
            "n": self.n,
            "mode": "All solutions" if self.find_all else "First solution",
            "solutions": len(self.solutions),
            "placements": self.placements,
            "conflicts": self.conflicts,
            "backtracks": self.backtracks,
            "nodes": self.nodes,
            "max_depth": self.max_depth,
            "execution_seconds": elapsed,
            "trace_events": len(self.events),
            "trace_truncated": self.truncated_trace,
        }


def solve_n_queens(n: int, find_all: bool = True, trace_limit: int = 120_000):
    solver = NQueensSolver(n, find_all=find_all, trace_limit=trace_limit)
    stats = solver.solve()
    return solver.solutions, [e.to_dict() for e in solver.events], stats
