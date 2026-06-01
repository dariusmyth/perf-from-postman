from postman_parser import parse_postman
from assertion_parser import convert_assertions
from correlation_engine import extract_variables
from scenario_builder import load_yaml
from jmx_generator import generate_jmx

postman = parse_postman("inputs/postman_collection.json")

print("\n=== Requests discovered in Postman collection ===")
for key in postman.keys():
    print(f" - {key}")
print("===============================================\n")

scenarios_yaml = load_yaml("inputs/scenarios.yml")
profile = load_yaml("inputs/load_profile.yml")

final_scenarios = []

for scenario in scenarios_yaml["scenarios"]:

    scenario_requests = []

    for request_name in scenario["requests"]:

        if request_name not in postman:

            print(
                f"\nERROR: Request '{request_name}' "
                f"not found in Postman collection.\n"
            )

            print("Available requests:")

            for available in postman.keys():
                print(f" - {available}")

            raise Exception(
                f"Request '{request_name}' not found "
                f"in Postman collection"
            )

        req = postman[request_name]

        req["correlations"] = extract_variables(
            req.get("tests", [])
        )

        req["assertions"] = convert_assertions(
            req.get("tests", [])
        )

        scenario_requests.append(req)

    final_scenarios.append({
        "name": scenario["name"],
        "description": scenario.get("description", ""),
        "requests": scenario_requests
    })

context = {
    "users": profile["defaults"]["users"],
    "duration": profile["defaults"]["duration"],
    "scenarios": final_scenarios
}

generate_jmx(context)

print("JMX generated successfully")