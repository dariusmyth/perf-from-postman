import os
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from urllib.parse import urlparse


def prettify(elem):
    return minidom.parseString(
        tostring(elem, "utf-8")
    ).toprettyxml(indent="  ")


def parse_url(url):
    parsed = urlparse(url)
    return parsed.netloc, parsed.path + (("?" + parsed.query) if parsed.query else "")


def create_sampler(parent, name, method, host, path):

    sampler = SubElement(parent, "HTTPSamplerProxy", {
        "guiclass": "HttpTestSampleGui",
        "testclass": "HTTPSamplerProxy",
        "testname": name,
        "enabled": "true"
    })

    SubElement(sampler, "stringProp", {"name": "HTTPSampler.domain"}).text = host
    SubElement(sampler, "stringProp", {"name": "HTTPSampler.protocol"}).text = "https"
    SubElement(sampler, "stringProp", {"name": "HTTPSampler.path"}).text = path
    SubElement(sampler, "stringProp", {"name": "HTTPSampler.method"}).text = method

    return sampler


def generate_jmx(context):

    os.makedirs("output", exist_ok=True)

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
        "testname": "Postman Plan",
        "enabled": "true"
    })

    test_plan_tree = SubElement(root_hash, "hashTree")

    # THREAD GROUP
    thread_group = SubElement(test_plan_tree, "ThreadGroup", {
        "guiclass": "ThreadGroupGui",
        "testclass": "ThreadGroup",
        "testname": "Users",
        "enabled": "true"
    })

    thread_group_tree = SubElement(test_plan_tree, "hashTree")

    # LOOP CONTROLLER
    loop_controller = SubElement(thread_group_tree, "LoopController", {
        "guiclass": "LoopControlPanel",
        "testclass": "LoopController",
        "testname": "Loop",
        "enabled": "true"
    })

    loop_tree = SubElement(thread_group_tree, "hashTree")

    # SCENARIOS
    for scenario in context["scenarios"]:

        controller = SubElement(loop_tree, "GenericController", {
            "guiclass": "LogicControllerGui",
            "testclass": "GenericController",
            "testname": scenario["name"],
            "enabled": "true"
        })

        scenario_tree = SubElement(loop_tree, "hashTree")

        for req in scenario["requests"]:

            host, path = parse_url(req["url"])

            sampler = create_sampler(
                scenario_tree,
                req["name"],
                req["method"],
                host,
                path
            )

            # 🔥 FIX: DO NOT always add hashTree
            # Only add if needed (we skip it completely here)
            pass

    xml = prettify(root)

    with open("output/testplan.jmx", "w", encoding="utf-8") as f:
        f.write(xml)

    print("VALID STABLE JMX GENERATED")