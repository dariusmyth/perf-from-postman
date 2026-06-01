# generator/correlation_engine.py

def extract_variables(postman_tests):
    correlations = []

    for test_block in postman_tests:
        for line in test_block:
            if "pm.environment.set" in line:
                var = line.split('"')[1]
                correlations.append({
                    "type": "json",
                    "name": var,
                    "json_path": f"$.{var}"
                })

    return correlations