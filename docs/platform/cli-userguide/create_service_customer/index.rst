Cli Create Service and Customer Command Guide
=============================================

1. create-service-type
-----------------------

::

    usage: oclip service-type-create
    Add a service type in Onap
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

5. service type list
--------------------

::

    usage: oclip service-type-list
    List the service types configured in Onap
    Options:
    [-m | --host-url] [-C | --no-catalog] [-f | --format]
    [-h | --help] [-V | --verify] [-t | --no-title]
    [-d | --debug] [-v | --version] [-s | --long]
    [-D | --context] [-u | --host-username] [-a | --no-auth]
    [-p | --host-password]
    For example:
    "oclip service-type-list -m {} -u {} -p {}".format(parameters["aai_url"], parameters["aai_username"], \
                          parameters["aai_password"])

6. service type delete
----------------------

::

    usage: oclip service-type-delete
    usage: oclip service-type-delete
    Delete a service type from Onap
    Options:
    [-m | --host-url] [-C | --no-catalog] [-f | --format]
    [-h | --help] [-V | --verify] [-t | --no-title]
    [-d | --debug] [-v | --version] [-y | --resource-version]
    [-x | --service-type-id] [-s | --long] [-D | --context]
    [-u | --host-username] [-a | --no-auth] [-p | --host-password]
    For example:
    oclip service-type-delete -m https://159.138.61.203:30233 -u AAI -p AAI -x baf23ae9-f890-4b92-b568-2a70f5c86993 -y 1568444204387
    Note:
    service-type-id and resource-version is the result returned after executing the service-type-list command(command 5)

7. customer list
----------------

::

    usage: oclip customer-list
    Lists the registered customers in Onap
    Options:
    [-m | --host-url] [-C | --no-catalog] [-f | --format]
    [-h | --help] [-V | --verify] [-t | --no-title]
    [-d | --debug] [-v | --version] [-s | --long]
    [-D | --context] [-u | --host-username] [-a | --no-auth]
    [-p | --host-password]
    For example:
    oclip customer-list -m {} -u {} -p {}".format(parameters["aai_url"], parameters["aai_username"], \
                          parameters["aai_password"])

8. customer delete
------------------

::

    usage: oclip customer-delete
    Delete a customer from Onap
    Options:
    [-m | --host-url] [-C | --no-catalog] [-f | --format]
    [-h | --help] [-V | --verify] [-t | --no-title]
    [-d | --debug] [-v | --version] [-y | --resource-version]
    [-s | --long] [-D | --context] [-x | --customer-id]
    [-u | --host-username] [-a | --no-auth] [-p | --host-password]
    For example:
    oclip customer-delete -m https://159.138.61.203:30233 -u AAI -p AAI -x customer2 -y 1568615567019
 Note:
    customer-id and resource-version is the result returned after executing the customer-list command(command 7)
