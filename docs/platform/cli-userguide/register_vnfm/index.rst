Cli Regist Vnfm Command Guide
===============================

1. Register-vnfm
----------------

::

    usage: oclip vnfm-create
    Register a VNFM in Onap
    Options:
    [-m | --host-url] [-C | --no-catalog] [-f | --format]
    [-h | --help] [-e | --vendor] [-V | --verify]
    [-t | --no-title] [-d | --debug] [-v | --version]
    [-y | --vnfm-id] [-c | --type] [-x | --vim-id]
    [-s | --long] [-D | --context] [-j | --password]
    [-b | --name] [-i | --username] [-u | --host-username]
    [-g | --url] [-a | --no-auth] [-q | --vnfm-version]
    [-z | --certificate-url] [-p | --host-password]
    Error:
    On error, it prints <STATUS CODE>::<ERROR CODE>::<ERROR MESSAGE>
    For example:
    'oclip vnfm-create -b {} -c {} -e {} -v {} -g {} -x {} -i {} -j {} -q {} \
    -m {} -u {} -p {}'.format(vnfm_key, values.get("type"), values.get("vendor"), \
      values.get("version"), values.get("url"), values.get("vim-id"), \
      values.get("user-name"), values.get("user-password"), values.get("vnfm-version"), \
      parameters["aai_url"], parameters["aai_username"], parameters["aai_password"])

2. vnfm list
---------------

::

    usage: oclip vnfm-list
    List the configured vnfm
    Product: onap-dublin Service: aai Author: ONAP CLI Team onap-discuss@lists.onap.org
    Options:
    [-m | --host-url] [-C | --no-catalog] [-f | --format]
    [-h | --help] [-V | --verify] [-t | --no-title]
    [-d | --debug] [-v | --version] [-s | --long]
    [-D | --context] [-u | --host-username] [-a | --no-auth]
    [-p | --host-password]
    For example:
        "oclip vnfm-list -m {} -u {} -p {}".format(parameters["aai_url"], parameters["aai_username"], \
                          parameters["aai_password"])


3. vnfm-delete
-----------------

::


    usage: oclip vnfm-delete
    Un-register a VNFM in Onap
    Options:
    [-m | --host-url] [-C | --no-catalog] [-f | --format]
    [-h | --help] [-V | --verify] [-t | --no-title]
    [-d | --debug] [-v | --version] [-y | --resource-version]
    [-x | --vnfm-id] [-s | --long] [-D | --context]
    [-u | --host-username] [-a | --no-auth] [-p | --host-password]
    For example:
    oclip vnfm-delete -m https://159.138.61.203:30233 -uAAI -p AAI -x 4839a0bc-60d1-4346-9c69-185d0962633b -y 1568450136276
    Note:
    vnfm-id and resource-version is the result returned after executing the vnfm-list command(command 2)
