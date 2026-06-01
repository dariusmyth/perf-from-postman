# generator/postman_parser.py
import json

def parse_postman(path):
    with open(path) as f:
        data = json.load(f)

    requests = {}

    for item in data["item"]:
        name = item["name"]
        req = item["request"]

        events = item.get("event", [])

        tests = []
        pre_scripts = []

        for e in events:
            if e["listen"] == "test":
                tests.append(e["script"]["exec"])
            if e["listen"] == "prerequest":
                pre_scripts.append(e["script"]["exec"])

        requests[name] = {
            "method": req["method"],
            "url": req["url"]["raw"],
            "headers": req.get("header", []),
            "body": req.get("body", {}),
            "tests": tests,
            "pre": pre_scripts
        }

    return requests