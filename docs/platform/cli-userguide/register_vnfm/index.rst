Cli Regist Vnfm Command Guide
===============================

1. Register-vnfm
----------------

::

    usage: oclip vnfm-create
    Register a VNFM in Onap
    Product: onap-dublin Service: aai Author: ONAP CLI Team onap-discuss@lists.onap.org
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
