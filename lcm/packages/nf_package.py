# Copyright 2016-2017 ZTE Corporation.
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

from lcm.pub.database.models import NfPackageModel, VnfPackageFileModel, NfInstModel
from lcm.pub.utils.values import ignore_case_get
from lcm.pub.utils import fileutil
from lcm.pub.msapi.catalog import STATUS_ONBOARDED, P_STATUS_ENABLED
from lcm.pub.msapi.catalog import P_STATUS_DELETEFAILED, P_STATUS_DELETING
from lcm.pub.msapi.catalog import P_STATUS_NORMAL, P_STATUS_ONBOARDING, P_STATUS_ONBOARDFAILED
from lcm.pub.msapi.catalog import query_csar_from_catalog, set_csar_state
from lcm.pub.msapi.catalog import query_rawdata_from_catalog, delete_csar_from_catalog
from lcm.pub.msapi.catalog import get_download_url_from_catalog
from lcm.pub.exceptions import NSLCMException
from lcm.pub.msapi.extsys import get_vims
from lcm.pub.config.config import IMAGE_ROOT_PATH, IGNORE_DEL_IMG_WEHN_DEL_CSAR
from lcm.pub.nfvi.vim.vimadaptor import VimAdaptor
from lcm.pub.nfvi.vim import const
from lcm.pub.utils.jobutil import JobUtil
from lcm.pub.utils import toscautil

logger = logging.getLogger(__name__)

SUPPORT_MULTI_VIM, UNSUPPORT_MULTI_VIM = 1, 0
ZTE_PRIVATE = 0
DEPLOY_TYPE_IAAS = 1
IMAGE_FILE = 2
IMAGE_STATUS_ENABLE = "Enable"
MAX_RETRY_TIMES = 300
SLEEP_INTERVAL_SECONDS = 2
IMAGE_ACTIVE = 'active'
JOB_ERROR = 255


