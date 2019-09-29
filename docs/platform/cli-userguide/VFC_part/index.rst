Cli VFC part Command Guide
===============================

1. VFC nslcm create
-------------------

::

    usage: oclip vfc-nslcm-create
    vfc nslcm create ns
    Options:
    [-n | --ns-csar-name] [-m | --host-url] [-c | --ns-csar-uuid]
    [-C | --no-catalog] [-f | --format] [-h | --help]
    [-V | --verify] [-t | --no-title] [-d | --debug]
    [-v | --version] [-s | --long] [-D | --context]
    Error:
    On error, it prints <STATUS CODE>::<ERROR CODE>::<ERROR MESSAGE>
    For example:
    'oclip vfc-nslcm-create -m {} -c {} -n {} -q {} -S {}'.format(parameters["vfc-url"], \
      csar_id, ns.get("name"), parameters["customer_name"], parameters["service_name"])


2. VFC nslcm instance
---------------------

::

    usage: oclip vfc-nslcm-instance
    vfc nslcm instance ns
    Options:
    [[-m | --host-url] [-C | --no-catalog] [-f | --format]
    [-h | --help] [-V | --verify] [-t | --no-title]
    [-d | --debug] [-v | --version] [-c | --location-constraints]
    [-s | --long] [-D | --context] [-i | --ns-instance-id]
    [-n | --sdn-controller-id]
    Error:
    On error, it prints <STATUS CODE>::<ERROR CODE>::<ERROR MESSAGE>
    For example:
    'oclip vfc-nslcm-instantiate -m {} -i {} -c {} -n {}'.format(parameters["vfc-url"], \
        ns_instance_id, parameters["location"], parameters["sdc-controller-id"])


3. VFC nslcm terminate
----------------------

::

    usage: oclip vfc-nslcm-terminate
    vfc nslcm terminate ns
    Options:
    [[-m | --host-url] [-C | --no-catalog] [-f | --format]
    [-h | --help] [-V | --verify] [-t | --no-title]
    [-d | --debug] [-v | --version] [-c | --location-constraints]
    [-s | --long] [-D | --context] [-i | --ns-instance-id]
    Error:
    On error, it prints <STATUS CODE>::<ERROR CODE>::<ERROR MESSAGE>
    For example:
    'oclip vfc-nslcm-terminate -m {} -i {}'.format(parameters["vfc-url"], ns_instance_id)

4. VFC nslcm delete
----------------------

::

    usage: oclip vfc-nslcm-delete
    vfc nslcm terminate ns
    Options:
    [[-m | --host-url] [-C | --no-catalog] [-f | --format]
    [-h | --help] [-V | --verify] [-t | --no-title]
    [-d | --debug] [-v | --version] [-c | --location-constraints]
    [-s | --long] [-D | --context] [-c | --ns-instance-id]
    Error:
    On error, it prints <STATUS CODE>::<ERROR CODE>::<ERROR MESSAGE>
    For example:
    'oclip vfc-nslcm-delete -m {} -c {}'.format(parameters["vfc-url"], ns_instance_id)
