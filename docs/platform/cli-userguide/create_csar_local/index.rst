Cli cloud complex Command Guide
===============================

1. create-vnf-package
---------------------

::

    usage: vfc-catalog-create-vnf
    vfc create vnf
    Options:
    [-m | -m | --host-url]
    [-c | -user-key]
    [-e | -user-value]
    [-C | --no-catalog]
    [-f | --format] [-h | --help] [-V | --verify]
    [-t | --no-title] [-d | --debug] [-v | --version]
    [-s | --long] [-D | --context]
    Error:
    Error:
    On error, it prints <STATUS CODE>::<ERROR CODE>::<ERROR MESSAGE>
    For example:
    'oclip vfc-catalog-create-vnf -m {} -c {} -e {}'.format(parameters["vfc-url"], \
          vnf_values.get("key"), vnf_values.get("value"))


2. create-ns-package
---------------------

::

    usage: vfc-catalog-create-ns
    vfc create ns
    Options:
    [-m | -m | --host-url]
    [-c | -user-key]
    [-e | -user-value]
    [-C | --no-catalog]
    [-f | --format] [-h | --help] [-V | --verify]
    [-t | --no-title] [-d | --debug] [-v | --version]
    [-s | --long] [-D | --context]
    Error:
    On error, it prints <STATUS CODE>::<ERROR CODE>::<ERROR MESSAGE>
    For example:
    'oclip vfc-catalog-create-ns -m {} -c {} -e {}'.format(parameters["vfc-url"], \
      ns.get("key"), ns.get("value"))
