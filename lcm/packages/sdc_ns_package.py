# Copyright 2016 ZTE Corporation.
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

from lcm.pub.database.models import NSDModel, NSInstModel
from lcm.pub.utils.values import ignore_case_get
from lcm.pub.exceptions import NSLCMException
from lcm.pub.msapi import sdc

logger = logging.getLogger(__name__)

STATUS_SUCCESS, STATUS_FAILED = "success", "failed"


def fmt_ns_pkg_rsp(status, desc, error_code="500"):
    return [0, {"status": status, "statusDescription": desc, "errorCode": error_code}]


def ns_common_call(fun, csar_id, operation=""):
    ret = None
    try:
        if operation == "":
            ret = fun(csar_id)
        else:
            ret = fun(csar_id, operation)

        if ret[0] != 0:
            return fmt_ns_pkg_rsp(STATUS_FAILED, ret[1])
    except NSLCMException as e:
        return fmt_ns_pkg_rsp(STATUS_FAILED, e.message)
    except:
        logger.error(traceback.format_exc())
        return fmt_ns_pkg_rsp(STATUS_FAILED, str(sys.exc_info()))
    return fmt_ns_pkg_rsp(STATUS_SUCCESS, ret[1], "")

def ns_on_distribute(csar_id):
    return ns_common_call(SdcNsPackage().on_distribute, csar_id)


def ns_delete_csar(csar_id):
    return ns_common_call(SdcNsPackage().delete_csar, csar_id)


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
        download_artifacts(artifact["toscaModelURL"], "TODO:Local Path")

        NSDModel(
            id=csar_id,
            nsd_id="TODO",
            name="TODO",
            vendor="TODO",
            description="TODO",
            version="TODO",
            nsd_model="TODO",
            nsd_path="TODO").save()

    def delete_csar(self, csar_id, force_delete):
        if force_delete:
            NSInstModel.objects.filter(nspackage_id=csar_id).delete()
        else:
            if NSInstModel.objects.filter(nspackage_id=csar_id):
                raise NSLCMException("CSAR(%s) is in using, cannot be deleted." % csar_id)
        NSDModel.objects.filter(id=csar_id).delete()


    def get_csars(self):
        ret = {"csars": []}
        nss = NSDModel.objects.filter()
        for ns in nss:
            ret["csars"].append({
                "csarId": ns.id,
                "nsdId": ns.nsd_id
            })
        return ret

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


       