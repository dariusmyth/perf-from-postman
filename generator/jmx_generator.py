import os
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from urllib.parse import urlparse
import time


def prettify(elem):
    return minidom.parseString(
        tostring(elem, "utf-8")
    ).toprettyxml(indent="  ")


def parse_url(url):
    """
    Return (scheme, netloc, path_with_query)
    """
    p = urlparse(url)
    path = p.path or "/"
    if p.query:
        path = path + "?" + p.query
    scheme = p.scheme if p.scheme else "https"
    return scheme, p.netloc, path


def create_sampler(parent, name, method, protocol, host, path, headers=None, body=None):
    """
    Create an HTTPSamplerProxy under `parent`.
    Returns the sampler element (already appended to parent).
    Caller should create a sibling hashTree after this sampler in the parent.
    """

    sampler = SubElement(parent, "HTTPSamplerProxy", {
        "guiclass": "HttpTestSampleGui",
        "testclass": "HTTPSamplerProxy",
        "testname": name,
        "enabled": "true"
    })

    # Arguments container (empty by default)
    args_ep = SubElement(sampler, "elementProp", {
        "name": "HTTPsampler.Arguments",
        "elementType": "Arguments",
        "guiclass": "HTTPArgumentsPanel",
        "testclass": "Arguments",
        "testname": "User Defined Variables"
    })
    args_collection = SubElement(args_ep, "collectionProp", {"name": "Arguments.arguments"})
    # (If body is form-data / params, we could populate Arguments.arguments here)

    SubElement(sampler, "stringProp", {"name": "HTTPSampler.domain"}).text = host.split(":")[0] if host else ""
    # split out port if present in netloc
    port = ""
    if ":" in host:
        port = host.split(":", 1)[1]
    SubElement(sampler, "stringProp", {"name": "HTTPSampler.port"}).text = port
    SubElement(sampler, "stringProp", {"name": "HTTPSampler.protocol"}).text = protocol
    SubElement(sampler, "stringProp", {"name": "HTTPSampler.contentEncoding"}).text = ""
    SubElement(sampler, "stringProp", {"name": "HTTPSampler.path"}).text = path
    SubElement(sampler, "stringProp", {"name": "HTTPSampler.method"}).text = method

    # Other typical sampler properties
    SubElement(sampler, "boolProp", {"name": "HTTPSampler.follow_redirects"}).text = "true"
    SubElement(sampler, "boolProp", {"name": "HTTPSampler.auto_redirects"}).text = "false"
    SubElement(sampler, "boolProp", {"name": "HTTPSampler.use_keepalive"}).text = "true"
    SubElement(sampler, "boolProp", {"name": "HTTPSampler.DO_MULTIPART_POST"}).text = "false"
    SubElement(sampler, "boolProp", {"name": "HTTPSampler.postBodyRaw"}).text = "false"

    # If there is a raw body, set postBodyRaw true and add it as an entry in Arguments
    if body:
        # body could be dict as returned from Postman parser; check for 'mode' and 'raw'
        mode = body.get("mode")
        if mode == "raw" and "raw" in body:
            SubElement(sampler, "boolProp", {"name": "HTTPSampler.postBodyRaw"}).text = "true"
            # Add raw body as an argument
            arg = SubElement(args_collection, "elementProp", {
                "name": "",
                "elementType": "HTTPArgument"
            })
            SubElement(arg, "boolProp", {"name": "HTTPArgument.always_encode"}).text = "false"
            SubElement(arg, "stringProp", {"name": "Argument.value"}).text = body["raw"]
            SubElement(arg, "stringProp", {"name": "Argument.metadata"}).text = "="

    return sampler


def add_header_manager(parent_hash_tree, headers):
    """
    Add a HeaderManager as a child (and also append its own hashTree).
    parent_hash_tree is the hashTree that follows the sampler.
    """
    hm = SubElement(parent_hash_tree, "HeaderManager", {
        "guiclass": "HeaderPanel",
        "testclass": "HeaderManager",
        "testname": "HTTP Header Manager",
        "enabled": "true"
    })
    coll = SubElement(hm, "collectionProp", {"name": "HeaderManager.headers"})
    for h in headers or []:
        # Postman headers may be dicts like {'key': 'Content-Type', 'value': 'application/json'}
        name = h.get("key") or h.get("name") or h.get("Key") or ""
        value = h.get("value") or h.get("Value") or ""
        elem = SubElement(coll, "elementProp", {"name": "", "elementType": "Header"})
        SubElement(elem, "stringProp", {"name": "Header.name"}).text = name
        SubElement(elem, "stringProp", {"name": "Header.value"}).text = value

    # Every test element should be followed by a hashTree; here we append the sampler's child hashTree
    SubElement(parent_hash_tree, "hashTree")


