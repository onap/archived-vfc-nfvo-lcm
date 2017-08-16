# Copyright 2017 ZTE Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import logging

import traceback
import sys
import os

from lcm.pub.database.models import NSDModel, NSInstModel, NfPackageModel
from lcm.pub.utils.values import ignore_case_get
from lcm.pub.exceptions import NSLCMException
from lcm.pub.msapi import sdc
from lcm.pub.config.config import CATALOG_ROOT_PATH
from lcm.pub.utils import toscaparser
from lcm.pub.utils import fileutil

logger = logging.getLogger(__name__)

STATUS_SUCCESS, STATUS_FAILED = "success", "failed"


def fmt_ns_pkg_rsp(status, desc, error_code="500"):
    return [0, {"status": status, "statusDescription": desc, "errorCode": error_code}]


def ns_on_distribute(csar_id):
    ret = None
    try:
        ret = SdcNsPackage().on_distribute(csar_id)
    except NSLCMException as e:
        SdcNsPackage().delete_catalog(csar_id)
        return fmt_ns_pkg_rsp(STATUS_FAILED, e.message)
    except:
        logger.error(traceback.format_exc())
        SdcNsPackage().delete_catalog(csar_id)
        return fmt_ns_pkg_rsp(STATUS_FAILED, str(sys.exc_info()))
    return fmt_ns_pkg_rsp(STATUS_SUCCESS, ret[1], "")


def ns_delete_csar(csar_id, force_delete):
    ret = None
    try:
        ret = SdcNsPackage().delete_csar(csar_id, force_delete)
    except NSLCMException as e:
        return fmt_ns_pkg_rsp(STATUS_FAILED, e.message)
    except:
        logger.error(traceback.format_exc())
        return fmt_ns_pkg_rsp(STATUS_FAILED, str(sys.exc_info()))
    return fmt_ns_pkg_rsp(STATUS_SUCCESS, ret[1], "")

def ns_get_csars():
    ret = None
    try:
        ret = SdcNsPackage().get_csars()
    except NSLCMException as e:
        return [1, e.message]
    except:
        logger.error(traceback.format_exc())
        return [1, str(sys.exc_info())]
    return ret

def ns_get_csar(csar_id):
    ret = None
    try:
        ret = SdcNsPackage().get_csar(csar_id)
    except NSLCMException as e:
        return [1, e.message]
    except:
        logger.error(traceback.format_exc())
        return [1, str(sys.exc_info())]
    return ret


###############################################################################################################

class SdcNsPackage(object):
    """
    Actions for sdc ns package.
    """

    def __init__(self):
        pass

    def on_distribute(self, csar_id):
        if NSDModel.objects.filter(id=csar_id):
            raise NSLCMException("NS CSAR(%s) already exists." % csar_id)

        artifact = sdc.get_artifact(sdc.ASSETTYPE_SERVICES, csar_id)
        local_path = os.path.join(CATALOG_ROOT_PATH, csar_id)
        local_file_name = sdc.download_artifacts(artifact["toscaModelURL"], local_path)
        
        nsd_json = toscaparser.parse_nsd(local_file_name)
        nsd = json.JSONDecoder().decode(nsd_json)

        nsd_id = nsd["metadata"]["id"]
        if NSDModel.objects.filter(nsd_id=nsd_id):
            raise NSLCMException("NSD(%s) already exists." % nsd_id)

        for vnf in nsd["vnfs"]:
            vnfd_id = vnf["properties"]["id"]
            pkg = NfPackageModel.objects.filter(vnfdid=vnfd_id)
            if not pkg:
                raise NSLCMException("VNF package(%s) is not distributed." % vnfd_id)

        NSDModel(
            id=csar_id,
            nsd_id=nsd_id,
            name=nsd["metadata"].get("name", nsd_id),
            vendor=nsd["metadata"].get("vendor", "undefined"),
            description=nsd["metadata"].get("description", ""),
            version=nsd["metadata"].get("version", "undefined"),
            nsd_path=local_file_name,
            nsd_model=nsd_json).save()

        return [0, "CSAR(%s) distributed successfully." % csar_id]


    def delete_csar(self, csar_id, force_delete):
        if force_delete:
            NSInstModel.objects.filter(nspackage_id=csar_id).delete()
        else:
            if NSInstModel.objects.filter(nspackage_id=csar_id):
                raise NSLCMException("CSAR(%s) is in using, cannot be deleted." % csar_id)
        NSDModel.objects.filter(id=csar_id).delete()


    def get_csars(self):
        csars = {"csars": []}
        nss = NSDModel.objects.filter()
        for ns in nss:
            csars["csars"].append({
                "csarId": ns.id,
                "nsdId": ns.nsd_id
            })
        return [0, csars]

    def get_csar(self, csar_id):
        package_info = {}
        csars = NSDModel.objects.filter(id=csar_id)
        if csars:
            package_info["nsdId"] = csars[0].nsd_id
            package_info["nsdProvider"] = csars[0].vendor
            package_info["nsdVersion"] = csars[0].version

        nss = NSInstModel.objects.filter(nspackage_id=csar_id)
        ns_instance_info = [{
            "nsInstanceId": ns.id, 
            "nsInstanceName": ns.name} for ns in nss]

        return [0, {"csarId": csar_id, 
            "packageInfo": package_info, 
            "nsInstanceInfo": ns_instance_info}]

    def delete_catalog(self, csar_id):
        local_path = os.path.join(CATALOG_ROOT_PATH, csar_id)
        fileutil.delete_dirs(local_path)



       