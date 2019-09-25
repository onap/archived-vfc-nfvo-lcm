Cli cloud complex Command Guide
===============================

1. create-vnf-package
---------------------

::

    usage: oclip complex-create
    Create a cloud complex in Onap
    Options:
    [-m | -m | --host-url]
    [-c | -user-key]
    [-e | -user-value]
    Error:
    On error, it prints <STATUS CODE>::<ERROR CODE>::<ERROR MESSAGE>
    For example:
    'oclip vfc-catalog-create-vnf -m {} -c {} -e {}'.format(parameters["vfc-url"], \
          vnf_values.get("key"), vnf_values.get("value"))