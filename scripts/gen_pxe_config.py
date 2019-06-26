#!/usr/bin/env python3
#
# USAGE: gen_pxe_config.py -t <template> [-c <config>]... [-d KEY=VALUE]...
#
import yaml
import jinja2

if __name__ == "__main__":
    print("start")

    j2 = jinja2.Environment(
        loader=jinja2.FileSystemLoader("."),
        undefined=jinja2.StrictUndefined,
        trim_blocks=True)

    template = j2.get_template("./templates/vanilla.ks.j2")

    os = { "distro": "fedora", "version": 30 }
    install_source = yaml.load(open("./configs/kickstart.yaml"), yaml.loader.BaseLoader)
    node_spec = yaml.load(open("./configs/node1.yaml"), yaml.loader.BaseLoader)
    secrets = yaml.load(open("./secrets.yaml"), yaml.loader.BaseLoader)

    config = { **os, **install_source, **node_spec, **secrets }

    print(template.render(config))
    
    print("end")
