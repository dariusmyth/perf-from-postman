import os
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from urllib.parse import urlparse


def prettify(elem):
    rough = tostring(elem, "utf-8")
    reparsed = minidom.parseString(rough)
    return reparsed.toprettyxml(indent="  ")


def parse_url(full_url):
    """
    Converts Postman URL → JMeter host + path
    """
    parsed = urlparse(full_url)

    host = parsed.netloc
    path = parsed.path

    if parsed.query:
        path += "?" + parsed.query

    return host, path


def add_http_sampler(parent, name, method, host, path):

    sampler = SubElement(parent, "HTTPSamplerProxy", {
        "guiclass": "HttpTestSampleGui",
        "testclass": "HTTPSamplerProxy",
        "testname": name,
        "enabled": "true"
    })

    SubElement(sampler, "stringProp", {
        "name": "HTTPSampler.domain"
    }).text = host

    SubElement(sampler, "stringProp", {
        "name": "HTTPSampler.port"
    }).text = ""

    SubElement(sampler, "stringProp", {
        "name": "HTTPSampler.protocol"
    }).text = "https"

    SubElement(sampler, "stringProp", {
        "name": "HTTPSampler.path"
    }).text = path

    SubElement(sampler, "stringProp", {
        "name": "HTTPSampler.method"
    }).text = method

    return sampler


def generate_jmx(context):

    os.makedirs("output", exist_ok=True)

    # ROOT
    root = Element("jmeterTestPlan", {
        "version": "1.2",
        "properties": "5.0",
        "jmeter": "5.6.3"
    })

    root_hash = SubElement(root, "hashTree")

    # TEST PLAN
    test_plan = SubElement(root_hash, "TestPlan", {
        "guiclass": "TestPlanGui",
        "testclass": "TestPlan",
        "testname": "Postman Generated Test Plan",
        "enabled": "true"
    })

    SubElement(test_plan, "stringProp", {
        "name": "TestPlan.comments"
    }).text = "Generated from Postman"

    SubElement(test_plan, "boolProp", {
        "name": "TestPlan.functional_mode"
    }).text = "false"

    test_plan_tree = SubElement(root_hash, "hashTree")

    # THREAD GROUP
    thread_group = SubElement(test_plan_tree, "ThreadGroup", {
        "guiclass": "ThreadGroupGui",
        "testclass": "ThreadGroup",
        "testname": "Users",
        "enabled": "true"
    })

    SubElement(thread_group, "stringProp", {
        "name": "ThreadGroup.num_threads"
    }).text = str(context.get("users", 1))

    SubElement(thread_group, "stringProp", {
        "name": "ThreadGroup.ramp_time"
    }).text = "1"

    SubElement(thread_group, "stringProp", {
        "name": "ThreadGroup.on_sample_error"
    }).text = "continue"

    thread_group_tree = SubElement(test_plan_tree, "hashTree")

    # LOOP CONTROLLER
    loop_controller = SubElement(thread_group_tree, "LoopController", {
        "guiclass": "LoopControlPanel",
        "testclass": "LoopController",
        "testname": "Loop Controller",
        "enabled": "true"
    })

    SubElement(loop_controller, "boolProp", {
        "name": "LoopController.continue_forever"
    }).text = "false"

    SubElement(loop_controller, "stringProp", {
        "name": "LoopController.loops"
    }).text = "1"

    loop_tree = SubElement(thread_group_tree, "hashTree")

    # REQUESTS FROM POSTMAN
    for scenario in context["scenarios"]:

        scenario_controller = SubElement(loop_tree, "GenericController", {
            "guiclass": "LogicControllerGui",
            "testclass": "GenericController",
            "testname": scenario["name"],
            "enabled": "true"
        })

        scenario_tree = SubElement(loop_tree, "hashTree")

        for req in scenario["requests"]:

            host, path = parse_url(req["url"])

            add_http_sampler(
                scenario_tree,
                req["name"],
                req["method"],
                host,
                path
            )

            # IMPORTANT: hashTree for sampler (required by JMeter)
            SubElement(scenario_tree, "hashTree")

    # WRITE FILE
    xml_output = prettify(root)

    with open("output/testplan.jmx", "w", encoding="utf-8") as f:
        f.write(xml_output)

    print("✅ Valid JMeter JMX generated at output/testplan.jmx")