# analytics/trend_builder.py

import json
import os
from datetime import datetime

def load_last_runs():
    runs_dir = "results/runs"
    if not os.path.exists(runs_dir):
        return []

    # Only include directories (ignore files like created.md)
    runs = [d for d in sorted(os.listdir(runs_dir)) if os.path.isdir(os.path.join(runs_dir, d))]

    # Keep the last 5 run directories
    runs = runs[-5:]

    data = []

    for r in runs:
        path = os.path.join(runs_dir, r, "summary.json")

        if os.path.exists(path):
            with open(path) as f:
                data.append(json.load(f))

    return data


def build_trend():
    runs = load_last_runs()

    trend = {
        "avg_response_time": [],
        "error_rate": [],
        "timestamps": []
    }

    for r in runs:
        # guard access if keys missing in summary.json
        trend["avg_response_time"].append(r.get("avg_rt"))
        trend["error_rate"].append(r.get("errors"))
        trend["timestamps"].append(r.get("timestamp"))

    return trend


def save_trend(trend):
    os.makedirs("results/trend", exist_ok=True)

    with open("results/trend/trend.json", "w") as f:
        json.dump(trend, f, indent=2)