class NfOnBoardingThread(threading.Thread):
    """
    NF package onBoarding
    """

    def __init__(self, csar_id, vim_ids, lab_vim_id, job_id):
        threading.Thread.__init__(self)
        self.csar_id = csar_id
        self.vim_ids = vim_ids
        self.lab_vim_id = lab_vim_id
        self.job_id = job_id

        self.csar_info = None
        self.nfd = None
        self.nfd_id = None
        self.img_save_path = os.path.join(IMAGE_ROOT_PATH, self.job_id)

        self.need_rollback_when_failed = False

    def run(self):
        try:
            self.on_boarding()
        except NSLCMException as e:
            self.rollback_on_boarding()
            JobUtil.add_job_status(self.job_id, JOB_ERROR, e.message)
        except:
            logger.error(traceback.format_exc())
            logger.error(str(sys.exc_info()))
            self.rollback_on_boarding()
            JobUtil.add_job_status(self.job_id, JOB_ERROR, "Failed to onBoarding CSAR(%s)" % self.csar_id)

    def on_boarding(self):
        JobUtil.create_job(
            inst_type='nf',
            jobaction='on_boarding',
            inst_id=self.csar_id,
            job_id=self.job_id)
        JobUtil.add_job_status(self.job_id, 5, "Start CSAR(%s) onBoarding." % self.csar_id)
        self.on_boarding_pre_deal()
        self.nf_package_save()
        self.need_rollback_when_failed = True
        nf_images = self.download_nf_images()
        self.upload_nf_images(nf_images)
        set_csar_state(self.csar_id, "onBoardState", STATUS_ONBOARDED)
        set_csar_state(self.csar_id, "processState", P_STATUS_NORMAL)
        set_csar_state(self.csar_id, "operationalState", P_STATUS_ENABLED)
        JobUtil.add_job_status(self.job_id, 100, "CSAR(%s) onBoarding successfully." % self.csar_id)

    def on_boarding_pre_deal(self):
        JobUtil.add_job_status(self.job_id, 10, "Check status of CSAR(%s) from catalog." % self.csar_id)

        self.csar_info = query_csar_from_catalog(self.csar_id)

        on_board_state = ignore_case_get(self.csar_info, "onBoardState")
        if on_board_state == STATUS_ONBOARDED:
            raise NSLCMException("CSAR(%s) already onBoarded." % self.csar_id)

        process_state = ignore_case_get(self.csar_info, "processState")
        if process_state == P_STATUS_ONBOARDING:
            raise NSLCMException("CSAR(%s) is onBoarding now." % self.csar_id)

        JobUtil.add_job_status(self.job_id, 20, "Get model of CSAR(%s) from catalog." % self.csar_id)

        raw_data = query_rawdata_from_catalog(self.csar_id)
        self.nfd = toscautil.convert_vnfd_model(raw_data["rawData"]) # convert to inner json
        self.nfd = json.JSONDecoder().decode(self.nfd)
        self.nfd_id = self.nfd["metadata"]["id"]
        if NfPackageModel.objects.filter(vnfdid=self.nfd_id):
            raise NSLCMException("NFD(%s) already exists." % self.nfd_id)

    def nf_package_save(self):
        JobUtil.add_job_status(self.job_id, 30, "Save CSAR(%s) to database." % self.csar_id)
        vnfd_ver = self.nfd["metadata"].get("vnfd_version")
        if not vnfd_ver:
            vnfd_ver = self.nfd["metadata"].get("vnfdVersion")
        NfPackageModel(
            uuid=str(uuid.uuid4()),
            nfpackageid=self.csar_id,
            vnfdid=self.nfd_id,
            vendor=self.nfd["metadata"].get("vendor", "undefined"),
            vnfdversion=vnfd_ver,
            vnfversion=self.nfd["metadata"].get("version", "undefined"),
            vnfdmodel=json.JSONEncoder().encode(self.nfd)
            ).save()

    def download_nf_images(self):
        nf_images = []
        for image_file in self.nfd["image_files"]:
            img_name = image_file["properties"]["name"]
            img_relative_path = image_file["properties"]["file_url"]
            img_type = image_file["properties"]["disk_format"]
            img_desc = image_file.get("description", "")
            img_url, img_local_path = get_download_url_from_catalog(self.csar_id, img_relative_path)
            JobUtil.add_job_status(self.job_id, 50, "Start to download Image(%s)." % img_name)
            is_download_ok, img_save_full_path = fileutil.download_file_from_http(img_url, 
                self.img_save_path, img_name)
            if not is_download_ok:
                raise NSLCMException("Failed to download image from %s" % img_url)
            logger.debug("Download Image(%s) to %s successfully.", img_name, img_save_full_path)
            nf_images.append({
                "image_url": img_url,
                "img_name": img_name,
                "img_save_full_path": img_save_full_path,
                "img_type": img_type,
                "img_desc": img_desc})
        return nf_images

    def upload_nf_images(self, nf_images):
        vims = get_vims()
        if self.lab_vim_id and (not self.vim_ids):
            self.vim_ids = [self.lab_vim_id]
        for vim_id in self.vim_ids:
            sel_vim = [vim for vim in vims if vim["vimId"] == vim_id]
            if not sel_vim:
                logger.warn("VIMID(%s) does not exist.", vim_id)
                continue
            vim_api = VimAdaptor({
                "vimid": vim_id,
                "vimtype": sel_vim[0]["type"],
                "url": sel_vim[0]["url"],
                "user": sel_vim[0]["userName"],
                "passwd": sel_vim[0]["password"],
                "tenant": sel_vim[0]["tenant"]})
            for nf_image in nf_images:
                self.upload_one_nf_image(vim_api, nf_image, vim_id, sel_vim)
        fileutil.delete_dirs(self.img_save_path)

    def upload_one_nf_image(self, vim_api, nf_image, vim_id, sel_vim):
        JobUtil.add_job_status(self.job_id, 80, "Start to upload Image(%s) to VIM(%s)." %
                               (nf_image["img_name"], vim_id))
        ret = vim_api.create_image({
            "image_url": nf_image["image_url"],
            "image_name": nf_image["img_name"],
            "image_path": nf_image["img_save_full_path"],
            "image_type": nf_image["img_type"]})
        if ret[0] != 0:
            raise NSLCMException("Failed to create image:%s" % ret[1])
        image_id = ret[1]["id"]

        self.wait_until_upload_done(vim_api, image_id)

        VnfPackageFileModel(
            vnfpid=self.csar_id,
            filename=nf_image["img_name"],
            filetype=IMAGE_FILE,
            imageid=image_id,
            vimid=vim_id,
            vimuser=sel_vim[0]["userName"],
            tenant=sel_vim[0]["tenant"],
            purpose=nf_image["img_desc"],
            status=IMAGE_STATUS_ENABLE).save()

    def wait_until_upload_done(self, vim_api, image_id):
        retry_times = 0
        image_create_success = False

        while retry_times < MAX_RETRY_TIMES:
            retry_times += 1
            ret = vim_api.get_image(image_id=image_id)
            if ret[0] != 0:
                logging.warn("Failed to query image:%s", ret[1])
                continue
            if ret[1]["status"] == IMAGE_ACTIVE:
                image_create_success = True
                break
            time.sleep(SLEEP_INTERVAL_SECONDS)

        if not image_create_success:
            timeout_seconds = MAX_RETRY_TIMES * SLEEP_INTERVAL_SECONDS
            raise NSLCMException("Failed to create image:timeout(%s seconds.)" % timeout_seconds)

    def rollback_on_boarding(self):
        if not self.need_rollback_when_failed:
            return
        try:
            set_csar_state(self.csar_id, "processState", P_STATUS_ONBOARDFAILED)
            NfPackageModel.objects.filter(nfpackageid=self.csar_id).delete()
            VnfPackageFileModel.objects.filter(vnfpid=self.csar_id).delete()
            fileutil.delete_dirs(self.img_save_path)
        except:
            logger.error(traceback.format_exc())
            logger.error(str(sys.exc_info()))


