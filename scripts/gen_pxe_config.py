#!/usr/bin/env python3
#
# Generate the files necessary to kickstart a host from PXE:
#
# PXEROOT/pxelinux.cfg/{hexaddr} - PXE file for stage 1 boot
# KSROOT/<hostname>-<distro><version>.ks - Kickstart file for stage 2
#
# USAGE: gen_pxe_config.py -t <template> [-c <config>]... [-d KEY=VALUE]...
#
# INPUTS
import yaml
import jinja2

def load_template(file):
    j2 = jinja2.Environment(
        loader=jinja2.FileSystemLoader("."),
        undefined=jinja2.StrictUndefined,
        trim_blocks=True)

    return j2.get_template(file) 

def merge_configs():

    os = { "distro": "fedora", "version": 30 }
    install_source = yaml.load(open("./configs/kickstart.yaml"), yaml.loader.BaseLoader)
    node_spec = yaml.load(open("./configs/node1.yaml"), yaml.loader.BaseLoader)
    secrets = yaml.load(open("./secrets.yaml"), yaml.loader.BaseLoader)

    config = { **os, **install_source, **node_spec, **secrets }

    return config

def gen_pxe_file(config):
    template = load_template("./templates/pxe-kickstart.j2")
    print(template.render(config))

def gen_kickstart_file(config):
    template = load_template("./templates/vanilla.ks.j2")
    print(template.render(config))


def main():

    config = merge_configs()
    gen_pxe_file(config)
    print("\n---\n")
    gen_kickstart_file(config)

if __name__ == "__main__":
    print("start")

    main()

    print("end")
