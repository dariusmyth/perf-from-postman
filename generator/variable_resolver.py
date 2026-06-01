# generator/variable_resolver.py

import re


POSTMAN_PATTERN = r"\{\{(.*?)\}\}"


def postman_to_jmeter(value: str):

    if not isinstance(value, str):
        return value

    matches = re.findall(
        POSTMAN_PATTERN,
        value
    )

    for match in matches:
        value = value.replace(
            "{{" + match + "}}",
            "${" + match + "}"
        )

    return value


def resolve_request_variables(request):

    request["url"] = postman_to_jmeter(
        request["url"]
    )

    if "body" in request:

        if isinstance(request["body"], dict):

            body_str = str(request["body"])

            request["body"] = postman_to_jmeter(
                body_str
            )

    return request