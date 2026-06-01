import json


def process_items(items, requests):

    for item in items:

        if "item" in item:
            process_items(item["item"], requests)
            continue

        name = item["name"]

        request = item["request"]

        events = item.get("event", [])

        tests = []
        prerequests = []

        for event in events:

            if event["listen"] == "test":
                tests.append(
                    event["script"]["exec"]
                )

            if event["listen"] == "prerequest":
                prerequests.append(
                    event["script"]["exec"]
                )

        requests[name] = {
            "name": name,
            "method": request["method"],
            "url": request["url"]["raw"],
            "headers": request.get("header", []),
            "body": request.get("body", {}),
            "tests": tests,
            "pre": prerequests
        }


def parse_postman(path):

    with open(path, "r") as f:
        collection = json.load(f)

    requests = {}

    process_items(
        collection["item"],
        requests
    )

    return requests