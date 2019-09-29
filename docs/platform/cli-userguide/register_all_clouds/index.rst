Cli Regist Clouds Command Guide
===============================

1. Register-all-clouds
----------------------

::

    usage: oclip cloud-create
    Create a cloud region in Onap
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


2. cloud list
--------------

::

    usage: oclip cloud-list
    List the configured clouds and Onap service subscriptions
    Options:
    [-m | --host-url] [-C | --no-catalog] [-f | --format]
    [-h | --help] [-V | --verify] [-t | --no-title]
    [-d | --debug] [-v | --version] [-s | --long]
    [-D | --context] [-u | --host-username] [-a | --no-auth]
    [-p | --host-password]
    For example:
    "oclip cloud-list -m {} -u {} -p {}".format(parameters["aai_url"], parameters["aai_username"], \
                          parameters["aai_password"])

3. cloud delete
---------------

::

    usage: oclip cloud-delete
    Delete a cloud region from Onap
    Options:
    [-m | --host-url] [-C | --no-catalog] [-f | --format]
    [-h | --help] [-V | --verify] [-t | --no-title]
    [-d | --debug] [-v | --version] [-x | --cloud-name]
    [-z | --resource-version] [-s | --long] [-D | --context]
    [-y | --region-name] [-u | --host-username] [-a | --no-auth]
    [-p | --host-password]
    For example:
    oclip cloud-delete -m https://159.138.61.203:30233 -u AAI -p AAI -y admin-fd -z 1568466594680 -x CloudOwner
   Note:
    region-name and resource-version and cloud-name is the result returned after executing the cloud-list command(command 2)
