# analytics/trend_builder.py

import json
import os
from datetime import datetime

def load_last_runs():
    runs_dir = "results/runs"
    runs = sorted(os.listdir(runs_dir))[-5:]

    data = []

    for r in runs:
        path = f"{runs_dir}/{r}/summary.json"

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
        trend["avg_response_time"].append(r["avg_rt"])
        trend["error_rate"].append(r["errors"])
        trend["timestamps"].append(r["timestamp"])

    return trend


def save_trend(trend):
    os.makedirs("results/trend", exist_ok=True)

    with open("results/trend/trend.json", "w") as f:
        json.dump(trend, f, indent=2)