######################################################################################################################


class NfPkgDeleteThread(threading.Thread):
    """
    NF Package Deleting
    """

    def __init__(self, csar_id, job_id):
        threading.Thread.__init__(self)
        self.csar_id = csar_id
        self.job_id = job_id

    def run(self):
        try:
            self.delete_csar()
        except NSLCMException as e:
            set_csar_state(self.csar_id, "processState", P_STATUS_DELETEFAILED)
            JobUtil.add_job_status(self.job_id, JOB_ERROR, e.message)
        except:
            logger.error(traceback.format_exc())
            logger.error(str(sys.exc_info()))
            set_csar_state(self.csar_id, "processState", P_STATUS_DELETEFAILED)
            JobUtil.add_job_status(self.job_id, JOB_ERROR, "Failed to delete CSAR(%s)" % self.csar_id)

    def delete_csar(self):
        JobUtil.create_job(
            inst_type='nf',
            jobaction='delete',
            inst_id=self.csar_id,
            job_id=self.job_id)
        JobUtil.add_job_status(self.job_id, 5, "Start to delete CSAR(%s)." % self.csar_id)
        if query_csar_from_catalog(self.csar_id, "processState") == P_STATUS_DELETING:
            JobUtil.add_job_status(self.job_id, 100, "CSAR(%s) is deleting now." % self.csar_id)
            return

        if NfInstModel.objects.filter(package_id=self.csar_id):
            ret = set_csar_state(self.csar_id, "deletionPending", True)
            JobUtil.add_job_status(self.job_id, 100, ret[1])
            return

        NfPackage().delete_csar(self.csar_id, self.job_id)


class NfPkgDeletePendingThread(threading.Thread):
    """
    NF Package Delete Pending
    """

    def __init__(self, csar_id, job_id):
        threading.Thread.__init__(self)
        self.csar_id = csar_id
        self.job_id = job_id

    def run(self):
        try:
            self.delete_pending_csar()
        except NSLCMException as e:
            set_csar_state(self.csar_id, "processState", P_STATUS_DELETEFAILED)
            JobUtil.add_job_status(self.job_id, JOB_ERROR, e.message)
        except:
            logger.error(traceback.format_exc())
            logger.error(str(sys.exc_info()))
            set_csar_state(self.csar_id, "processState", P_STATUS_DELETEFAILED)
            JobUtil.add_job_status(self.job_id, JOB_ERROR, "Failed to delete CSAR(%s)" % self.csar_id)

    def delete_pending_csar(self):
        JobUtil.create_job(
            inst_type='nf',
            jobaction='delete_pending',
            inst_id=self.csar_id,
            job_id=self.job_id)
        JobUtil.add_job_status(self.job_id, 5, "Start to delete pending CSAR(%s)." % self.csar_id)

        if not NfPackageModel.objects.filter(nfpackageid=self.csar_id):
            JobUtil.add_job_status(self.job_id, 100, "Delete pending CSAR(%s) successfully." % self.csar_id)
            return

        csar_info = query_csar_from_catalog(self.csar_id)

        process_state = ignore_case_get(csar_info, "processState")
        if process_state == P_STATUS_DELETING:
            JobUtil.add_job_status(self.job_id, 100, "CSAR(%s) is deleting now." % self.csar_id)
            return

        deletion_pending = ignore_case_get(csar_info, "deletionPending")
        if deletion_pending.lower() == "false":
            JobUtil.add_job_status(self.job_id, 100, "CSAR(%s) need not to be deleted." % self.csar_id)
            return

        if NfInstModel.objects.filter(package_id=self.csar_id):
            JobUtil.add_job_status(self.job_id, 100, "CSAR(%s) is in using, cannot be deleted." % self.csar_id)
            return

        NfPackage().delete_csar(self.csar_id, self.job_id)


