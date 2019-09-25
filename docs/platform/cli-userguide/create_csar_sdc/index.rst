Cli Create Csar Command Guide
===============================

1. create-vlm
---------------

::

    usage: oclip vlm-create
    Create License Model
    Product: onap-dublin Service: sdc Author: ONAP CLI Team onap-discuss@lists.onap.org
    Options:
    [-m | --host-url] [-C | --no-catalog] [-f | --format]
    [-h | --help] [-V | --verify] [-t | --no-title]
    [-d | --debug] [-v | --version] [-y | --description]
    [-s | --long] [-D | --context] [-x | --vendor-name]
    [-u | --host-username] [-a | --no-auth] [-p | --host-password]
    Error:
    On error, it prints <STATUS CODE>::<ERROR CODE>::<ERROR MESSAGE>
    For example:
    "oclip vlm-create -x {} -u {} -p {} -m {}".format(parameters["vendor-name"], \
      parameters["sdc_creator"], parameters["sdc_password"], parameters["sdc_onboarding_url"])

2. create-vsp
---------------

::

    usage: oclip vsp-create
    Create Vendor Software Product
    Product: onap-dublin Service: sdc Author: ONAP CLI Team onap-discuss@lists.onap.org
    Options:
    [-m | --host-url] [-j | --vlm-feature-group-id] [-C | --no-catalog]
    [-f | --format] [-h | --help] [-V | --verify]
    [-t | --no-title] [-d | --debug] [-v | --version]
    [-o | --onboarding-method] [-e | --vlm-vendor] [-x | --vsp-name]
    [-y | --vsp-description] [-s | --long] [-D | --context]
    [-i | --vlm-agreement-id] [-c | --vlm-version] [-u | --host-username]
    [-a | --no-auth] [-g | --vlm-id] [-p | --host-password]
    Error:
    On error, it prints <STATUS CODE>::<ERROR CODE>::<ERROR MESSAGE>
    For example:
    "oclip vsp-create -j {} -o {} -e {} -x {} -y {} -i {} -c {} -g {} -u {} -p {} -m {}".format( in_list[0], \
          parameters["onboarding-method"], parameters["vendor-name" ], value.get("vsp-name"), value.get("vsp-desc"), in_list[1], \
          in_list[2], in_list[3], parameters["sdc_creator"], parameters["sdc_password"], parameters["sdc_onboarding_url"] )


3. create-vf-model
------------------

::

    usage: oclip vf-model-create
    Create Virtual function from Vendor Software Product
    Product: onap-dublin Service: sdc Author: ONAP HPA Team onap-discuss@lists.onap.org
    Options:
    [-m | --host-url] [-C | --no-catalog] [-f | --format]
    [-h | --help] [-V | --verify] [-t | --no-title]
    [-d | --debug] [-v | --version] [-y | --description]
    [-g | --vsp-version] [-x | --name] [-s | --long]
    [-D | --context] [-z | --vendor-name] [-u | --host-username]
    [-a | --no-auth] [-b | --vsp-id] [-p | --host-password]
    Error:
    On error, it prints <STATUS CODE>::<ERROR CODE>::<ERROR MESSAGE>
    For example:
    "oclip vf-model-create -y {} -g {} -x {} -z {} -b {} -u {} -p {} -m {}".format(value.get("vf-description"), \
          value.get("vsp-version"), value.get("vf-name"), parameters["vendor-name"], vsp_dict[name], \
          parameters["sdc_creator"], parameters["sdc_password"], parameters["sdc_catalog_url"])

4. create-service-model
-----------------------

::

    usage: oclip service-model-create
    Create Service model in SDC
    Product: onap-dublin Service: sdc Author: ONAP HPA Team onap-discuss@lists.onap.org
    Options:
    [-m | --host-url] [-C | --no-catalog] [-f | --format]
    [-h | --help] [-V | --verify] [-t | --no-title]
    [-d | --debug] [-v | --version] [-z | --project-code]
    [-y | --description] [-e | --icon-id] [-c | --category-display-name]
    [-s | --long] [-D | --context] [-x | --service-name]
    [-u | --host-username] [-a | --no-auth] [-b | --category]
    [-p | --host-password]
    Error:
    On error, it prints <STATUS CODE>::<ERROR CODE>::<ERROR MESSAGE>
    For example:
    "oclip service-model-create -z {} -y {} -e {} -x {} -c {} -b {} -u {} -p {} -m {} |grep ID".format(parameters["project-code"], \
    parameters["service-model-desc"], parameters["icon-id"], parameters["service-model-name"], parameters["category-display"], \
    parameters["category"],parameters["sdc_creator"], parameters["sdc_password"], parameters["sdc_catalog_url"])

5. vfc-catalog-onboard-vnf
--------------------------

::

    usage: oclip vfc-catalog-onboard-vnf
    vfc onboard vnf to catalog of vfc
    Product: onap-dublin Service: vfc Author: ONAP HPA Integration Team (haibin.huang@intel.com)
    Options:
    [-m | --host-url] [-C | --no-catalog] [-f | --format]
    [-h | --help] [-V | --verify] [-t | --no-title]
    [-d | --debug] [-v | --version] [-s | --long]
    [-D | --context] [-c | --vnf-csar-uuid]
    Error:
    On error, it prints <STATUS CODE>::<ERROR CODE>::<ERROR MESSAGE>
    For example:
    oclip vfc-catalog-onboard-vnf - -c {}'.format(value.get("csar-id"))


6. vfc-catalog-onboard-ns
--------------------------

::

    usage: oclip vfc-catalog-onboard-ns
    vfc onboard ns to catalog of vfc
    Product: onap-dublin Service: vfc Author: ONAP HPA Integration Team (haibin.huang@intel.com)
    Options:
    [-m | --host-url] [-c | --ns-csar-uuid] [-C | --no-catalog]
    [-f | --format] [-h | --help] [-V | --verify]
    [-t | --no-title] [-d | --debug] [-v | --version]
    [-s | --long] [-D | --context]
    Error:
    On error, it prints <STATUS CODE>::<ERROR CODE>::<ERROR MESSAGE>
    For example:
    'oclip vfc-catalog-onboard-ns -c {}'.format(parameters["ns"]["csar-id"])


