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
#
# distro
# version
# hostspec
# PXE/kickstart service spec
# secrets spec
# 
#
# Where are the templates?
# Where are the config data files?

# Where do I put the PXE file? what is it called?
#
# Where do I put the kickstart file? what is it called?


import yaml
import jinja2
import re
import sys
import os
import argparse

pxe_root = "./pxe"
ks_root = "./kickstart"

#
# From https://github.com/bd808/python-iptools
#

_DOTTED_QUAD_RE = re.compile(r'^(\d{1,3}\.){0,3}\d{1,3}$')

def validate_ip (s):
    """Validate a dotted-quad ip address.
    The string is considered a valid dotted-quad address if it consists of
    one to four octets (0-255) seperated by periods (.).
    >>> validate_ip('127.0.0.1')
    True
    >>> validate_ip('127.0')
    True
    >>> validate_ip('127.0.0.256')
    False
    >>> validate_ip(None) #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    TypeError: expected string or buffer
    :param s: String to validate as a dotted-quad ip address.
    :type s: str
    :returns: ``True`` if a valid dotted-quad ip address, ``False`` otherwise.
    :raises: TypeError
    """
    if _DOTTED_QUAD_RE.match(s):
        quads = s.split('.')
        for q in quads:
            if int(q) > 255:
                return False
        return True
    return False
#end validate_ip

def ip2long (ip):
    """Convert a dotted-quad ip address to a network byte order 32-bit
    integer.
    >>> ip2long('127.0.0.1')
    2130706433
    >>> ip2long('127.1')
    2130706433
    >>> ip2long('127')
    2130706432
    >>> ip2long('127.0.0.256') is None
    True
    :param ip: Dotted-quad ip address (eg. '127.0.0.1').
    :type ip: str
    :returns: Network byte order 32-bit integer or ``None`` if ip is invalid.
    """
    if not validate_ip(ip):
        return None
    quads = ip.split('.')
    if len(quads) == 1:
        # only a network quad
        quads = quads + [0, 0, 0]
    elif len(quads) < 4:
        # partial form, last supplied quad is host address, rest is network
        host = quads[-1:]
        quads = quads[:-1] + [0,] * (4 - len(quads)) + host

    lngip = 0
    for q in quads:
        lngip = (lngip << 8) | int(q)
    return lngip
#end ip2long

def ip2hex (addr):
    """Convert a dotted-quad ip address to a hex encoded number.
    >>> ip2hex('0.0.0.1')
    '00000001'
    >>> ip2hex('127.0.0.1')
    '7f000001'
    >>> ip2hex('127.255.255.255')
    '7fffffff'
    >>> ip2hex('128.0.0.1')
    '80000001'
    >>> ip2hex('128.1')
    '80000001'
    >>> ip2hex('255.255.255.255')
    'ffffffff'
    :param addr: Dotted-quad ip address.
    :type addr: str
    :returns: Numeric ip address as a hex-encoded string or ``None`` if
        invalid.
    """
    netip = ip2long(addr)
    if netip is None:
        return None
    return "%08x" % netip
#end ip2hex

# =============================================================================
#
# =============================================================================

def process_cli(args):
    parser = argparse.ArgumentParser()

    parser.add_argument("--mode", default="kickstart", choices=["kickstart", "manual", "rescue"])
    parser.add_argument("--hostname", "-H")
    parser.add_argument("--distro", "--distribution", default="fedora")
    parser.add_argument("--version", default="30")

    return parser.parse_args()
#
# 
#
def load_template(file):
    j2 = jinja2.Environment(
        loader=jinja2.FileSystemLoader("."),
        undefined=jinja2.StrictUndefined,
        trim_blocks=True)

    return j2.get_template(file) 

def merge_configs(opts):

    os = {"mode": opts.mode, "distro": opts.distro, "version": opts.version}
    
    install_source = yaml.load(open("./configs/kickstart.yaml"), yaml.loader.BaseLoader)
    node_spec = yaml.load(open("./configs/{}.yaml".format(opts.hostname)), yaml.loader.BaseLoader)
    secrets = yaml.load(open("./secrets.yaml"), yaml.loader.BaseLoader)

    config = { **os, **install_source, **node_spec, **secrets }

    return config

def gen_pxe_file(config):
    template = load_template("./templates/pxe-{}.j2".format(config['mode']))
    return template.render(config)

def gen_kickstart_file(config):
    template = load_template("./templates/{}{}.ks.j2".format(config['distro'], config['version']))
    return template.render(config)



def main():

    opts = process_cli(sys.argv)
    # Process inputs

    config = merge_configs(opts)
    pxe_content = gen_pxe_file(config)
    kickstart_content = gen_kickstart_file(config)

    hex_address = ip2hex(config['ipaddress']).upper()
    
    pxe_file_name = os.path.join(pxe_root, hex_address)
    print("writing to {}".format(pxe_file_name))
    pxe_file = open(pxe_file_name, "w")
    pxe_file.write(pxe_content)
    pxe_file.close()

    if opts.mode == "kickstart":
        ks_file_name = os.path.join(
            ks_root,
            "{}-{}{}.ks".format(
                config['hostname'],
                config['distro'],
                config['version']))

        print("writing to {}".format(ks_file_name))
        ks_file = open(ks_file_name, "w")
        ks_file.write(kickstart_content)
        ks_file.close()

    
if __name__ == "__main__":
    print("start")

    main()

    print("end")
