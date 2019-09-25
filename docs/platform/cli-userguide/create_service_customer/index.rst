Cli Create Service and Customer Command Guide
=============================================

1. create-service-type
-----------------------

::

    usage: oclip service-type-create
    Add a service type in Onap
    Product: onap-dublin Service: aai Author: ONAP CLI Team onap-discuss@lists.onap.org
    Options:
    [-m | --host-url] [-C | --no-catalog] [-x | --service-type]
    [-f | --format] [-h | --help] [-V | --verify]
    [-t | --no-title] [-d | --debug] [-v | --version]
    [-y | --service-type-id] [-s | --long] [-D | --context]
    [-u | --host-username] [-a | --no-auth] [-p | --host-password]
    Error:
    On error, it prints <STATUS CODE>::<ERROR CODE>::<ERROR MESSAGE>
    For example:
    "oclip service-type-create -x {} -m {} -u {} -p {}".format( parameters["service_name"], \
      parameters["aai_url"], parameters["aai_username"], parameters["aai_password"])

2. create-customer
------------------

::

    usage: oclip customer-create
    Create a customer in Onap
    Product: onap-dublin Service: aai Author: ONAP CLI Team onap-discuss@lists.onap.org
    Options:
    [-m | --host-url] [-y | --subscriber-name] [-C | --no-catalog]
    [-f | --format] [-h | --help] [-V | --verify]
    [-t | --no-title] [-d | --debug] [-v | --version]
    [-x | --customer-name] [-s | --long] [-D | --context]
    [-u | --host-username] [-a | --no-auth] [-p | --host-password]
    Error:
    On error, it prints <STATUS CODE>::<ERROR CODE>::<ERROR MESSAGE>
    For example:
    "oclip customer-create -x {} -y {} -m {} -u {} -p {}".format( parameters["customer_name"], \
    parameters["subscriber_name"], parameters["aai_url"], parameters["aai_username"], parameters["aai_password"])


3. add-customer-subscription(subscription not exist)
----------------------------------------------------

::

    usage: oclip customer-create
    Create a customer in Onap
    Product: onap-dublin Service: aai Author: ONAP CLI Team onap-discuss@lists.onap.org
    Options:
    [-m | --host-url] [-y | --subscriber-name] [-C | --no-catalog]
    [-f | --format] [-h | --help] [-V | --verify]
    [-t | --no-title] [-d | --debug] [-v | --version]
    [-x | --customer-name] [-s | --long] [-D | --context]
    [-u | --host-username] [-a | --no-auth] [-p | --host-password]
    Error:
    On error, it prints <STATUS CODE>::<ERROR CODE>::<ERROR MESSAGE>
    For example:
    "oclip subscription-create -x {} -c {} -z {} -e {} -y {} -r {} -m {} -u {} -p {}".format(\
          parameters["customer_name"], cloud_region_values.get("tenant-id"), parameters["cloud-owner"], parameters["service_name"],\
          cloud_region_values.get("default-tenant"), cloud_region, parameters["aai_url"], parameters["aai_username"], parameters["aai_password"] )

4. add-customer-subscription(subscription existed)
--------------------------------------------------

::

    usage: oclip subscription-cloud-add
    Add a new cloud region to a customer subscription
    Product: onap-dublin Service: aai Author: Intel ONAP HPA integration team (itohan.ukponmwan@intel.com)
    Options:
    [-m | --host-url] [-C | --no-catalog] [-f | --format]
    [-h | --help] [-V | --verify] [-t | --no-title]
    [-d | --debug] [-v | --version] [-x | --customer-name]
    [-c | --cloud-tenant-id] [-s | --long] [-D | --context]
    [-z | --cloud-owner] [-e | --service-type] [-u | --host-username]
    [-a | --no-auth] [-y | --tenant-name] [-r | --cloud-region]
    [-p | --host-password]
    Error:
    On error, it prints <STATUS CODE>::<ERROR CODE>::<ERROR MESSAGE>
    For example:
    "oclip subscription-cloud-add -x {} -c {} -z {} -e {} -y {} -r {} -m {} -u {} -p {}".format(\
          parameters["customer_name"], cloud_region_values.get("tenant-id"), parameters["cloud-owner"], parameters["service_name"],\
          cloud_region_values.get("default-tenant"), cloud_region, parameters["aai_url"], parameters["aai_username"], parameters["aai_password"] )
