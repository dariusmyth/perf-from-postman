import os
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom


def prettify(elem):
    rough_string = tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def add_httpsampler(parent, name, method, path):

    sampler = SubElement(parent, "HTTPSamplerProxy", {
        "guiclass": "HttpTestSampleGui",
        "testclass": "HTTPSamplerProxy",
        "testname": name,
        "enabled": "true"
    })

    SubElement(sampler, "stringProp", {
        "name": "HTTPSampler.method"
    }).text = method

    SubElement(sampler, "stringProp", {
        "name": "HTTPSampler.path"
    }).text = path

    return sampler


def generate_jmx(context):

    os.makedirs("output", exist_ok=True)

    # Root
    jmeter = Element("jmeterTestPlan", {
        "version": "1.2",
        "properties": "5.0",
        "jmeter": "5.6.3"
    })

    tree = SubElement(jmeter, "hashTree")

    # TEST PLAN
    test_plan = SubElement(tree, "TestPlan", {
        "guiclass": "TestPlanGui",
        "testclass": "TestPlan",
        "testname": "Postman Generated Test Plan",
        "enabled": "true"
    })

    SubElement(test_plan, "stringProp", {
        "name": "TestPlan.comments"
    }).text = "Generated from Postman collection"

    test_plan_tree = SubElement(tree, "hashTree")

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

        # Scenario controller
        controller = SubElement(loop_tree, "GenericController", {
            "guiclass": "LogicControllerGui",
            "testclass": "GenericController",
            "testname": scenario["name"],
            "enabled": "true"
        })

        controller_tree = SubElement(loop_tree, "hashTree")

        for req in scenario["requests"]:

            # Convert Postman URL → path only
            url = req["url"]

            if "http" in url:
                path = "/" + "/".join(url.split("/")[3:])
            else:
                path = url

            sampler = add_httpsampler(
                controller_tree,
                req["name"],
                req["method"],
                path
            )

            SubElement(controller_tree, "hashTree")

    # OUTPUT
    xml_str = prettify(jmeter)

    with open("output/testplan.jmx", "w", encoding="utf-8") as f:
        f.write(xml_str)

    print("VALID JMX generated at output/testplan.jmx")