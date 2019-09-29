Cli cloud complex Command Guide
===============================

1. complex-create
-----------------

::

    usage: oclip complex-create
    Create a cloud complex in Onap
    Options:
    [-V | --verify] [-f | --format] [-h | --help]
    [-t | --no-title] [-j | --street2] [-v | --version]
    [-r | --physical-location-type] [-s | --long] [-lt | --latitude]
    [-x | --physical-location-id] [-y | --data-center-code] [-a | --no-auth]
    [-l | --region] [-p | --host-password] [-m | --host-url]
    [-C | --no-catalog] [-i | --street1] [-lo | --longitude]
    [-d | --debug] [-S | --state] [-la | --lata]
    [-D | --context] [-g | --city] [-w | --postal-code]
    [-z | --complex-name] [-k | --country] [-o | --elevation]
    [-u | --host-username] [-q | --identity-url]
    Error:
    On error, it prints <STATUS CODE>::<ERROR CODE>::<ERROR MESSAGE>
    For example:
    "oclip complex-create -j {} -r {} -x {} -y {} -lt {} -l {} -i {} -lo {} \
                         -S {} -la {} -g {} -w {} -z {} -k {} -o {} -q {} -m {} -u {} -p {}".format(parameters["street2"], \
                          parameters["physical_location"], parameters["complex_name"], \
                          parameters["data_center_code"], parameters["latitude"], parameters["region"], \
                          parameters["street1"], parameters["longitude"], parameters["state"], \
                          parameters["lata"], parameters["city"], parameters["postal-code"], \
                          parameters["complex_name"], parameters["country"], parameters["elevation"], \
                          parameters["identity_url"], parameters["aai_url"], parameters["aai_username"], \
                          parameters["aai_password"])

2. complex-list
-----------------

::


    usage: oclip complex-list
    List the configured complexes
    Options:
    [-m | --host-url] [-C | --no-catalog] [-f | --format]
    [-h | --help] [-V | --verify] [-t | --no-title]
    [-d | --debug] [-v | --version] [-s | --long]
    [-D | --context] [-u | --host-username] [-a | --no-auth]
    [-p | --host-password]
    For example:
    "oclip complex-list -m {} -u {} -p {}".format(parameters["aai_url"], parameters["aai_username"], \
                          parameters["aai_password"])


3. complex-delete
-----------------

::


    usage: oclip complex-delete
    Delete a complex from Onap
    Options:
    [-m | --host-url] [-C | --no-catalog] [-f | --format]
    [-h | --help] [-V | --verify] [-t | --no-title]
    [-d | --debug] [-v | --version] [-y | --resource-version]
    [-s | --long] [-D | --context] [-x | --complex-name]
    [-u | --host-username] [-a | --no-auth] [-p | --host-password]
    For example:
    oclip complex-delete -m https://159.138.61.203:30233 -u AAI -p AAI -x clli1 -y 1568444028429
    Note:
    complex-name and resource-version is the result returned after executing the complex-list command(command 2)
