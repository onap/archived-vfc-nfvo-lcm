Cli Regist Clouds Command Guide
===============================

1. Register-all-clouds
----------------------

::

    usage: oclip cloud-create
    Create a cloud region in Onap
    Product: onap-dublin Service: aai Author: Intel ONAP HPA integration team (itohan.ukponmwan@intel.com)
    Options:
    [-e | --esr-id] [-V | --verify] [-f | --format]
    [-h | --help] [-t | --no-title] [-v | --version]
    [-c | --cloud-domain] [-s | --long] [-b | --user-name]
    [-r | --owner-type] [-S | --sriov-automation] [-I | --extra-info]
    [-x | --cloud-owner] [-Q | --system-type] [-y | --region-name]
    [-j | --password] [-a | --no-auth] [-w | --cloud-region-version]
    [-p | --host-password] [-m | --host-url] [-C | --no-catalog]
    [-i | --identity-url] [-d | --debug] [-g | --cloud-zone]
    [-l | --default-tenant] [-url | --service-url] [-n | --complex-name]
    [-q | --cloud-type] [-D | --context] [-z | --ssl-insecure]
    [-k | --system-status] [-u | --host-username]
    Error:
    On error, it prints <STATUS CODE>::<ERROR CODE>::<ERROR MESSAGE>
    For example:
    'oclip cloud-create -e {} -b {} -I {{\\\\\\"openstack-region-id\\\\\\":\\\\\\"{}\\\\\\"}} \
    -x {} -y {} -j {} -w {} -l {} -url {} -n {} -q {} -r {} -Q {} -i {} -g {} -z {} -k {} -c {} -m {} -u {} -p {}'.format(
      values.get("esr-system-info-id"), values.get("user-name"), cloud_region, parameters["cloud-owner"], \
      cloud_region, values.get("password"), values.get("cloud-region-version"), values.get("default-tenant"), \
      values.get("service-url"), parameters["complex_name"], values.get("cloud-type"), parameters["owner-defined-type"], \
      values.get("system-type"), values.get("identity-url"), parameters["cloud-zone"], values.get("ssl-insecure"), \
      values.get("system-status"), values.get("cloud-domain"), parameters["aai_url"], parameters["aai_username"], \
      parameters["aai_password"])