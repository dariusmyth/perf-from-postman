# generator/scenario_builder.py

import yaml


def load_yaml(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def build_scenarios(
        scenarios_yaml: dict,
        postman_requests: dict
):
    scenarios = []

    ordered = sorted(
        scenarios_yaml["scenarios"],
        key=lambda x: x["order"]
    )

    for scenario in ordered:

        requests = []

        for request_name in scenario["requests"]:

            if request_name not in postman_requests:
                raise Exception(
                    f"Request '{request_name}' not found in Postman collection"
                )

            requests.append(postman_requests[request_name])

        scenarios.append({
            "name": scenario["name"],
            "description": scenario.get("description", ""),
            "order": scenario["order"],
            "requests": requests
        })

    return scenarios