# generator/jmx_generator.py

from jinja2 import Environment, FileSystemLoader

def generate_jmx(context):
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("testplan.j2")

    rendered = template.render(context)

    with open("output/testplan.jmx", "w") as f:
        f.write(rendered)