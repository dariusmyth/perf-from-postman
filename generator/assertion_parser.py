# generator/assertion_parser.py

def convert_assertions(tests):
    assertions = []

    for t in tests:
        for line in t:

            if "status(200)" in line:
                assertions.append({
                    "type": "response_code",
                    "expected": "200"
                })

            if ".to.exist" in line:
                assertions.append({
                    "type": "json_assertion",
                    "exists": True
                })

    return assertions