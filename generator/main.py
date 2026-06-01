# generator/main.py

from postman_parser import parse_postman
from assertion_parser import convert_assertions
from correlation_engine import extract_variables
from scenario_builder import load_yaml
from jmx_generator import generate_jmx

postman = parse_postman("inputs/postman_collection.json")
scenarios = load_yaml("inputs/scenarios.yml")
profile = load_yaml("inputs/load_profile.yml")

final_scenarios = []

for sc in scenarios["scenarios"]:
    reqs = []

    for r in sc["requests"]:
        req = postman[r]

        req["correlations"] = extract_variables(req.get("tests", []))
        req["assertions"] = convert_assertions(req.get("tests", []))

        reqs.append(req)

    final_scenarios.append({
        "name": sc["name"],
        "requests": reqs
    })

context = {
    "users": profile["defaults"]["users"],
    "duration": profile["defaults"]["duration"],
    "scenarios": final_scenarios
}

generate_jmx(context)