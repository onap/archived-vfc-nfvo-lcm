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
import uuid
import os
import time
import threading
import traceback
import sys

from lcm.pub.database.models import NfPackageModel, NfInstModel
from lcm.pub.utils.values import ignore_case_get
from lcm.pub.utils import fileutil
from lcm.pub.exceptions import NSLCMException
from lcm.pub.config.config import CATALOG_ROOT_PATH
from lcm.pub.msapi.extsys import get_vims
from lcm.pub.utils.jobutil import JobUtil
from lcm.pub.utils import toscaparser
from lcm.pub.msapi import sdc

logger = logging.getLogger(__name__)

JOB_ERROR = 255

def nf_get_csars():
    ret = None
    try:
        ret = SdcNfPackage().get_csars()
    except NSLCMException as e:
        return [1, e.message]
    except:
        logger.error(traceback.format_exc())
        return [1, str(sys.exc_info())]
    return ret

def nf_get_csar(csar_id):
    ret = None
    try:
        ret = SdcNfPackage().get_csar(csar_id)
    except NSLCMException as e:
        return [1, e.message]
    except:
        logger.error(traceback.format_exc())
        return [1, str(sys.exc_info())]
    return ret

#####################################################################################

class SdcNfDistributeThread(threading.Thread):
    """
    Sdc NF Package Distribute
    """

    def __init__(self, csar_id, vim_ids, lab_vim_id, job_id):
        threading.Thread.__init__(self)
        self.csar_id = csar_id
        self.vim_ids = vim_ids
        self.lab_vim_id = lab_vim_id
        self.job_id = job_id

        self.csar_save_path = os.path.join(CATALOG_ROOT_PATH, csar_id)

    def run(self):
        try:
            self.on_distribute()
        except NSLCMException as e:
            self.rollback_distribute()
            JobUtil.add_job_status(self.job_id, JOB_ERROR, e.message)
        except:
            logger.error(traceback.format_exc())
            logger.error(str(sys.exc_info()))
            self.rollback_distribute()
            JobUtil.add_job_status(self.job_id, JOB_ERROR, "Failed to distribute CSAR(%s)" % self.csar_id)

    def on_distribute(self):
        JobUtil.create_job(
            inst_type='nf',
            jobaction='on_distribute',
            inst_id=self.csar_id,
            job_id=self.job_id)
        JobUtil.add_job_status(self.job_id, 5, "Start CSAR(%s) distribute." % self.csar_id)

        if NfPackageModel.objects.filter(nfpackageid=self.csar_id):
            raise NSLCMException("NF CSAR(%s) already exists." % self.csar_id)

        artifact = sdc.get_artifact(sdc.ASSETTYPE_RESOURCES, self.csar_id)
        local_path = os.path.join(CATALOG_ROOT_PATH, self.csar_id)
        local_file_name = sdc.download_artifacts(artifact["toscaModelURL"], 
            local_path, "%s.csar" % artifact.get("name", self.csar_id))
        
        vnfd_json = toscaparser.parse_vnfd(local_file_name)
        vnfd = json.JSONDecoder().decode(vnfd_json)

        nfd_id = vnfd["metadata"]["id"]
        if NfPackageModel.objects.filter(vnfdid=nfd_id):
            raise NSLCMException("NFD(%s) already exists." % nfd_id)

        JobUtil.add_job_status(self.job_id, 30, "Save CSAR(%s) to database." % self.csar_id)

        vnfd_ver = vnfd["metadata"].get("vnfd_version")
        if not vnfd_ver:
            vnfd_ver = vnfd["metadata"].get("vnfdVersion", "undefined")
        NfPackageModel(
            uuid=self.csar_id,
            nfpackageid=self.csar_id,
            vnfdid=nfd_id,
            vendor=vnfd["metadata"].get("vendor", "undefined"),
            vnfdversion=vnfd_ver,
            vnfversion=vnfd["metadata"].get("version", "undefined"),
            vnfdmodel=vnfd_json,
            vnfd_path=local_file_name
            ).save()

        JobUtil.add_job_status(self.job_id, 100, "CSAR(%s) distribute successfully." % self.csar_id)


    def rollback_distribute(self):
        try:
            NfPackageModel.objects.filter(nfpackageid=self.csar_id).delete()
            fileutil.delete_dirs(self.csar_save_path)
        except:
            logger.error(traceback.format_exc())
            logger.error(str(sys.exc_info()))


######################################################################################################################


class SdcNfPkgDeleteThread(threading.Thread):
    """
    Sdc NF Package Deleting
    """

    def __init__(self, csar_id, job_id, force_delete):
        threading.Thread.__init__(self)
        self.csar_id = csar_id
        self.job_id = job_id
        self.force_delete = force_delete

    def run(self):
        try:
            self.delete_csar()
        except NSLCMException as e:
            JobUtil.add_job_status(self.job_id, JOB_ERROR, e.message)
        except:
            logger.error(traceback.format_exc())
            logger.error(str(sys.exc_info()))
            JobUtil.add_job_status(self.job_id, JOB_ERROR, "Failed to delete CSAR(%s)" % self.csar_id)

    def delete_csar(self):
        JobUtil.create_job(
            inst_type='nf',
            jobaction='delete',
            inst_id=self.csar_id,
            job_id=self.job_id)
        JobUtil.add_job_status(self.job_id, 5, "Start to delete CSAR(%s)." % self.csar_id)

        if self.force_delete:
            NfInstModel.objects.filter(package_id=self.csar_id).delete()
        else:
            if NfInstModel.objects.filter(package_id=self.csar_id):
                raise NSLCMException("NfInst by csar(%s) exists, cannot delete." % self.csar_id)

        JobUtil.add_job_status(self.job_id, 50, "Delete CSAR(%s) from Database." % self.csar_id)

        NfPackageModel.objects.filter(nfpackageid=self.csar_id).delete()

        JobUtil.add_job_status(self.job_id, 80, "Delete local CSAR(%s) file." % self.csar_id)

        csar_save_path = os.path.join(CATALOG_ROOT_PATH, self.csar_id)
        fileutil.delete_dirs(csar_save_path)

        JobUtil.add_job_status(self.job_id, 100, "Delete CSAR(%s) successfully." % self.csar_id)


######################################################################################################################

class SdcNfPackage(object):
    """
    Actions for sdc nf package.
    """

    def __init__(self):
        pass

    def get_csars(self):
        csars = {"csars": []}
        nf_pkgs = NfPackageModel.objects.filter()
        for nf_pkg in nf_pkgs:
            csars["csars"].append({
                "csarId": nf_pkg.nfpackageid,
                "vnfdId": nf_pkg.vnfdid
            })
        return [0, csars]
        
    def get_csar(self, csar_id):
        pkg_info = {}
        nf_pkg = NfPackageModel.objects.filter(nfpackageid=csar_id)
        if nf_pkg:
            pkg_info["vnfdId"] = nf_pkg[0].vnfdid
            pkg_info["vnfdProvider"] = nf_pkg[0].vendor
            pkg_info["vnfdVersion"] = nf_pkg[0].vnfdversion
            pkg_info["vnfVersion"] = nf_pkg[0].vnfversion


        vnf_insts = NfInstModel.objects.filter(package_id=csar_id)
        vnf_inst_info = [{"vnfInstanceId": vnf_inst.nfinstid,
                          "vnfInstanceName": vnf_inst.nf_name} for vnf_inst in vnf_insts]

        return [0, {"csarId": csar_id,
                    "packageInfo": pkg_info,
                    "imageInfo": [],
                    "vnfInstanceInfo": vnf_inst_info}]


        