def generate_jmx(context):
    """
    context expected shape:
    {
      "users": <int>,
      "duration": <int seconds>,
      "scenarios": [
         { "name": "...", "description": "...", "requests": [ { name, method, url, headers, body, tests, pre, correlations, assertions }, ... ] }
      ]
    }
    """
    os.makedirs("output", exist_ok=True)

    root = Element("jmeterTestPlan", {
        "version": "1.2",
        "properties": "5.0",
        "jmeter": "5.6.3"
    })

    root_hash = SubElement(root, "hashTree")

    # TestPlan
    test_plan = SubElement(root_hash, "TestPlan", {
        "guiclass": "TestPlanGui",
        "testclass": "TestPlan",
        "testname": "Postman Plan",
        "enabled": "true"
    })

    # user-defined variables (empty)
    udv = SubElement(test_plan, "elementProp", {
        "name": "TestPlan.user_defined_variables",
        "elementType": "Arguments",
        "guiclass": "ArgumentsPanel",
        "testclass": "Arguments",
        "testname": "User Defined Variables"
    })
    SubElement(udv, "collectionProp", {"name": "Arguments.arguments"})

    SubElement(test_plan, "stringProp", {"name": "TestPlan.comments"}).text = ""
    SubElement(test_plan, "boolProp", {"name": "TestPlan.functional_mode"}).text = "false"
    SubElement(test_plan, "boolProp", {"name": "TestPlan.serialize_threadgroups"}).text = "false"

    test_plan_tree = SubElement(root_hash, "hashTree")

    # ThreadGroup container
    tg = SubElement(test_plan_tree, "ThreadGroup", {
        "guiclass": "ThreadGroupGui",
        "testclass": "ThreadGroup",
        "testname": "Users",
        "enabled": "true"
    })

    # ThreadGroup main controller (LoopController as elementProp)
    main_controller = SubElement(tg, "elementProp", {
        "name": "ThreadGroup.main_controller",
        "elementType": "LoopController",
        "guiclass": "LoopControlPanel",
        "testclass": "LoopController",
        "testname": "Loop Controller"
    })
    SubElement(main_controller, "boolProp", {"name": "LoopController.continue_forever"}).text = "false"
    # If duration provided, set loops to -1 so scheduler can stop the ThreadGroup by duration
    loops = "-1" if context.get("duration") else "1"
    SubElement(main_controller, "stringProp", {"name": "LoopController.loops"}).text = loops

    SubElement(tg, "stringProp", {"name": "ThreadGroup.on_sample_error"}).text = "continue"
    SubElement(tg, "stringProp", {"name": "ThreadGroup.num_threads"}).text = str(context.get("users", 1))
    SubElement(tg, "stringProp", {"name": "ThreadGroup.ramp_time"}).text = "1"
    # scheduler
    if context.get("duration"):
        SubElement(tg, "boolProp", {"name": "ThreadGroup.scheduler"}).text = "true"
        SubElement(tg, "stringProp", {"name": "ThreadGroup.duration"}).text = str(context["duration"])
    else:
        SubElement(tg, "boolProp", {"name": "ThreadGroup.scheduler"}).text = "false"

    # Optional timing props
    now = int(time.time() * 1000)
    SubElement(tg, "longProp", {"name": "ThreadGroup.start_time"}).text = str(now)
    SubElement(tg, "longProp", {"name": "ThreadGroup.end_time"}).text = str(now + (context.get("duration", 0) * 1000))

    thread_group_tree = SubElement(test_plan_tree, "hashTree")

    # We'll put per-scenario GenericControllers under the LoopController area (loop_tree)
    # Create a top-level LoopController container so scenarios can be grouped
    # In the original code the loop controller was placed under thread_group_tree; keep that but structure the children correctly
    loop_controller = SubElement(thread_group_tree, "GenericController", {
        "guiclass": "LogicControllerGui",
        "testclass": "GenericController",
        "testname": "Scenario Container",
        "enabled": "true"
    })
    loop_tree = SubElement(thread_group_tree, "hashTree")

    # For each scenario create a GenericController + its hashTree; inside the scenario hashTree, put samplers
    for scenario in context.get("scenarios", []):
        controller = SubElement(loop_tree, "GenericController", {
            "guiclass": "LogicControllerGui",
            "testclass": "GenericController",
            "testname": scenario.get("name", "scenario"),
            "enabled": "true"
        })
        scenario_tree = SubElement(loop_tree, "hashTree")

        for req in scenario.get("requests", []):
            scheme, host, path = parse_url(req["url"])
            sampler = create_sampler(
                scenario_tree,
                req.get("name", ""),
                req.get("method", "GET"),
                scheme,
                host,
                path,
                headers=req.get("headers", []),
                body=req.get("body", {})
            )

            # CRITICAL: the hashTree must be a sibling (child of scenario_tree) immediately after sampler
            sampler_hash = SubElement(scenario_tree, "hashTree")

            # Add header manager (if headers present) inside sampler_hash
            if req.get("headers"):
                add_header_manager(sampler_hash, req["headers"])
            # If we add other elements (post processors / assertions / extractors), they'd also go in this sampler_hash
            # ensure each element is followed by its own hashTree if needed.

    xml = prettify(root)

    with open("output/testplan.jmx", "w", encoding="utf-8") as f:
        f.write(xml)

    print("VALID JMX GENERATED")