####################################################################################################################
class NfPackage(object):
    """
    Actions for nf package.
    """

    def __init__(self):
        pass

    def get_csars(self):
        ret = {"csars": []}
        nf_pkgs = NfPackageModel.objects.filter()
        for nf_pkg in nf_pkgs:
            ret["csars"].append({
                "csarId": nf_pkg.nfpackageid,
                "vnfdId": nf_pkg.vnfdid
            })
        return ret
        
    def get_csar(self, csar_id):
        pkg_info = {}
        nf_pkg = NfPackageModel.objects.filter(nfpackageid=csar_id)
        if nf_pkg:
            pkg_info["vnfdId"] = nf_pkg[0].vnfdid
            pkg_info["vnfdProvider"] = nf_pkg[0].vendor
            pkg_info["vnfdVersion"] = nf_pkg[0].vnfdversion
            pkg_info["vnfVersion"] = nf_pkg[0].vnfversion

        casrinfo = query_csar_from_catalog(csar_id)
        props_of_catalog = [
            "name", "provider", "version", "operationalState", "usageState",
            "onBoardState", "processState", "deletionPending", "downloadUri",
            "createTime", "modifyTime", "format", "size"]
        for prop in props_of_catalog:
            pkg_info[prop] = ignore_case_get(casrinfo, prop)

        nf_pkg_files = VnfPackageFileModel.objects.filter(vnfpid=csar_id)
        img_info = [{
            "index": str(i),
            "fileName": nf_pkg_files[i].filename,
            "imageId": nf_pkg_files[i].imageid,
            "vimId": nf_pkg_files[i].vimid,
            "vimUser": nf_pkg_files[i].vimuser,
            "tenant": nf_pkg_files[i].tenant,
            "status": nf_pkg_files[i].status}
            for i in range(len(nf_pkg_files))]

        vnf_insts = NfInstModel.objects.filter(package_id=csar_id)
        vnf_inst_info = [{"vnfInstanceId": vnf_inst.nfinstid,
                          "vnfInstanceName": vnf_inst.nf_name} for vnf_inst in vnf_insts]

        return [0, {"csarId": csar_id,
                    "packageInfo": pkg_info,
                    "imageInfo": img_info,
                    "vnfInstanceInfo": vnf_inst_info}]

    def delete_csar(self, csar_id, job_id):
        JobUtil.add_job_status(job_id, 10, "Set processState of CSAR(%s)." % csar_id)
        set_csar_state(csar_id, "processState", P_STATUS_DELETING)

        JobUtil.add_job_status(job_id, 20, "Get package files of CSAR(%s)." % csar_id)
        all_nf_pkg_files = VnfPackageFileModel.objects.all()
        nf_pkg_files = VnfPackageFileModel.objects.filter(vnfpid=csar_id)
        vims = get_vims()

        for pkg_file in nf_pkg_files:
            if IGNORE_DEL_IMG_WEHN_DEL_CSAR:
                logger.warn("ignore delete image(%s)" % pkg_file.filename)
                continue
            JobUtil.add_job_status(job_id, 50, "Delete image(%s) of CSAR(%s)." %
                                   (pkg_file.filename, csar_id))
            if self.is_image_refed_by_other_nf_pkg(all_nf_pkg_files, pkg_file.imageid, csar_id, pkg_file.vimid):
                logger.warn("Image(%s) is refered by CSAR(%s).", pkg_file.filename, csar_id)
                continue
            sel_vim = [vim for vim in vims if vim["vimId"] == pkg_file.vimid]
            if not sel_vim:
                logger.warn("Vim(%s) does not exist.", pkg_file.vimid)
                continue
            vim_api = VimAdaptor({
                "vimid": pkg_file.vimid,
                "vimtype": sel_vim[0]["type"],
                "url": sel_vim[0]["url"],
                "user": sel_vim[0]["userName"],
                "passwd": sel_vim[0]["password"],
                "tenant": sel_vim[0]["tenant"]})
            ret = vim_api.delete_image(pkg_file.imageid)
            if ret[0] != 0:
                logger.error("Failed to delete image(%s) from vim(%s)", pkg_file.filename, pkg_file.vimid)

        JobUtil.add_job_status(job_id, 70, "Delete CSAR(%s) from catalog." % csar_id)
        ret = delete_csar_from_catalog(csar_id)
        if ret[0] != 0:
            raise NSLCMException(ret[1])

        JobUtil.add_job_status(job_id, 90, "Delete CSAR(%s) from database." % csar_id)
        VnfPackageFileModel.objects.filter(vnfpid=csar_id).delete()
        NfPackageModel.objects.filter(nfpackageid=csar_id).delete()

        JobUtil.add_job_status(job_id, 100, "Delete CSAR(%s) successfully." % csar_id)

    def is_image_refed_by_other_nf_pkg(self, nf_pkg_files, imageid, csar_id, vim_id):
        for f in nf_pkg_files:
            if f.imageid == imageid and f.vimid == vim_id and f.vnfpid != csar_id:
                return True
        return False
