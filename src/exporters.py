from __future__ import annotations

import csv
import io
import json
from typing import Dict, List


def stats_json(stats: Dict) -> str:
    return json.dumps(stats, indent=2)


def trace_csv(events: List[Dict]) -> str:
    output = io.StringIO()
    fieldnames = ["step", "action", "row", "col", "depth", "message", "board"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for event in events:
        writer.writerow({
            "step": event["step"],
            "action": event["action"],
            "row": event["row"] + 1 if event["row"] >= 0 else "",
            "col": event["col"] + 1 if event["col"] >= 0 else "",
            "depth": event["depth"],
            "message": event["message"],
            "board": ",".join(str(x + 1) if x >= 0 else "-" for x in event["board"]),
        })
    return output.getvalue()


def solution_csv(solution: List[int]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["row", "column"])
    for row, col in enumerate(solution, start=1):
        writer.writerow([row, col + 1])
    return output.getvalue()
