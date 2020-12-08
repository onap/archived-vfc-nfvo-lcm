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
import uuid
import time
import mock

from django.test import TestCase, Client
from rest_framework import status

from lcm.ns_vnfs.biz.grant_vnfs import GrantVnfs
from lcm.pub.database.models import VLInstModel, NfInstModel, JobModel, NSInstModel, VmInstModel, \
    OOFDataModel, VNFCInstModel, PortInstModel, CPInstModel, SubscriptionModel
from lcm.pub.exceptions import NSLCMException
from lcm.pub.utils import restcall
from lcm.jobs.enum import JOB_MODEL_STATUS, JOB_TYPE, JOB_ACTION, JOB_PROGRESS
from lcm.pub.utils.jobutil import JobUtil
from lcm.pub.utils.timeutil import now_time
from lcm.pub.utils.values import ignore_case_get
from lcm.ns_vnfs.biz.grant_vnf import GrantVnf
from lcm.ns_vnfs.biz.heal_vnfs import NFHealService
from lcm.ns_vnfs.biz.scale_vnfs import NFManualScaleService
from lcm.ns_vnfs.biz.subscribe import SubscriptionDeletion
from lcm.ns_vnfs.biz.terminate_nfs import TerminateVnfs
from lcm.ns_vnfs.enum import VNF_STATUS, LIFE_CYCLE_OPERATION, RESOURCE_CHANGE_TYPE, VNFC_CHANGE_TYPE, \
    INST_TYPE, NETWORK_RESOURCE_TYPE
from lcm.ns_vnfs.biz.place_vnfs import PlaceVnfs
from lcm.ns_vnfs.tests.test_data import vnfm_info, vim_info, vnf_place_request
from lcm.ns_vnfs.tests.test_data import nf_package_info, nsd_model_dict, subscription_response_data
from lcm.ns_vnfs.biz.create_vnfs import CreateVnfs
from lcm.ns_vnfs.biz import create_vnfs, grant_vnf
from lcm.ns_vnfs.biz.update_vnfs import NFOperateService
from lcm.ns_vnfs.biz.verify_vnfs import VerifyVnfs
from lcm.ns.enum import OWNER_TYPE
from lcm.ns_vnfs.biz.handle_notification import HandleVnfLcmOocNotification, HandleVnfIdentifierCreationNotification, \
    HandleVnfIdentifierDeletionNotification
from lcm.ns_vnfs.biz.notify_lcm import NotifyLcm


class TestGetVnfViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.nf_inst_id = str(uuid.uuid4())
        NfInstModel(nfinstid=self.nf_inst_id, nf_name="vnf1", vnfm_inst_id="1", vnf_id="vnf_id1",
                    status=VNF_STATUS.ACTIVE, create_time=now_time(), lastuptime=now_time()).save()

    def tearDown(self):
        NfInstModel.objects.all().delete()

    def test_get_vnf(self):
        response = self.client.get("/api/nslcm/v1/ns/vnfs/%s" % self.nf_inst_id)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        context = json.loads(response.content)
        self.assertEqual(self.nf_inst_id, context["vnfInstId"])


class TestTerminateVnfViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.data = {
            "terminationType": "forceful",
            "gracefulTerminationTimeout": "600"
        }
        self.ns_inst_id = str(uuid.uuid4())
        self.nf_inst_id = "1"
        self.vim_id = str(uuid.uuid4())
        self.job_id = str(uuid.uuid4())
        self.nf_uuid = "111"
        self.vnfd_model = {"metadata": {"vnfdId": "1"}}
        NSInstModel.objects.all().delete()
        NfInstModel.objects.all().delete()
        VmInstModel.objects.all().delete()
        NSInstModel(id=self.ns_inst_id, name="ns_name").save()
        NfInstModel.objects.create(nfinstid=self.nf_inst_id,
                                   vnfm_inst_id="1",
                                   status="active",
                                   mnfinstid=self.nf_uuid,
                                   vnfd_model=self.vnfd_model
                                   )
        VmInstModel.objects.create(vmid="1",
                                   vimid='{"cloud_owner": "VCPE", "cloud_regionid": "RegionOne"}',
                                   instid=self.nf_inst_id
                                   )
        SubscriptionModel(vnf_instance_filter=self.nf_inst_id, callback_uri="", links="").save()

    def tearDown(self):
        NSInstModel.objects.all().delete()
        NfInstModel.objects.all().delete()
        VmInstModel.objects.all().delete()
        SubscriptionModel.objects.all().delete()

    @mock.patch.object(TerminateVnfs, "run")
    def test_terminate_vnf_url(self, mock_run):
        req_data = {
            "terminationType": "forceful",
            "gracefulTerminationTimeout": "600"}

        response = self.client.post("/api/nslcm/v1/ns/terminatevnf/%s" % self.nf_inst_id, data=req_data)
        self.assertEqual(status.HTTP_202_ACCEPTED, response.status_code)

    @mock.patch.object(time, "sleep")
    @mock.patch.object(restcall, "call_req")
    def test_terminate_vnf(self, mock_call_req, mock_sleep):
        job_id = JobUtil.create_job(JOB_TYPE.VNF, JOB_ACTION.TERMINATE, self.nf_inst_id)
        job_info = {
            "jobId": job_id,
            "responsedescriptor": {"status": JOB_MODEL_STATUS.FINISHED}
        }
        mock_vals = {
            "/external-system/esr-vnfm-list/esr-vnfm/1?depth=all":
                [0, json.JSONEncoder().encode(vnfm_info), "200"],
            "/api/ztevnfmdriver/v1/1/vnfs/111/terminate":
                [0, json.JSONEncoder().encode({"jobId": job_id}), "200"],
            "/api/ztevnfmdriver/v1/1/jobs/" + job_id + "?responseId=0":
                [0, json.JSONEncoder().encode(job_info), "200"],
            "/api/resmgr/v1/vnf/1":
                [0, json.JSONEncoder().encode({"jobId": job_id}), "200"],
            "api/gvnfmdriver/v1/1/subscriptions/":
                [0, json.JSONEncoder().encode({}), "200"]
        }

        def side_effect(*args):
            return mock_vals[args[4]]
        mock_call_req.side_effect = side_effect
        TerminateVnfs(self.data, self.nf_inst_id, job_id).run()
        nfinst = NfInstModel.objects.filter(nfinstid=self.nf_inst_id)
        if nfinst:
            self.assertEqual(1, 0)
        else:
            self.assertEqual(1, 1)
        self.assertEqual(JobModel.objects.get(jobid=job_id).progress, 100)

    @mock.patch.object(time, "sleep")
    @mock.patch.object(restcall, "call_req")
    @mock.patch.object(SubscriptionDeletion, "send_subscription_deletion_request")
    def test_terminate_vnf_when_no_vnf_uuid(self, mock_send_subscription_deletion_request, mock_call_req, mock_sleep):
        nf_inst_id = "test_terminate_vnf_when_no_vnf_uuid"
        NSInstModel(id=nf_inst_id, name="ns_name_2").save()
        NfInstModel.objects.create(nfinstid=nf_inst_id,
                                   vnfm_inst_id="2",
                                   status="active",
                                   vnfd_model=self.vnfd_model
                                   )
        VmInstModel.objects.create(vmid="2",
                                   vimid='{"cloud_owner": "VCPE", "cloud_regionid": "RegionOne"}',
                                   instid=nf_inst_id
                                   )
        job_id = JobUtil.create_job(JOB_TYPE.VNF, JOB_ACTION.TERMINATE, nf_inst_id)
        job_info = {
            "jobId": job_id,
            "responsedescriptor": {"status": JOB_MODEL_STATUS.FINISHED}
        }
        mock_vals = {
            "/external-system/esr-vnfm-list/esr-vnfm/2?depth=all":
                [0, json.JSONEncoder().encode(vnfm_info), "200"],
            "/api/ztevnfmdriver/v1/2/vnfs/None/terminate":
                [0, json.JSONEncoder().encode({"jobId": job_id}), "200"],
            "/api/ztevnfmdriver/v1/2/jobs/" + job_id + "?responseId=0":
                [0, json.JSONEncoder().encode(job_info), "200"],
            "/api/resmgr/v1/vnf/%s" % nf_inst_id:
                [0, json.JSONEncoder().encode({"jobId": job_id}), "200"]
        }

        def side_effect(*args):
            return mock_vals[args[4]]

        mock_call_req.side_effect = side_effect
        TerminateVnfs(self.data, nf_inst_id, job_id).run()
        nfinst = NfInstModel.objects.filter(nfinstid=nf_inst_id)
        if nfinst:
            self.assertEqual(1, 0)
        else:
            self.assertEqual(1, 1)
        self.assertEqual(JobModel.objects.get(jobid=job_id).progress, 100)

    @mock.patch.object(time, "sleep")
    @mock.patch.object(restcall, "call_req")
    @mock.patch.object(SubscriptionDeletion, "send_subscription_deletion_request")
    def test_terminate_vnf_when_nf_not_exists(self, mock_send_subscription_deletion_request, mock_call_req, mock_sleep):
        job_id = JobUtil.create_job(JOB_TYPE.VNF, JOB_ACTION.TERMINATE, self.nf_inst_id)
        TerminateVnfs(self.data, "nf_not_exists", job_id).run()
        nfinst = NfInstModel.objects.filter(nfinstid="nf_not_exists")
        if nfinst:
            self.assertEqual(1, 0)
        else:
            self.assertEqual(1, 1)
        self.assertEqual(JobModel.objects.get(jobid=job_id).progress, 255)

    def test_terminate_vnf_when_vnf_is_dealing(self):
        NfInstModel.objects.filter(nfinstid=self.nf_inst_id).update(status=VNF_STATUS.TERMINATING)
        job_id = JobUtil.create_job(JOB_TYPE.VNF, JOB_ACTION.TERMINATE, self.nf_inst_id)
        TerminateVnfs(self.data, self.nf_inst_id, job_id).run()
        self.assertEqual(NfInstModel.objects.get(nfinstid=self.nf_inst_id).status, VNF_STATUS.FAILED)
        self.assertEqual(JobModel.objects.get(jobid=job_id).progress, 255)

    @mock.patch.object(time, "sleep")
    @mock.patch.object(restcall, "call_req")
    @mock.patch.object(SubscriptionDeletion, "send_subscription_deletion_request")
    def test_terminate_vnf_when_job_error(self, mock_send_subscription_deletion_request, mock_call_req, mock_sleep):
        job_id = JobUtil.create_job(JOB_TYPE.VNF, JOB_ACTION.TERMINATE, self.nf_inst_id)
        job_info = {
            "jobId": job_id,
            "responsedescriptor": {"status": JOB_MODEL_STATUS.ERROR}
        }
        mock_vals = {
            "/external-system/esr-vnfm-list/esr-vnfm/1?depth=all":
                [0, json.JSONEncoder().encode(vnfm_info), "200"],
            "/api/ztevnfmdriver/v1/1/vnfs/111/terminate":
                [0, json.JSONEncoder().encode({"jobId": job_id}), "200"],
            "/api/ztevnfmdriver/v1/1/jobs/" + job_id + "?responseId=0":
                [0, json.JSONEncoder().encode(job_info), "200"]
        }

        def side_effect(*args):
            return mock_vals[args[4]]

        mock_call_req.side_effect = side_effect
        TerminateVnfs(self.data, self.nf_inst_id, job_id).run()
        self.assertEqual(NfInstModel.objects.get(nfinstid=self.nf_inst_id).status, VNF_STATUS.FAILED)
        self.assertEqual(JobModel.objects.get(jobid=job_id).progress, 255)


class TestScaleVnfViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.nf_inst_id = str(uuid.uuid4())
        self.url = "/api/nslcm/v1/ns/ns_vnfs/%s/scaling" % self.nf_inst_id
        self.data = {
            "scaleVnfData":
                {
                    "type": "SCALE_OUT",
                    "aspectId": "demo_aspect1",
                    "numberOfSteps": 1,
                    "additionalParam": {}
                }
        }
        NfInstModel.objects.create(nfinstid=self.nf_inst_id, vnfm_inst_id="vnfm_inst_id_001",
                                   mnfinstid="m_nf_inst_id_001")

    def tearDown(self):
        NfInstModel.objects.all().delete()

    # def test_scale_vnf_view(self):
    #     response = self.client.post(self.url, self.data)
    #     self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    @mock.patch.object(time, "sleep")
    @mock.patch.object(restcall, "call_req")
    def test_scale_vnf_success(self, mock_call_req, mock_sleep):
        scale_service = NFManualScaleService(self.nf_inst_id, self.data)
        job_info = {
            "jobId": scale_service.job_id,
            "responsedescriptor": {"status": JOB_MODEL_STATUS.FINISHED}
        }
        mock_vals = {
            "/external-system/esr-vnfm-list/esr-vnfm/vnfm_inst_id_001?depth=all":
                [0, json.JSONEncoder().encode(vnfm_info), "200"],
            "/api/ztevnfmdriver/v1/vnfm_inst_id_001/vnfs/m_nf_inst_id_001/scale":
                [0, json.JSONEncoder().encode({"jobId": scale_service.job_id}), "200"],
            "/api/ztevnfmdriver/v1/vnfm_inst_id_001/jobs/" + scale_service.job_id + "?responseId=0":
                [0, json.JSONEncoder().encode(job_info), "200"]
        }

        def side_effect(*args):
            return mock_vals[args[4]]
        mock_call_req.side_effect = side_effect
        scale_service.run()
        nsIns = NfInstModel.objects.get(nfinstid=self.nf_inst_id)
        self.assertEqual(nsIns.status, VNF_STATUS.ACTIVE)

        jobs = JobModel.objects.get(jobid=scale_service.job_id)
        self.assertEqual(JOB_PROGRESS.FINISHED, jobs.progress)

    @mock.patch.object(time, "sleep")
    @mock.patch.object(restcall, "call_req")
    def test_scale_vnf_when_job_fail(self, mock_call_req, mock_sleep):
        scale_service = NFManualScaleService(self.nf_inst_id, self.data)
        job_info = {
            "jobId": scale_service.job_id,
            "responsedescriptor": {"status": JOB_MODEL_STATUS.ERROR}
        }
        mock_vals = {
            "/external-system/esr-vnfm-list/esr-vnfm/vnfm_inst_id_001?depth=all":
                [0, json.JSONEncoder().encode(vnfm_info), "200"],
            "/api/ztevnfmdriver/v1/vnfm_inst_id_001/vnfs/m_nf_inst_id_001/scale":
                [0, json.JSONEncoder().encode({"jobId": scale_service.job_id}), "200"],
            "/api/ztevnfmdriver/v1/vnfm_inst_id_001/jobs/" + scale_service.job_id + "?responseId=0":
                [0, json.JSONEncoder().encode(job_info), "200"]
        }

        def side_effect(*args):
            return mock_vals[args[4]]

        mock_call_req.side_effect = side_effect
        scale_service.run()
        nsIns = NfInstModel.objects.get(nfinstid=self.nf_inst_id)
        self.assertEqual(nsIns.status, VNF_STATUS.ACTIVE)
        jobs = JobModel.objects.get(jobid=scale_service.job_id)
        self.assertEqual(JOB_PROGRESS.ERROR, jobs.progress)

    def test_scale_vnf_when_exception(self):
        req_data = {
            "scaleVnfData": [
                {
                    "type": "SCALE_OUT",
                    "aspectId": "demo_aspect1",
                    "numberOfSteps": 1,
                },
                {
                    "type": "SCALE_OUT",
                    "aspectId": "demo_aspect2",
                    "numberOfSteps": 1,
                }
            ]
        }
        scale_service = NFManualScaleService(self.nf_inst_id, req_data)
        scale_service.run()
        nsIns = NfInstModel.objects.get(nfinstid=self.nf_inst_id)
        self.assertEqual(nsIns.status, VNF_STATUS.ACTIVE)

        jobs = JobModel.objects.get(jobid=scale_service.job_id)
        self.assertEqual(JOB_PROGRESS.ERROR, jobs.progress)

    def test_scale_vnf_when_nf_instance_does_not_exist(self):
        req_data = {
            "scaleVnfData":
                {
                    "type": "SCALE_OUT",
                    "aspectId": "demo_aspect1",
                    "numberOfSteps": 1,
                }
        }
        scale_service = NFManualScaleService("nf_instance_does_not_exist", req_data)
        scale_service.run()

        jobs = JobModel.objects.get(jobid=scale_service.job_id)
        self.assertEqual(JOB_PROGRESS.ERROR, jobs.progress)

    def test_scale_vnf_when_scale_vnf_data_does_not_exist(self):
        req_data = {
            "scaleVnfData": {}
        }
        scale_service = NFManualScaleService(self.nf_inst_id, req_data)
        scale_service.run()
        nsIns = NfInstModel.objects.get(nfinstid=self.nf_inst_id)
        self.assertEqual(nsIns.status, VNF_STATUS.ACTIVE)

        jobs = JobModel.objects.get(jobid=scale_service.job_id)
        self.assertEqual(JOB_PROGRESS.ERROR, jobs.progress)


class TestHealVnfViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.ns_inst_id = str(uuid.uuid4())
        self.nf_inst_id = str(uuid.uuid4())
        self.nf_uuid = "111"
        self.data = {
            "action": "vmReset",
            "affectedvm": {
                "vmid": "1",
                "vduid": "1",
                "vmname": "name",
            },
            "additionalParams": {
                "actionvminfo": {
                    "vmid": "vm_id_001",
                }
            }
        }
        NSInstModel(id=self.ns_inst_id, name="ns_name").save()
        NfInstModel.objects.create(nfinstid=self.nf_inst_id, status=VNF_STATUS.NULL, vnfm_inst_id="vnfm_inst_id_001",
                                   mnfinstid="m_nf_inst_id_001")
        NfInstModel.objects.create(nfinstid="non_vud_id", status=VNF_STATUS.NULL, vnfm_inst_id="vnfm_inst_id_001",
                                   mnfinstid="m_nf_inst_id_001")
        VNFCInstModel.objects.create(nfinstid=self.nf_inst_id, vmid="vm_id_001", vduid="vdu_id_001")
        VmInstModel.objects.create(resouceid="vm_id_001", vmname="vm_name_001")

    def tearDown(self):
        NSInstModel.objects.all().delete()
        NfInstModel.objects.all().delete()

    @mock.patch.object(time, "sleep")
    @mock.patch.object(restcall, "call_req")
    def test_heal_vnf_success(self, mock_call_req, mock_sleep):
        heal_service = NFHealService(self.nf_inst_id, self.data)
        mock_vals = {
            "/test/bins/1?timeout=15000":
                [0, json.JSONEncoder().encode(['{"powering-off": "", "instance_id": "vm_id_001", '
                                               '"display_name": ""}']), "200"],
            "/external-system/esr-vnfm-list/esr-vnfm/vnfm_inst_id_001?depth=all":
                [0, json.JSONEncoder().encode(vnfm_info), "200"],
            "/api/ztevnfmdriver/v1/vnfm_inst_id_001/vnfs/m_nf_inst_id_001/heal":
                [0, json.JSONEncoder().encode({"jobId": heal_service.job_id}), "200"],
            "/api/ztevnfmdriver/v1/vnfm_inst_id_001/jobs/" + heal_service.job_id + "?responseId=0":
                [0, json.JSONEncoder().encode({
                    "jobId": heal_service.job_id,
                    "responsedescriptor": {
                        "status": JOB_MODEL_STATUS.FINISHED,
                        "responsehistorylist": [{
                            "progress": "0",
                            "status": JOB_MODEL_STATUS.PROCESSING,
                            "responseid": "2",
                            "statusdescription": "creating",
                            "errorcode": "0"
                        }]
                    }
                }), "200"]
        }

        def side_effect(*args):
            return mock_vals[args[4]]

        mock_call_req.side_effect = side_effect
        heal_service.run()
        self.assertEqual(NfInstModel.objects.get(nfinstid=self.nf_inst_id).status, VNF_STATUS.ACTIVE)
        jobs = JobModel.objects.get(jobid=heal_service.job_id)
        self.assertEqual(JOB_PROGRESS.FINISHED, jobs.progress)

    def test_heal_vnf_when_non_existing_vnf(self, ):
        heal_service = NFHealService("on_existing_vnf", self.data)
        heal_service.run()
        self.assertEqual(NfInstModel.objects.get(nfinstid=self.nf_inst_id).status, VNF_STATUS.NULL)
        jobs = JobModel.objects.get(jobid=heal_service.job_id)
        self.assertEqual(JOB_PROGRESS.ERROR, jobs.progress)

    def test_heal_vnf_when_additional_params_non_exist(self):
        data = {"action": "vmReset"}
        heal_service = NFHealService(self.nf_inst_id, data)
        heal_service.run()
        self.assertEqual(NfInstModel.objects.get(nfinstid=self.nf_inst_id).status, VNF_STATUS.NULL)
        jobs = JobModel.objects.get(jobid=heal_service.job_id)
        self.assertEqual(JOB_PROGRESS.ERROR, jobs.progress)

    def test_heal_vnf_when_non_vud_id(self, ):
        heal_service = NFHealService("non_vud_id", self.data)
        heal_service.run()
        self.assertEqual(NfInstModel.objects.get(nfinstid="non_vud_id").status, VNF_STATUS.NULL)
        jobs = JobModel.objects.get(jobid=heal_service.job_id)
        self.assertEqual(JOB_PROGRESS.ERROR, jobs.progress)

    @mock.patch.object(restcall, "call_req")
    def test_heal_vnf_when_no_vnfm_job_id(self, mock_call_req):
        heal_service = NFHealService(self.nf_inst_id, self.data)
        mock_vals = {
            "/test/bins/1?timeout=15000":
                [0, json.JSONEncoder().encode(['{"powering-off": "", "instance_id": "vm_id_001", '
                                               '"display_name": ""}']), "200"],
            "/external-system/esr-vnfm-list/esr-vnfm/vnfm_inst_id_001?depth=all":
                [0, json.JSONEncoder().encode(vnfm_info), "200"],
            "/api/ztevnfmdriver/v1/vnfm_inst_id_001/vnfs/m_nf_inst_id_001/heal":
                [0, json.JSONEncoder().encode({}), "200"]
        }

        def side_effect(*args):
            return mock_vals[args[4]]

        mock_call_req.side_effect = side_effect
        heal_service.run()
        self.assertEqual(NfInstModel.objects.get(nfinstid=self.nf_inst_id).status, VNF_STATUS.ACTIVE)
        jobs = JobModel.objects.get(jobid=heal_service.job_id)
        self.assertEqual(JOB_PROGRESS.FINISHED, jobs.progress)

    @mock.patch.object(time, "sleep")
    @mock.patch.object(restcall, "call_req")
    def test_heal_vnf_when_job_bot_finish(self, mock_call_req, mock_sleep):
        heal_service = NFHealService(self.nf_inst_id, self.data)
        mock_vals = {
            "/test/bins/1?timeout=15000":
                [0, json.JSONEncoder().encode(['{"powering-off": "", "instance_id": "vm_id_001", '
                                               '"display_name": ""}']), "200"],
            "/external-system/esr-vnfm-list/esr-vnfm/vnfm_inst_id_001?depth=all":
                [0, json.JSONEncoder().encode(vnfm_info), "200"],
            "/api/ztevnfmdriver/v1/vnfm_inst_id_001/vnfs/m_nf_inst_id_001/heal":
                [0, json.JSONEncoder().encode({"jobId": heal_service.job_id}), "200"],
            "/api/ztevnfmdriver/v1/vnfm_inst_id_001/jobs/" + heal_service.job_id + "?responseId=0":
                [0, json.JSONEncoder().encode({
                    "jobId": heal_service.job_id,
                    "responsedescriptor": {
                        "status": JOB_MODEL_STATUS.ERROR,
                        "responsehistorylist": [{
                            "progress": "0",
                            "status": JOB_MODEL_STATUS.PROCESSING,
                            "responseid": "2",
                            "statusdescription": "creating",
                            "errorcode": "0"
                        }]
                    }
                }), "200"]
        }

        def side_effect(*args):
            return mock_vals[args[4]]

        mock_call_req.side_effect = side_effect
        heal_service.run()
        self.assertEqual(NfInstModel.objects.get(nfinstid=self.nf_inst_id).status, VNF_STATUS.HEALING)
        jobs = JobModel.objects.get(jobid=heal_service.job_id)
        self.assertEqual(JOB_PROGRESS.ERROR, jobs.progress)


class TestGetVnfmInfoViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.vnfm_id = str(uuid.uuid4())

    def tearDown(self):
        pass

    @mock.patch.object(restcall, "call_req")
    def test_get_vnfm_info(self, mock_call_req):
        vnfm_info_aai = {
            "vnfm-id": "example-vnfm-id-val-62576",
            "vim-id": "example-vim-id-val-35114",
            "certificate-url": "example-certificate-url-val-90242",
            "esr-system-info-list": {
                "esr-system-info": [
                    {
                        "esr-system-info-id": "example-esr-system-info-id-val-78484",
                        "system-name": "example-system-name-val-23790",
                        "type": "example-type-val-52596",
                        "vendor": "example-vendor-val-47399",
                        "version": "example-version-val-42051",
                        "service-url": "example-service-url-val-10731",
                        "user-name": "example-user-name-val-65946",
                        "password": "example-password-val-22505",
                        "system-type": "example-system-type-val-27221",
                        "protocal": "example-protocal-val-54632",
                        "ssl-cacert": "example-ssl-cacert-val-45965",
                        "ssl-insecure": True,
                        "ip-address": "example-ip-address-val-19212",
                        "port": "example-port-val-57641",
                        "cloud-domain": "example-cloud-domain-val-26296",
                        "default-tenant": "example-default-tenant-val-87724"
                    }
                ]
            }
        }
        r1 = [0, json.JSONEncoder().encode(vnfm_info_aai), "200"]
        mock_call_req.side_effect = [r1]
        esr_system_info = ignore_case_get(ignore_case_get(vnfm_info_aai, "esr-system-info-list"), "esr-system-info")
        expect_data = {
            "vnfmId": vnfm_info_aai["vnfm-id"],
            "name": vnfm_info_aai["vnfm-id"],
            "type": ignore_case_get(esr_system_info[0], "type"),
            "vimId": vnfm_info_aai["vim-id"],
            "vendor": ignore_case_get(esr_system_info[0], "vendor"),
            "version": ignore_case_get(esr_system_info[0], "version"),
            "description": "vnfm",
            "certificateUrl": vnfm_info_aai["certificate-url"],
            "url": ignore_case_get(esr_system_info[0], "service-url"),
            "userName": ignore_case_get(esr_system_info[0], "user-name"),
            "password": ignore_case_get(esr_system_info[0], "password"),
            "createTime": ""
        }

        response = self.client.get("/api/nslcm/v1/vnfms/%s" % self.vnfm_id)
        self.assertEqual(status.HTTP_200_OK, response.status_code, response.content)
        context = json.loads(response.content)
        self.assertEqual(expect_data, context)


class TestGetVimInfoViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.vim_id = {"cloud_owner": "VCPE", "cloud_regionid": "RegionOne"}

    def tearDown(self):
        pass

    @mock.patch.object(restcall, "call_req")
    def test_get_vim_info(self, mock_call_req):
        r1 = [0, json.JSONEncoder().encode(vim_info), "200"]
        mock_call_req.side_effect = [r1]
        esr_system_info = ignore_case_get(ignore_case_get(vim_info, "esr-system-info-list"), "esr-system-info")
        expect_data = {
            "vimId": self.vim_id,
            "name": self.vim_id,
            "url": ignore_case_get(esr_system_info[0], "service-url"),
            "userName": ignore_case_get(esr_system_info[0], "user-name"),
            "password": ignore_case_get(esr_system_info[0], "password"),
            # "tenant": ignore_case_get(tenants[0], "tenant-id"),
            "tenant": ignore_case_get(esr_system_info[0], "default-tenant"),
            "vendor": ignore_case_get(esr_system_info[0], "vendor"),
            "version": ignore_case_get(esr_system_info[0], "version"),
            "description": "vim",
            "domain": "",
            "type": ignore_case_get(esr_system_info[0], "type"),
            "createTime": ""
        }

        # response = self.client.get("/api/nslcm/v1/vims/%s" % self.vim_id)
        response = self.client.get("/api/nslcm/v1/vims/%s/%s" % (self.vim_id["cloud_owner"], self.vim_id["cloud_regionid"]))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        context = json.loads(response.content)
        self.assertEqual(expect_data["url"], context["url"])


class TestPlaceVnfViews(TestCase):
    def setUp(self):
        self.vnf_inst_id = "1234"
        self.vnf_id = "vG"
        self.client = Client()
        self.url = "/api/nslcm/v1/ns/placevnf"
        self.data = vnf_place_request
        OOFDataModel.objects.all().delete()
        OOFDataModel.objects.create(
            request_id="1234",
            transaction_id="1234",
            request_status="init",
            request_module_name=self.vnf_id,
            service_resource_id=self.vnf_inst_id,
            vim_id="",
            cloud_owner="",
            cloud_region_id="",
            vdu_info="",
        )

    def tearDown(self):
        OOFDataModel.objects.all().delete()

    @mock.patch.object(restcall, "call_req")
    def test_place_vnf(self, mock_call_req):
        vdu_info_json = [{
            "vduName": "vG_0",
            "flavorName": "HPA.flavor.1",
            "flavorId": "12345",
            "directive": []
        }]
        # response = self.client.post(self.url, data=self.data)
        PlaceVnfs(vnf_place_request).extract()
        db_info = OOFDataModel.objects.filter(request_id=vnf_place_request.get("requestId"), transaction_id=vnf_place_request.get("transactionId"))
        self.assertEqual(db_info[0].request_status, "completed")
        self.assertEqual(db_info[0].vim_id, "CloudOwner1_DLLSTX1A")
        self.assertEqual(db_info[0].cloud_owner, "CloudOwner1")
        self.assertEqual(db_info[0].cloud_region_id, "DLLSTX1A")
        self.assertEqual(db_info[0].vdu_info, json.dumps(vdu_info_json))

    def test_place_vnf_with_invalid_response(self):
        resp = {
            "requestId": "1234",
            "transactionId": "1234",
            "statusMessage": "xx",
            "requestStatus": "pending",
            "solutions": {
                "placementSolutions": [
                    [
                        {
                            "resourceModuleName": self.vnf_id,
                            "serviceResourceId": self.vnf_inst_id,
                            "solution": {
                                "identifierType": "serviceInstanceId",
                                "identifiers": [
                                    "xx"
                                ],
                                "cloudOwner": "CloudOwner1 "
                            },
                            "assignmentInfo": []
                        }
                    ]
                ],
                "licenseSolutions": [
                    {
                        "resourceModuleName": "string",
                        "serviceResourceId": "string",
                        "entitlementPoolUUID": [
                            "string"
                        ],
                        "licenseKeyGroupUUID": [
                            "string"
                        ],
                        "entitlementPoolInvariantUUID": [
                            "string"
                        ],
                        "licenseKeyGroupInvariantUUID": [
                            "string"
                        ]
                    }
                ]
            }
        }
        PlaceVnfs(resp).extract()
        db_info = OOFDataModel.objects.filter(request_id=resp.get("requestId"), transaction_id=resp.get("transactionId"))
        self.assertEqual(db_info[0].request_status, "pending")
        self.assertEqual(db_info[0].vim_id, "none")
        self.assertEqual(db_info[0].cloud_owner, "none")
        self.assertEqual(db_info[0].cloud_region_id, "none")
        self.assertEqual(db_info[0].vdu_info, "none")

    def test_place_vnf_with_no_assignment_info(self):
        resp = {
            "requestId": "1234",
            "transactionId": "1234",
            "statusMessage": "xx",
            "requestStatus": "completed",
            "solutions": {
                "placementSolutions": [
                    [
                        {
                            "resourceModuleName": self.vnf_id,
                            "serviceResourceId": self.vnf_inst_id,
                            "solution": {
                                "identifierType": "serviceInstanceId",
                                "identifiers": [
                                    "xx"
                                ],
                                "cloudOwner": "CloudOwner1 "
                            }
                        }
                    ]
                ],
                "licenseSolutions": [
                    {
                        "resourceModuleName": "string",
                        "serviceResourceId": "string",
                        "entitlementPoolUUID": [
                            "string"
                        ],
                        "licenseKeyGroupUUID": [
                            "string"
                        ],
                        "entitlementPoolInvariantUUID": [
                            "string"
                        ],
                        "licenseKeyGroupInvariantUUID": [
                            "string"
                        ]
                    }
                ]
            }
        }
        PlaceVnfs(resp).extract()
        db_info = OOFDataModel.objects.filter(request_id=resp.get("requestId"), transaction_id=resp.get("transactionId"))
        self.assertEqual(db_info[0].request_status, "completed")
        self.assertEqual(db_info[0].vim_id, "none")
        self.assertEqual(db_info[0].cloud_owner, "none")
        self.assertEqual(db_info[0].cloud_region_id, "none")
        self.assertEqual(db_info[0].vdu_info, "none")

    def test_place_vnf_no_directives(self):
        resp = {
            "requestId": "1234",
            "transactionId": "1234",
            "statusMessage": "xx",
            "requestStatus": "completed",
            "solutions": {
                "placementSolutions": [
                    [
                        {
                            "resourceModuleName": self.vnf_id,
                            "serviceResourceId": self.vnf_inst_id,
                            "solution": {
                                "identifierType": "serviceInstanceId",
                                "identifiers": [
                                    "xx"
                                ],
                                "cloudOwner": "CloudOwner1 "
                            },
                            "assignmentInfo": [
                                {"key": "locationId",
                                 "value": "DLLSTX1A"
                                 }
                            ]
                        }
                    ]
                ],
                "licenseSoutions": [
                    {
                        "resourceModuleName": "string",
                        "serviceResourceId": "string",
                        "entitlementPoolUUID": [
                            "string"
                        ],
                        "licenseKeyGroupUUID": [
                            "string"
                        ],
                        "entitlementPoolInvariantUUID": [
                            "string"
                        ],
                        "licenseKeyGroupInvariantUUID": [
                            "string"
                        ]
                    }
                ]
            }
        }
        PlaceVnfs(resp).extract()
        db_info = OOFDataModel.objects.filter(request_id=resp.get("requestId"), transaction_id=resp.get("transactionId"))
        self.assertEqual(db_info[0].request_status, "completed")
        self.assertEqual(db_info[0].vim_id, "none")
        self.assertEqual(db_info[0].cloud_owner, "none")
        self.assertEqual(db_info[0].cloud_region_id, "none")
        self.assertEqual(db_info[0].vdu_info, "none")

    def test_place_vnf_with_no_solution(self):
        resp = {
            "requestId": "1234",
            "transactionId": "1234",
            "statusMessage": "xx",
            "requestStatus": "completed",
            "solutions": {
                "placementSolutions": [],
                "licenseSoutions": []
            }
        }
        PlaceVnfs(resp).extract()
        db_info = OOFDataModel.objects.filter(request_id=resp.get("requestId"), transaction_id=resp.get("transactionId"))
        self.assertEqual(db_info[0].request_status, "completed")
        self.assertEqual(db_info[0].vim_id, "none")
        self.assertEqual(db_info[0].cloud_owner, "none")
        self.assertEqual(db_info[0].cloud_region_id, "none")
        self.assertEqual(db_info[0].vdu_info, "none")


class TestGrantVnfsViews(TestCase):
    def setUp(self):
        self.vnf_inst_id = str(uuid.uuid4())
        self.data = {
            "vnfInstanceId": self.vnf_inst_id,
            "lifecycleOperation": LIFE_CYCLE_OPERATION.INSTANTIATE,
            "addResource": [{"type": RESOURCE_CHANGE_TYPE.VDU, "vdu": "vdu_grant_vnf_add_resources"}],
            "additionalParam": {
                "vnfmid": "vnfm_inst_id_001",
                "vimid": '{"cloud_owner": "VCPE", "cloud_regionid": "RegionOne"}'
            }
        }
        self.client = Client()
        self.url = "/api/nslcm/v1/ns/grantvnf"
        NfInstModel(mnfinstid=self.vnf_inst_id, nfinstid="vnf_inst_id_001", package_id="package_id_001",
                    vnfm_inst_id="vnfm_inst_id_001").save()

    def tearDown(self):
        OOFDataModel.objects.all().delete()
        NfInstModel.objects.all().delete()

    # @mock.patch.object(restcall, "call_req")
    # def test_nf_grant_view(self, mock_call_req):
    #     mock_vals = {
    #         "/api/catalog/v1/vnfpackages/package_id_001":
    #             [0, json.JSONEncoder().encode(nf_package_info), "200"],
    #         "/api/resmgr/v1/resource/grant":
    #             [1, json.JSONEncoder().encode({}), "200"],
    #         "/cloud-infrastructure/cloud-regions/cloud-region/VCPE/RegionOne?depth=all":
    #             [0, json.JSONEncoder().encode(vim_info), "201"],
    #     }
    #
    #     def side_effect(*args):
    #         return mock_vals[args[4]]
    #
    #     mock_call_req.side_effect = side_effect
    #     data = {
    #         "vnfInstanceId": self.vnf_inst_id,
    #         "lifecycleOperation": LIFE_CYCLE_OPERATION.INSTANTIATE
    #     }
    #     response = self.client.post(self.url, data=data)
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    @mock.patch.object(restcall, "call_req")
    def test_nf_grant_view_when_add_resource(self, mock_call_req):
        mock_vals = {
            "/api/catalog/v1/vnfpackages/package_id_001":
                [0, json.JSONEncoder().encode(nf_package_info), "200"],
            "/api/resmgr/v1/resource/grant":
                [1, json.JSONEncoder().encode({}), "200"],
            "/cloud-infrastructure/cloud-regions/cloud-region/VCPE/RegionOne?depth=all":
                [0, json.JSONEncoder().encode(vim_info), "201"],
        }

        def side_effect(*args):
            return mock_vals[args[4]]
        mock_call_req.side_effect = side_effect
        resp = GrantVnfs(json.dumps(self.data), "").send_grant_vnf_to_resMgr()
        return_success = {"vim": {"accessInfo": {"tenant": "admin"},
                                  "vimId": "example-cloud-owner-val-97336_example-cloud-region-id-val-35532"}}
        self.assertEqual(resp, return_success)

    @mock.patch.object(restcall, "call_req")
    def test_nf_grant_view_when_remove_resource(self, mock_call_req):
        mock_vals = {
            "/api/catalog/v1/vnfpackages/package_id_001":
                [0, json.JSONEncoder().encode(nf_package_info), "200"],
            "/api/resmgr/v1/resource/grant":
                [1, json.JSONEncoder().encode({}), "200"],
            "/cloud-infrastructure/cloud-regions/cloud-region/VCPE/RegionOne?depth=all":
                [0, json.JSONEncoder().encode(vim_info), "201"],
        }

        def side_effect(*args):
            return mock_vals[args[4]]

        mock_call_req.side_effect = side_effect
        self.data.pop("addResource")
        self.data["removeResource"] = [{"vdu": "vdu_grant_vnf_remove_resources"}]
        resp = GrantVnfs(json.dumps(self.data), "").send_grant_vnf_to_resMgr()
        return_success = {"vim": {"accessInfo": {"tenant": "admin"},
                                  "vimId": "example-cloud-owner-val-97336_example-cloud-region-id-val-35532"}}
        self.assertEqual(resp, return_success)


class TestGrantVnfViews(TestCase):
    def setUp(self):
        self.vnf_inst_id = str(uuid.uuid4())
        self.data = {
            "vnfInstanceId": self.vnf_inst_id,
            "vnfLcmOpOccId": "vnf_lcm_op_occ_id",
            "addResources": [{"vdu": "vdu_grant_vnf_add_resources"}],
            "operation": "INSTANTIATE"
        }
        self.client = Client()
        vdu_info_dict = [{"vduName": "vg", "flavorName": "flavor_1", "flavorId": "flavor_id_001", "directive": []}]
        OOFDataModel(request_id="request_id_001", transaction_id="transaction_id_001", request_status="done",
                     request_module_name="vg", service_resource_id=self.vnf_inst_id, vim_id="cloudOwner_casa",
                     cloud_owner="cloudOwner", cloud_region_id="casa", vdu_info=json.dumps(vdu_info_dict)).save()
        NfInstModel(mnfinstid=self.vnf_inst_id, nfinstid="vnf_inst_id_001", package_id="package_id_001",
                    vnfm_inst_id="vnfm_id_001").save()

    def tearDown(self):
        OOFDataModel.objects.all().delete()
        NfInstModel.objects.all().delete()

    @mock.patch.object(grant_vnf, "vim_connections_get")
    def test_vnf_grant_view(self, mock_grant):
        resmgr_grant_resp = {
            "vim": {
                "vimId": "cloudOwner_casa",
                "accessInfo": {
                    "tenant": "tenantA"
                }
            }
        }
        mock_grant.return_value = resmgr_grant_resp
        self.data.pop("addResources")
        response = self.client.post("/api/nslcm/v2/grants", data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["vimAssets"]["computeResourceFlavours"][0]["vimConnectionId"], "cloudOwner_casa")
        self.assertEqual(response.data["vimAssets"]["computeResourceFlavours"][0]["resourceProviderId"], "vg")
        self.assertEqual(response.data["vimAssets"]["computeResourceFlavours"][0]["vimFlavourId"], "flavor_id_001")

    @mock.patch.object(restcall, "call_req")
    @mock.patch.object(grant_vnf, "vim_connections_get")
    def test_exec_grant_when_add_resources_success(self, mock_grant, mock_call_req):
        mock_vals = {
            "/api/catalog/v1/vnfpackages/package_id_001":
                [0, json.JSONEncoder().encode(nf_package_info), "200"],
        }

        def side_effect(*args):
            return mock_vals[args[4]]

        mock_call_req.side_effect = side_effect
        resmgr_grant_resp = {
            "vim": {
                "vimId": "cloudOwner_casa",
                "accessInfo": {
                    "tenant": "tenantA"
                }
            }
        }
        mock_grant.return_value = resmgr_grant_resp
        resp = GrantVnf(json.dumps(self.data)).exec_grant()
        self.assertEqual(resp["vimAssets"]["computeResourceFlavours"][0]["vimConnectionId"], "cloudOwner_casa")
        self.assertEqual(resp["vimAssets"]["computeResourceFlavours"][0]["resourceProviderId"], "vg")
        self.assertEqual(resp["vimAssets"]["computeResourceFlavours"][0]["vimFlavourId"], "flavor_id_001")

    def test_exec_grant_when_add_resources_but_no_vnfinst(self):
        self.data["vnfInstanceId"] = "no_vnfinst"
        resp = None
        try:
            resp = GrantVnf(json.dumps(self.data)).exec_grant()
        except NSLCMException as e:
            self.assertEqual(type(e), NSLCMException)
        finally:
            self.assertEqual(resp, None)

    @mock.patch.object(time, "sleep")
    @mock.patch.object(restcall, "call_req")
    @mock.patch.object(grant_vnf, "vim_connections_get")
    def test_exec_grant_when_add_resources_but_no_off(self, mock_grant, mock_call_req, mock_sleep):
        NfInstModel(mnfinstid="add_resources_but_no_off", nfinstid="vnf_inst_id_002",
                    package_id="package_id_002").save()
        mock_sleep.return_value = None
        mock_vals = {
            "/api/catalog/v1/vnfpackages/package_id_002":
                [0, json.JSONEncoder().encode(nf_package_info), "200"],
        }

        def side_effect(*args):
            return mock_vals[args[4]]

        mock_call_req.side_effect = side_effect
        resmgr_grant_resp = {
            "vim": {
                "vimId": "cloudOwner_casa",
                "accessInfo": {
                    "tenant": "tenantA"
                }
            }
        }
        mock_grant.return_value = resmgr_grant_resp
        self.data["vnfInstanceId"] = "add_resources_but_no_off"
        resp = GrantVnf(json.dumps(self.data)).exec_grant()
        self.assertEqual(resp["vnfInstanceId"], "add_resources_but_no_off")
        self.assertEqual(resp["vnfLcmOpOccId"], "vnf_lcm_op_occ_id")
        vimConnections = [{
            "id": "cloudOwner_casa",
            "vimId": "cloudOwner_casa",
            "vimType": None,
            "interfaceInfo": None,
            "accessInfo": {"tenant": "tenantA"},
            "extra": None
        }]
        self.assertEqual(resp["vimConnections"], vimConnections)

    @mock.patch.object(grant_vnf, "vim_connections_get")
    def test_exec_grant_when_resource_template_in_add_resources(self, mock_grant):
        resmgr_grant_resp = {
            "vim": {
                "vimId": "cloudOwner_casa",
                "accessInfo": {
                    "tenant": "tenantA"
                }
            }
        }
        mock_grant.return_value = resmgr_grant_resp
        self.data["addResources"] = [{"vdu": "vdu_grant_vnf_add_resources"}, "resourceTemplate"]
        resp = GrantVnf(json.dumps(self.data)).exec_grant()
        self.assertEqual(resp["vimAssets"]["computeResourceFlavours"][0]["vimConnectionId"], "cloudOwner_casa")
        self.assertEqual(resp["vimAssets"]["computeResourceFlavours"][0]["resourceProviderId"], "vg")
        self.assertEqual(resp["vimAssets"]["computeResourceFlavours"][0]["vimFlavourId"], "flavor_id_001")

    @mock.patch.object(restcall, "call_req")
    @mock.patch.object(grant_vnf, "vim_connections_get")
    def test_exec_grant_when_remove_resources_success(self, mock_grant, mock_call_req):
        mock_vals = {
            "/api/catalog/v1/vnfpackages/package_id_001":
                [0, json.JSONEncoder().encode(nf_package_info), "200"],
        }

        def side_effect(*args):
            return mock_vals[args[4]]

        mock_call_req.side_effect = side_effect
        resmgr_grant_resp = {
            "vim": {
                "vimId": "cloudOwner_casa",
                "accessInfo": {
                    "tenant": "tenantA"
                }
            }
        }
        mock_grant.return_value = resmgr_grant_resp
        self.data.pop("addResources")
        self.data["removeResources"] = [{"vdu": "vdu_grant_vnf_remove_resources"}]
        self.data["additionalparams"] = {"vnfmid": "vnfm_id_001"}
        resp = GrantVnf(json.dumps(self.data)).exec_grant()
        self.assertEqual(resp["vimAssets"]["computeResourceFlavours"][0]["vimConnectionId"], "cloudOwner_casa")
        self.assertEqual(resp["vimAssets"]["computeResourceFlavours"][0]["resourceProviderId"], "vg")
        self.assertEqual(resp["vimAssets"]["computeResourceFlavours"][0]["vimFlavourId"], "flavor_id_001")

    def test_exec_grant_when_remove_resources_no_vnfinst(self):
        self.data.pop("addResources")
        self.data["removeResources"] = [{"vdu": "vdu_grant_vnf_remove_resources"}]
        self.data["additionalparams"] = {"vnfmid": "vnfm_id_002"}
        resp = None
        try:
            resp = GrantVnf(json.dumps(self.data)).exec_grant()
        except NSLCMException as e:
            self.assertEqual(type(e), NSLCMException)
        finally:
            self.assertEqual(resp, None)

    @mock.patch.object(time, "sleep")
    @mock.patch.object(restcall, "call_req")
    @mock.patch.object(grant_vnf, "vim_connections_get")
    def test_exec_grant_when_remove_resources_but_no_off(self, mock_grant, mock_call_req, mock_sleep):
        NfInstModel(mnfinstid="remove_resources_but_no_off", nfinstid="vnf_inst_id_002", package_id="package_id_002",
                    vnfm_inst_id="vnfm_id_002").save()
        mock_sleep.return_value = None
        mock_vals = {
            "/api/catalog/v1/vnfpackages/package_id_002":
                [0, json.JSONEncoder().encode(nf_package_info), "200"],
        }

        def side_effect(*args):
            return mock_vals[args[4]]

        mock_call_req.side_effect = side_effect
        resmgr_grant_resp = {
            "vim": {
                "vimId": "cloudOwner_casa",
                "accessInfo": {
                    "tenant": "tenantA"
                }
            }
        }
        mock_grant.return_value = resmgr_grant_resp
        self.data["vnfInstanceId"] = "remove_resources_but_no_off"
        self.data.pop("addResources")
        self.data["removeResources"] = [{"vdu": "vdu_grant_vnf_remove_resources"}]
        self.data["additionalparams"] = {"vnfmid": "vnfm_id_002"}
        resp = GrantVnf(json.dumps(self.data)).exec_grant()
        self.assertEqual(resp["vnfInstanceId"], "remove_resources_but_no_off")
        self.assertEqual(resp["vnfLcmOpOccId"], "vnf_lcm_op_occ_id")
        vimConnections = [{
            "id": "cloudOwner_casa",
            "vimId": "cloudOwner_casa",
            "vimType": None,
            "interfaceInfo": None,
            "accessInfo": {"tenant": "tenantA"},
            "extra": None
        }]
        self.assertEqual(resp["vimConnections"], vimConnections)

    @mock.patch.object(grant_vnf, "vim_connections_get")
    def test_exec_grant_when_resource_template_in_remove_resources(self, mock_grant):
        resmgr_grant_resp = {
            "vim": {
                "vimId": "cloudOwner_casa",
                "accessInfo": {
                    "tenant": "tenantA"
                }
            }
        }
        mock_grant.return_value = resmgr_grant_resp
        self.data.pop("addResources")
        self.data["removeResources"] = [{"vdu": "vdu_grant_vnf_remove_resources"}, "resourceTemplate"]
        resp = GrantVnf(json.dumps(self.data)).exec_grant()
        self.assertEqual(resp["vimAssets"]["computeResourceFlavours"][0]["vimConnectionId"], "cloudOwner_casa")
        self.assertEqual(resp["vimAssets"]["computeResourceFlavours"][0]["resourceProviderId"], "vg")
        self.assertEqual(resp["vimAssets"]["computeResourceFlavours"][0]["vimFlavourId"], "flavor_id_001")


class TestCreateVnfViews(TestCase):
    def setUp(self):
        self.ns_inst_id = str(uuid.uuid4())
        self.job_id = str(uuid.uuid4())
        self.data = {
            "vnfIndex": "1",
            "nsInstanceId": self.ns_inst_id,
            # "additionalParamForNs": {"inputs": json.dumps({})},
            "additionalParamForVnf": [
                {
                    "vnfprofileid": "VBras",
                    "additionalparam": {
                        "inputs": json.dumps({
                            "vnf_param1": "11",
                            "vnf_param2": "22"
                        }),
                        "vnfminstanceid": "1",
                        # "vimId": "zte_test",
                        "vimId": '{"cloud_owner": "VCPE", "cloud_regionid": "RegionOne"}'
                    }
                }
            ]
        }
        self.client = Client()
        NSInstModel(id=self.ns_inst_id, name="ns", nspackage_id="1", nsd_id="nsd_id", description="description",
                    status="instantiating", nsd_model=json.dumps(nsd_model_dict), create_time=now_time(),
                    lastuptime=now_time()).save()
        VLInstModel(vldid="ext_mnet_network", ownertype=OWNER_TYPE.NS, ownerid=self.ns_inst_id,
                    vimid="{}").save()

    def tearDown(self):
        NfInstModel.objects.all().delete()
        JobModel.objects.all().delete()

    @mock.patch.object(CreateVnfs, "run")
    def test_create_vnf_view(self, mock_run):
        response = self.client.post("/api/nslcm/v1/ns/vnfs", data=self.data)
        self.assertEqual(status.HTTP_202_ACCEPTED, response.status_code)
        context = json.loads(response.content)
        self.assertTrue(NfInstModel.objects.filter(nfinstid=context["vnfInstId"]).exists())

    @mock.patch.object(time, "sleep")
    @mock.patch.object(restcall, "call_req")
    def test_create_vnf_thread_sucess(self, mock_call_req, mock_sleep):
        mock_sleep.return_value = None
        nf_inst_id, job_id = create_vnfs.prepare_create_params()
        mock_vals = {
            "/api/catalog/v1/vnfpackages/zte_vbras":
                [0, json.JSONEncoder().encode(nf_package_info), "200"],
            "/external-system/esr-vnfm-list/esr-vnfm/1?depth=all":
                [0, json.JSONEncoder().encode(vnfm_info), "200"],
            "/api/ztevnfmdriver/v1/1/vnfs":
                [0, json.JSONEncoder().encode({"jobId": self.job_id, "vnfInstanceId": 3}), "200"],
            "/api/oof/v1/placement":
                [0, json.JSONEncoder().encode({}), "202"],
            "/api/resmgr/v1/vnf":
                [0, json.JSONEncoder().encode({}), "200"],
            "/api/ztevnfmdriver/v1/1/jobs/" + self.job_id + "?responseId=0":
                [0, json.JSONEncoder().encode({"jobid": self.job_id,
                                               "responsedescriptor": {"progress": "100",
                                                                      "status": JOB_MODEL_STATUS.FINISHED,
                                                                      "responseid": "3",
                                                                      "statusdescription": "creating",
                                                                      "errorcode": "0",
                                                                      "responsehistorylist": [
                                                                          {"progress": "0",
                                                                           "status": JOB_MODEL_STATUS.PROCESSING,
                                                                           "responseid": "2",
                                                                           "statusdescription": "creating",
                                                                           "errorcode": "0"}]}}), "200"],
            "api/gvnfmdriver/v1/1/subscriptions":
                [0, json.JSONEncoder().encode(subscription_response_data), "200"],
            "/api/resmgr/v1/vnfinfo":
                [0, json.JSONEncoder().encode(subscription_response_data), "200"],

            # "/network/generic-vnfs/generic-vnf/%s" % nf_inst_id:
            #     [0, json.JSONEncoder().encode({}), "201"],
            # "/cloud-infrastructure/cloud-regions/cloud-region/zte/test?depth=all":
            #     [0, json.JSONEncoder().encode(vim_info), "201"],
            # "/cloud-infrastructure/cloud-regions/cloud-region/zte/test/tenants/tenant/admin/vservers/vserver/1":
            #     [0, json.JSONEncoder().encode({}), "201"],

        }

        def side_effect(*args):
            return mock_vals[args[4]]
        mock_call_req.side_effect = side_effect
        data = {
            "ns_instance_id": ignore_case_get(self.data, "nsInstanceId"),
            "additional_param_for_ns": ignore_case_get(self.data, "additionalParamForNs"),
            "additional_param_for_vnf": ignore_case_get(self.data, "additionalParamForVnf"),
            "vnf_index": ignore_case_get(self.data, "vnfIndex")
        }
        CreateVnfs(data, nf_inst_id, job_id).run()
        self.assertEqual(NfInstModel.objects.get(nfinstid=nf_inst_id).status, VNF_STATUS.ACTIVE)
        self.assertEqual(JobModel.objects.get(jobid=job_id).progress, JOB_PROGRESS.FINISHED)

    def test_create_vnf_thread_when_the_name_of_vnf_instance_already_exists(self):
        NfInstModel(nf_name="").save()
        nf_inst_id, job_id = create_vnfs.prepare_create_params()
        data = {
            "ns_instance_id": ignore_case_get(self.data, "nsInstanceId"),
            "additional_param_for_ns": ignore_case_get(self.data, "additionalParamForNs"),
            "additional_param_for_vnf": ignore_case_get(self.data, "additionalParamForVnf"),
            "vnf_index": ignore_case_get(self.data, "vnfIndex")
        }
        CreateVnfs(data, nf_inst_id, job_id).run()
        self.assertEqual(NfInstModel.objects.get(nfinstid=nf_inst_id).status, VNF_STATUS.FAILED)
        self.assertEqual(JobModel.objects.get(jobid=job_id).progress, JOB_PROGRESS.ERROR)

    @mock.patch.object(time, "sleep")
    @mock.patch.object(restcall, "call_req")
    def test_create_vnf_thread_when_data_has_vnfd_id(self, mock_call_req, mock_sleep):
        mock_sleep.return_value = None
        nf_inst_id, job_id = create_vnfs.prepare_create_params()
        mock_vals = {
            "/api/catalog/v1/vnfpackages/data_has_vnfd_id":
                [0, json.JSONEncoder().encode(nf_package_info), "200"],
            "/external-system/esr-vnfm-list/esr-vnfm/1?depth=all":
                [0, json.JSONEncoder().encode(vnfm_info), "200"],
            "/api/ztevnfmdriver/v1/1/vnfs":
                [0, json.JSONEncoder().encode({"jobId": self.job_id, "vnfInstanceId": 3}), "200"],
            "/api/oof/v1/placement":
                [0, json.JSONEncoder().encode({}), "202"],
            "/api/resmgr/v1/vnf":
                [0, json.JSONEncoder().encode({}), "200"],
            "/api/ztevnfmdriver/v1/1/jobs/" + self.job_id + "?responseId=0":
                [0, json.JSONEncoder().encode({"jobid": self.job_id,
                                               "responsedescriptor": {"progress": "100",
                                                                      "status": JOB_MODEL_STATUS.FINISHED,
                                                                      "responseid": "3",
                                                                      "statusdescription": "creating",
                                                                      "errorcode": "0",
                                                                      "responsehistorylist": [
                                                                          {"progress": "0",
                                                                           "status": JOB_MODEL_STATUS.PROCESSING,
                                                                           "responseid": "2",
                                                                           "statusdescription": "creating",
                                                                           "errorcode": "0"}]}}), "200"],
            "api/gvnfmdriver/v1/1/subscriptions":
                [0, json.JSONEncoder().encode({}), "200"],
            "/api/resmgr/v1/vnfinfo":
                [0, json.JSONEncoder().encode(subscription_response_data), "200"]
        }

        def side_effect(*args):
            return mock_vals[args[4]]

        mock_call_req.side_effect = side_effect
        self.data["additionalParamForVnf"][0]["additionalparam"]["vnfdId"] = "data_has_vnfd_id"
        data = {
            "ns_instance_id": ignore_case_get(self.data, "nsInstanceId"),
            "additional_param_for_ns": ignore_case_get(self.data, "additionalParamForNs"),
            "additional_param_for_vnf": ignore_case_get(self.data, "additionalParamForVnf"),
            "vnf_index": ignore_case_get(self.data, "vnfIndex")
        }
        CreateVnfs(data, nf_inst_id, job_id).run()
        self.assertEqual(NfInstModel.objects.get(nfinstid=nf_inst_id).status, VNF_STATUS.ACTIVE)
        self.assertEqual(JobModel.objects.get(jobid=job_id).progress, JOB_PROGRESS.FINISHED)

    @mock.patch.object(restcall, "call_req")
    @mock.patch.object(CreateVnfs, "build_homing_request")
    def test_send_homing_request(self, mock_build_req, mock_call_req):
        nf_inst_id, job_id = create_vnfs.prepare_create_params()
        OOFDataModel.objects.all().delete()
        resp = {
            "requestId": "1234",
            "transactionId": "1234",
            "requestStatus": "accepted"
        }
        mock_build_req.return_value = {
            "requestInfo": {
                "transactionId": "1234",
                "requestId": "1234",
                "callbackUrl": "xx",
                "sourceId": "vfc",
                "requestType": "create",
                "numSolutions": 1,
                "optimizers": ["placement"],
                "timeout": 600
            },
            "placementInfo": {
                "placementDemands": [
                    {
                        "resourceModuleName": "vG",
                        "serviceResourceId": "1234",
                        "resourceModelInfo": {
                            "modelInvariantId": "1234",
                            "modelVersionId": "1234"
                        }
                    }
                ]
            },
            "serviceInfo": {
                "serviceInstanceId": "1234",
                "serviceName": "1234",
                "modelInfo": {
                    "modelInvariantId": "5678",
                    "modelVersionId": "7890"
                }
            }
        }
        mock_call_req.return_value = [0, json.JSONEncoder().encode(resp), "202"]
        data = {
            "ns_instance_id": ignore_case_get(self.data, "nsInstanceId"),
            "additional_param_for_ns": ignore_case_get(self.data, "additionalParamForNs"),
            "additional_param_for_vnf": ignore_case_get(self.data, "additionalParamForVnf"),
            "vnf_index": ignore_case_get(self.data, "vnfIndex")
        }
        CreateVnfs(data, nf_inst_id, job_id).send_homing_request_to_OOF()
        ret = OOFDataModel.objects.filter(request_id="1234", transaction_id="1234")
        self.assertIsNotNone(ret)

    @mock.patch.object(time, "sleep")
    @mock.patch.object(restcall, "call_req")
    def test_create_vnf_thread_sucess_when_failed_to_subscribe_from_vnfm(self, mock_call_req, mock_sleep):
        mock_sleep.return_value = None
        nf_inst_id, job_id = create_vnfs.prepare_create_params()
        mock_vals = {
            "/api/catalog/v1/vnfpackages/zte_vbras":
                [0, json.JSONEncoder().encode(nf_package_info), "200"],
            "/external-system/esr-vnfm-list/esr-vnfm/1?depth=all":
                [0, json.JSONEncoder().encode(vnfm_info), "200"],
            "/api/ztevnfmdriver/v1/1/vnfs":
                [0, json.JSONEncoder().encode({"jobId": self.job_id, "vnfInstanceId": 3}), "200"],
            "/api/oof/v1/placement":
                [0, json.JSONEncoder().encode({}), "202"],
            "/api/resmgr/v1/vnf":
                [0, json.JSONEncoder().encode({}), "200"],
            "/api/ztevnfmdriver/v1/1/jobs/" + self.job_id + "?responseId=0":
                [0, json.JSONEncoder().encode({"jobid": self.job_id,
                                               "responsedescriptor": {"progress": "100",
                                                                      "status": JOB_MODEL_STATUS.FINISHED,
                                                                      "responseid": "3",
                                                                      "statusdescription": "creating",
                                                                      "errorcode": "0",
                                                                      "responsehistorylist": [
                                                                          {"progress": "0",
                                                                           "status": JOB_MODEL_STATUS.PROCESSING,
                                                                           "responseid": "2",
                                                                           "statusdescription": "creating",
                                                                           "errorcode": "0"}]}}), "200"],
            "api/gvnfmdriver/v1/1/subscriptions":
                [1, json.JSONEncoder().encode(subscription_response_data), "200"],
            "/api/resmgr/v1/vnfinfo":
                [0, json.JSONEncoder().encode(subscription_response_data), "200"],
        }

        def side_effect(*args):
            return mock_vals[args[4]]

        mock_call_req.side_effect = side_effect
        data = {
            "ns_instance_id": ignore_case_get(self.data, "nsInstanceId"),
            "additional_param_for_ns": ignore_case_get(self.data, "additionalParamForNs"),
            "additional_param_for_vnf": ignore_case_get(self.data, "additionalParamForVnf"),
            "vnf_index": ignore_case_get(self.data, "vnfIndex")
        }
        CreateVnfs(data, nf_inst_id, job_id).run()
        self.assertEqual(NfInstModel.objects.get(nfinstid=nf_inst_id).status, VNF_STATUS.ACTIVE)
        self.assertEqual(JobModel.objects.get(jobid=job_id).progress, JOB_PROGRESS.FINISHED)


class TestUpdateVnfsViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.data = {
            "terminationType": "forceful",
            "gracefulTerminationTimeout": "600",
            "additionalParams": ""
        }
        self.nf_inst_id = "test_update_vnf"
        self.m_nf_inst_id = "test_update_vnf_m_nf_inst_id"
        self.vnfm_inst_id = "test_update_vnf_vnfm_inst_id"
        self.vnfd_model = {"metadata": {"vnfdId": "1"}}
        NfInstModel.objects.all().delete()
        NfInstModel.objects.create(nfinstid=self.nf_inst_id,
                                   vnfm_inst_id=self.vnfm_inst_id,
                                   status=VNF_STATUS.NULL,
                                   mnfinstid=self.m_nf_inst_id,
                                   vnfd_model=self.vnfd_model
                                   )

    def tearDown(self):
        NfInstModel.objects.all().delete()

    @mock.patch.object(time, "sleep")
    @mock.patch.object(restcall, "call_req")
    def test_update_vnf_thread(self, mock_call_req, mock_sleep):
        vnf_update_service = NFOperateService(self.nf_inst_id, self.data)
        job_info = {
            "jobId": vnf_update_service.job_id,
            "responsedescriptor": {"status": JOB_MODEL_STATUS.FINISHED}
        }
        mock_vals = {
            "/external-system/esr-vnfm-list/esr-vnfm/test_update_vnf_vnfm_inst_id?depth=all":
                [0, json.JSONEncoder().encode(vnfm_info), "200"],
            "/api/ztevnfmdriver/v1/test_update_vnf_vnfm_inst_id/vnfs/test_update_vnf_m_nf_inst_id/operate":
                [0, json.JSONEncoder().encode({"jobId": vnf_update_service.job_id}), "200"],
            "/api/ztevnfmdriver/v1/test_update_vnf_vnfm_inst_id/jobs/" + vnf_update_service.job_id + "?responseId=0":
                [0, json.JSONEncoder().encode(job_info), "200"],
        }

        def side_effect(*args):
            return mock_vals[args[4]]
        mock_call_req.side_effect = side_effect
        vnf_update_service.run()
        nfinst = NfInstModel.objects.get(nfinstid=self.nf_inst_id)
        self.assertEqual(nfinst.status, VNF_STATUS.ACTIVE)
        self.assertEqual(JobModel.objects.get(jobid=vnf_update_service.job_id).progress, JOB_PROGRESS.FINISHED)

    def test_update_vnf_thread_when_no_nf(self):
        NfInstModel.objects.all().delete()
        vnf_update_service = NFOperateService(self.nf_inst_id, self.data)
        vnf_update_service.run()
        self.assertEqual(JobModel.objects.get(jobid=vnf_update_service.job_id).progress, JOB_PROGRESS.ERROR)

    @mock.patch.object(time, "sleep")
    @mock.patch.object(restcall, "call_req")
    def test_update_vnf_thread_when_nf_update_failed(self, mock_call_req, mock_sleep):
        vnf_update_service = NFOperateService(self.nf_inst_id, self.data)
        job_info = {
            "jobId": vnf_update_service.job_id,
            "responsedescriptor": {"status": JOB_MODEL_STATUS.ERROR}
        }
        mock_vals = {
            "/external-system/esr-vnfm-list/esr-vnfm/test_update_vnf_vnfm_inst_id?depth=all":
                [0, json.JSONEncoder().encode(vnfm_info), "200"],
            "/api/ztevnfmdriver/v1/test_update_vnf_vnfm_inst_id/vnfs/test_update_vnf_m_nf_inst_id/operate":
                [0, json.JSONEncoder().encode({"jobId": vnf_update_service.job_id}), "200"],
            "/api/ztevnfmdriver/v1/test_update_vnf_vnfm_inst_id/jobs/" + vnf_update_service.job_id + "?responseId=0":
                [0, json.JSONEncoder().encode(job_info), "200"],
        }

        def side_effect(*args):
            return mock_vals[args[4]]

        mock_call_req.side_effect = side_effect
        vnf_update_service.run()
        nfinst = NfInstModel.objects.get(nfinstid=self.nf_inst_id)
        self.assertEqual(nfinst.status, VNF_STATUS.UPDATING)
        self.assertEqual(JobModel.objects.get(jobid=vnf_update_service.job_id).progress, JOB_PROGRESS.ERROR)


class TestVerifyVnfsViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = "/api/nslcm/v1/vnfonboarding"
        self.package_id = "test_verify_vnfs_package_id"
        self.nf_inst_id = "test_verify_vnfs"
        self.m_nf_inst_id = "test_verify_vnfs_m_nf_inst_id"
        self.vnfm_inst_id = "test_verify_vnfs_vnfm_inst_id"
        self.vnfd_model = {"metadata": {"vnfdId": "1"}}
        self.data = {
            "PackageID": self.package_id,
        }
        self.job_id = JobUtil.create_job(JOB_TYPE.VNF, "verify_vnfs", self.nf_inst_id)
        NfInstModel.objects.all().delete()
        NfInstModel.objects.create(package_id=self.package_id,
                                   nfinstid=self.nf_inst_id,
                                   vnfm_inst_id=self.vnfm_inst_id,
                                   status=VNF_STATUS.NULL,
                                   mnfinstid=self.m_nf_inst_id,
                                   vnfd_model=self.vnfd_model
                                   )

    def tearDown(self):
        NfInstModel.objects.all().delete()

    @mock.patch.object(VerifyVnfs, "run")
    def test_verify_vnfs_view(self, mock_run):
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(status.HTTP_202_ACCEPTED, response.status_code)

    def test_verify_vnfs_view_when_data_is_not_valid(self):
        response = self.client.post(self.url, data={})
        self.assertEqual(status.HTTP_409_CONFLICT, response.status_code)

    @mock.patch.object(time, "sleep")
    @mock.patch.object(restcall, "call_req")
    def test_verify_vnfs_thread(self, mock_call_req, mock_sleep):
        job_info_1 = {
            "jobId": "test_1",
            "responseDescriptor": {
                "status": JOB_MODEL_STATUS.FINISHED,
                "progress": 100,
                "responseId": 0,
                "statusDescription": ""
            }
        }
        job_info_2 = {
            "jobId": "test_2",
            "responseDescriptor": {
                "status": JOB_MODEL_STATUS.FINISHED,
                "progress": 100,
                "responseId": 0,
                "statusDescription": ""
            }
        }
        job_info_task = {
            "jobId": "task_id",
            "responseDescriptor": {
                "status": JOB_MODEL_STATUS.FINISHED,
                "progress": 100,
                "responseId": 0,
                "statusDescription": ""
            }
        }
        mock_vals = {
            "/api/nslcm/v1/vnfpackage":
                [0, json.JSONEncoder().encode(job_info_1), "200"],
            "/api/nslcm/v1/jobs/%s?responseId=%s" % ("test_1", 0):
                [0, json.JSONEncoder().encode(job_info_1), "200"],
            "/api/nslcm/v1/ns/ns_vnfs":
                [0, json.JSONEncoder().encode({"jobId": "test_2", "vnfInstId": ""}), "200"],
            "/api/nslcm/v1/jobs/%s?responseId=%s" % ("test_2", 0):
                [0, json.JSONEncoder().encode(job_info_2), "200"],
            "/openapi/vnfsdk/v1/functest/taskmanager/testtasks":
                [0, json.JSONEncoder().encode({"TaskID": "task_id"}), "200"],
            "/openapi/vnfsdk/v1/functest/taskmanager/testtasks/%s?responseId=%s" % ("task_id", 0):
                [0, json.JSONEncoder().encode(job_info_task), "200"],
            "/openapi/vnfsdk/v1/functest/taskmanager/testtasks/%s/result" % "task_id":
                [0, json.JSONEncoder().encode({"TaskID": "task_id"}), "200"],
        }

        def side_effect(*args):
            return mock_vals[args[4]]
        mock_call_req.side_effect = side_effect
        VerifyVnfs(self.data, self.job_id).run()
        self.assertEqual(JobModel.objects.get(jobid=self.job_id).progress, JOB_PROGRESS.FINISHED)

    @mock.patch.object(time, "sleep")
    @mock.patch.object(restcall, "call_req")
    def test_verify_vnfs_thread_when_failed_to_call_vnf_onboarding(self, mock_call_req, mock_sleep):
        mock_vals = {
            "/api/nslcm/v1/vnfpackage":
                [1, json.JSONEncoder().encode({}), "200"]
        }

        def side_effect(*args):
            return mock_vals[args[4]]

        mock_call_req.side_effect = side_effect
        VerifyVnfs(self.data, self.job_id).run()
        self.assertEqual(JobModel.objects.get(jobid=self.job_id).progress, JOB_PROGRESS.ERROR)

    @mock.patch.object(time, "sleep")
    @mock.patch.object(restcall, "call_req")
    def test_verify_vnfs_thread_when_do_on_boarding_failed_to_query_job(self, mock_call_req, mock_sleep):
        job_info_1 = {
            "jobId": "test_1",
            "responseDescriptor": {
                "status": JOB_MODEL_STATUS.FINISHED,
                "progress": 100,
                "responseId": 0,
                "statusDescription": ""
            }
        }
        mock_vals = {
            "/api/nslcm/v1/vnfpackage":
                [0, json.JSONEncoder().encode(job_info_1), "200"],
            "/api/nslcm/v1/jobs/%s?responseId=%s" % ("test_1", 0):
                [1, json.JSONEncoder().encode(job_info_1), "200"],
        }

        def side_effect(*args):
            return mock_vals[args[4]]

        mock_call_req.side_effect = side_effect
        VerifyVnfs(self.data, self.job_id).run()
        self.assertEqual(JobModel.objects.get(jobid=self.job_id).progress, JOB_PROGRESS.ERROR)

    @mock.patch.object(time, "sleep")
    @mock.patch.object(restcall, "call_req")
    def test_verify_vnfs_thread_when_do_on_boarding_job_does_not_exist(self, mock_call_req, mock_sleep):
        job_info_1 = {
            "jobId": "test_1",
        }
        mock_vals = {
            "/api/nslcm/v1/vnfpackage":
                [0, json.JSONEncoder().encode(job_info_1), "200"],
            "/api/nslcm/v1/jobs/%s?responseId=%s" % ("test_1", 0):
                [0, json.JSONEncoder().encode(job_info_1), "200"],
        }

        def side_effect(*args):
            return mock_vals[args[4]]

        mock_call_req.side_effect = side_effect
        VerifyVnfs(self.data, self.job_id).run()
        self.assertEqual(JobModel.objects.get(jobid=self.job_id).progress, JOB_PROGRESS.ERROR)

    @mock.patch.object(time, "sleep")
    @mock.patch.object(restcall, "call_req")
    def test_verify_vnfs_thread_when_do_on_boarding_job_process_error(self, mock_call_req, mock_sleep):
        job_info_1 = {
            "jobId": "test_1",
            "responseDescriptor": {
                "status": JOB_MODEL_STATUS.FINISHED,
                "progress": JOB_PROGRESS.ERROR,
                "responseId": 1,
                "statusDescription": "already onBoarded"
            }
        }
        job_info_2 = {
            "jobId": "test_2",
            "responseDescriptor": {
                "status": JOB_MODEL_STATUS.FINISHED,
                "progress": 100,
                "responseId": 0,
                "statusDescription": ""
            }
        }
        job_info_task = {
            "jobId": "task_id",
            "responseDescriptor": {
                "status": JOB_MODEL_STATUS.FINISHED,
                "progress": 100,
                "responseId": 0,
                "statusDescription": ""
            }
        }
        mock_vals = {
            "/api/nslcm/v1/vnfpackage":
                [0, json.JSONEncoder().encode(job_info_1), "200"],
            "/api/nslcm/v1/jobs/%s?responseId=%s" % ("test_1", 0):
                [0, json.JSONEncoder().encode(job_info_1), "200"],
            "/api/nslcm/v1/ns/ns_vnfs":
                [0, json.JSONEncoder().encode({"jobId": "test_2", "vnfInstId": ""}), "200"],
            "/api/nslcm/v1/jobs/%s?responseId=%s" % ("test_2", 0):
                [0, json.JSONEncoder().encode(job_info_2), "200"],
            "/openapi/vnfsdk/v1/functest/taskmanager/testtasks":
                [0, json.JSONEncoder().encode({"TaskID": "task_id"}), "200"],
            "/openapi/vnfsdk/v1/functest/taskmanager/testtasks/%s?responseId=%s" % ("task_id", 0):
                [0, json.JSONEncoder().encode(job_info_task), "200"],
            "/openapi/vnfsdk/v1/functest/taskmanager/testtasks/%s/result" % "task_id":
                [0, json.JSONEncoder().encode({"TaskID": "task_id"}), "200"],
        }

        def side_effect(*args):
            return mock_vals[args[4]]

        mock_call_req.side_effect = side_effect
        VerifyVnfs(self.data, self.job_id).run()
        self.assertEqual(JobModel.objects.get(jobid=self.job_id).progress, JOB_PROGRESS.FINISHED)

    @mock.patch.object(time, "sleep")
    @mock.patch.object(restcall, "call_req")
    def test_verify_vnfs_thread_when_failed_to_call_inst_vnf(self, mock_call_req, mock_sleep):
        job_info_1 = {
            "jobId": "test_1",
            "responseDescriptor": {
                "status": JOB_MODEL_STATUS.FINISHED,
                "progress": 100,
                "responseId": 0,
                "statusDescription": ""
            }
        }
        mock_vals = {
            "/api/nslcm/v1/vnfpackage":
                [0, json.JSONEncoder().encode(job_info_1), "200"],
            "/api/nslcm/v1/jobs/%s?responseId=%s" % ("test_1", 0):
                [0, json.JSONEncoder().encode(job_info_1), "200"],
            "/api/nslcm/v1/ns/ns_vnfs":
                [1, json.JSONEncoder().encode({"jobId": "test_2", "vnfInstId": ""}), "200"],
        }

        def side_effect(*args):
            return mock_vals[args[4]]

        mock_call_req.side_effect = side_effect
        VerifyVnfs(self.data, self.job_id).run()
        self.assertEqual(JobModel.objects.get(jobid=self.job_id).progress, JOB_PROGRESS.ERROR)

    @mock.patch.object(time, "sleep")
    @mock.patch.object(restcall, "call_req")
    def test_verify_vnfs_thread_when_do_term_vnf_job_process_error(self, mock_call_req, mock_sleep):
        job_info_1 = {
            "jobId": "test_1",
            "responseDescriptor": {
                "status": JOB_MODEL_STATUS.FINISHED,
                "progress": 100,
                "responseId": 0,
                "statusDescription": ""
            }
        }
        job_info_2 = {
            "jobId": "test_2",
            "responseDescriptor": {
                "status": JOB_MODEL_STATUS.FINISHED,
                "progress": JOB_PROGRESS.ERROR,
                "responseId": 0,
                "statusDescription": ""
            }
        }
        mock_vals = {
            "/api/nslcm/v1/vnfpackage":
                [0, json.JSONEncoder().encode(job_info_1), "200"],
            "/api/nslcm/v1/jobs/%s?responseId=%s" % ("test_1", 0):
                [0, json.JSONEncoder().encode(job_info_1), "200"],
            "/api/nslcm/v1/ns/ns_vnfs":
                [0, json.JSONEncoder().encode({"jobId": "test_2", "vnfInstId": ""}), "200"],
            "/api/nslcm/v1/jobs/%s?responseId=%s" % ("test_2", 0):
                [0, json.JSONEncoder().encode(job_info_2), "200"],
        }

        def side_effect(*args):
            return mock_vals[args[4]]

        mock_call_req.side_effect = side_effect
        VerifyVnfs(self.data, self.job_id).run()
        self.assertEqual(JobModel.objects.get(jobid=self.job_id).progress, JOB_PROGRESS.ERROR)

    @mock.patch.object(time, "sleep")
    @mock.patch.object(restcall, "call_req")
    def test_verify_vnfs_thread_when_failed_to_call_func_test(self, mock_call_req, mock_sleep):
        job_info_1 = {
            "jobId": "test_1",
            "responseDescriptor": {
                "status": JOB_MODEL_STATUS.FINISHED,
                "progress": 100,
                "responseId": 0,
                "statusDescription": ""
            }
        }
        job_info_2 = {
            "jobId": "test_2",
            "responseDescriptor": {
                "status": JOB_MODEL_STATUS.FINISHED,
                "progress": 100,
                "responseId": 0,
                "statusDescription": ""
            }
        }
        mock_vals = {
            "/api/nslcm/v1/vnfpackage":
                [0, json.JSONEncoder().encode(job_info_1), "200"],
            "/api/nslcm/v1/jobs/%s?responseId=%s" % ("test_1", 0):
                [0, json.JSONEncoder().encode(job_info_1), "200"],
            "/api/nslcm/v1/ns/ns_vnfs":
                [0, json.JSONEncoder().encode({"jobId": "test_2", "vnfInstId": ""}), "200"],
            "/api/nslcm/v1/jobs/%s?responseId=%s" % ("test_2", 0):
                [0, json.JSONEncoder().encode(job_info_2), "200"],
            "/openapi/vnfsdk/v1/functest/taskmanager/testtasks":
                [1, json.JSONEncoder().encode({"TaskID": "task_id"}), "200"]
        }

        def side_effect(*args):
            return mock_vals[args[4]]

        mock_call_req.side_effect = side_effect
        VerifyVnfs(self.data, self.job_id).run()
        self.assertEqual(JobModel.objects.get(jobid=self.job_id).progress, JOB_PROGRESS.ERROR)

    @mock.patch.object(time, "sleep")
    @mock.patch.object(restcall, "call_req")
    def test_verify_vnfs_thread_when_do_func_test_failed_query_job(self, mock_call_req, mock_sleep):
        job_info_1 = {
            "jobId": "test_1",
            "responseDescriptor": {
                "status": JOB_MODEL_STATUS.FINISHED,
                "progress": 100,
                "responseId": 0,
                "statusDescription": ""
            }
        }
        job_info_2 = {
            "jobId": "test_2",
            "responseDescriptor": {
                "status": JOB_MODEL_STATUS.FINISHED,
                "progress": 100,
                "responseId": 0,
                "statusDescription": ""
            }
        }
        job_info_task = {
            "jobId": "task_id",
            "responseDescriptor": {
                "status": JOB_MODEL_STATUS.FINISHED,
                "progress": 100,
                "responseId": 0,
                "statusDescription": ""
            }
        }
        mock_vals = {
            "/api/nslcm/v1/vnfpackage":
                [0, json.JSONEncoder().encode(job_info_1), "200"],
            "/api/nslcm/v1/jobs/%s?responseId=%s" % ("test_1", 0):
                [0, json.JSONEncoder().encode(job_info_1), "200"],
            "/api/nslcm/v1/ns/ns_vnfs":
                [0, json.JSONEncoder().encode({"jobId": "test_2", "vnfInstId": ""}), "200"],
            "/api/nslcm/v1/jobs/%s?responseId=%s" % ("test_2", 0):
                [0, json.JSONEncoder().encode(job_info_2), "200"],
            "/openapi/vnfsdk/v1/functest/taskmanager/testtasks":
                [0, json.JSONEncoder().encode({"TaskID": "task_id"}), "200"],
            "/openapi/vnfsdk/v1/functest/taskmanager/testtasks/%s?responseId=%s" % ("task_id", 0):
                [1, json.JSONEncoder().encode(job_info_task), "200"],
        }

        def side_effect(*args):
            return mock_vals[args[4]]

        mock_call_req.side_effect = side_effect
        VerifyVnfs(self.data, self.job_id).run()
        self.assertEqual(JobModel.objects.get(jobid=self.job_id).progress, JOB_PROGRESS.ERROR)

    @mock.patch.object(time, "sleep")
    @mock.patch.object(restcall, "call_req")
    def test_verify_vnfs_thread_when_do_func_test_job_does_not_exist(self, mock_call_req, mock_sleep):
        job_info_1 = {
            "jobId": "test_1",
            "responseDescriptor": {
                "status": JOB_MODEL_STATUS.FINISHED,
                "progress": 100,
                "responseId": 0,
                "statusDescription": ""
            }
        }
        job_info_2 = {
            "jobId": "test_2",
            "responseDescriptor": {
                "status": JOB_MODEL_STATUS.FINISHED,
                "progress": 100,
                "responseId": 0,
                "statusDescription": ""
            }
        }
        job_info_task = {
            "jobId": "task_id",
        }
        mock_vals = {
            "/api/nslcm/v1/vnfpackage":
                [0, json.JSONEncoder().encode(job_info_1), "200"],
            "/api/nslcm/v1/jobs/%s?responseId=%s" % ("test_1", 0):
                [0, json.JSONEncoder().encode(job_info_1), "200"],
            "/api/nslcm/v1/ns/ns_vnfs":
                [0, json.JSONEncoder().encode({"jobId": "test_2", "vnfInstId": ""}), "200"],
            "/api/nslcm/v1/jobs/%s?responseId=%s" % ("test_2", 0):
                [0, json.JSONEncoder().encode(job_info_2), "200"],
            "/openapi/vnfsdk/v1/functest/taskmanager/testtasks":
                [0, json.JSONEncoder().encode({"TaskID": "task_id"}), "200"],
            "/openapi/vnfsdk/v1/functest/taskmanager/testtasks/%s?responseId=%s" % ("task_id", 0):
                [0, json.JSONEncoder().encode(job_info_task), "200"],
            "/openapi/vnfsdk/v1/functest/taskmanager/testtasks/%s/result" % "task_id":
                [0, json.JSONEncoder().encode({"TaskID": "task_id"}), "200"],
        }

        def side_effect(*args):
            return mock_vals[args[4]]

        mock_call_req.side_effect = side_effect
        VerifyVnfs(self.data, self.job_id).run()
        self.assertEqual(JobModel.objects.get(jobid=self.job_id).progress, JOB_PROGRESS.ERROR)

    @mock.patch.object(time, "sleep")
    @mock.patch.object(restcall, "call_req")
    def test_verify_vnfs_thread_when_do_func_test_job_process_error(self, mock_call_req, mock_sleep):
        job_info_1 = {
            "jobId": "test_1",
            "responseDescriptor": {
                "status": JOB_MODEL_STATUS.FINISHED,
                "progress": 100,
                "responseId": 0,
                "statusDescription": ""
            }
        }
        job_info_2 = {
            "jobId": "test_2",
            "responseDescriptor": {
                "status": JOB_MODEL_STATUS.FINISHED,
                "progress": 100,
                "responseId": 0,
                "statusDescription": ""
            }
        }
        job_info_task = {
            "jobId": "task_id",
            "responseDescriptor": {
                "status": JOB_MODEL_STATUS.ERROR,
                "progress": JOB_PROGRESS.ERROR,
                "responseId": 1,
                "statusDescription": "already onBoarded"
            }
        }
        mock_vals = {
            "/api/nslcm/v1/vnfpackage":
                [0, json.JSONEncoder().encode(job_info_1), "200"],
            "/api/nslcm/v1/jobs/%s?responseId=%s" % ("test_1", 0):
                [0, json.JSONEncoder().encode(job_info_1), "200"],
            "/api/nslcm/v1/ns/ns_vnfs":
                [0, json.JSONEncoder().encode({"jobId": "test_2", "vnfInstId": ""}), "200"],
            "/api/nslcm/v1/jobs/%s?responseId=%s" % ("test_2", 0):
                [0, json.JSONEncoder().encode(job_info_2), "200"],
            "/openapi/vnfsdk/v1/functest/taskmanager/testtasks":
                [0, json.JSONEncoder().encode({"TaskID": "task_id"}), "200"],
            "/openapi/vnfsdk/v1/functest/taskmanager/testtasks/%s?responseId=%s" % ("task_id", 0):
                [0, json.JSONEncoder().encode(job_info_task), "200"],
            "/openapi/vnfsdk/v1/functest/taskmanager/testtasks/%s/result" % "task_id":
                [0, json.JSONEncoder().encode({"TaskID": "task_id"}), "200"],
        }

        def side_effect(*args):
            return mock_vals[args[4]]

        mock_call_req.side_effect = side_effect
        VerifyVnfs(self.data, self.job_id).run()
        self.assertEqual(JobModel.objects.get(jobid=self.job_id).progress, JOB_PROGRESS.FINISHED)

    @mock.patch.object(time, "sleep")
    @mock.patch.object(restcall, "call_req")
    def test_verify_vnfs_thread_when_do_func_test_failed_to_get_func_test_result(self, mock_call_req, mock_sleep):
        job_info_1 = {
            "jobId": "test_1",
            "responseDescriptor": {
                "status": JOB_MODEL_STATUS.FINISHED,
                "progress": 100,
                "responseId": 0,
                "statusDescription": ""
            }
        }
        job_info_2 = {
            "jobId": "test_2",
            "responseDescriptor": {
                "status": JOB_MODEL_STATUS.FINISHED,
                "progress": 100,
                "responseId": 0,
                "statusDescription": ""
            }
        }
        job_info_task = {
            "jobId": "task_id",
            "responseDescriptor": {
                "status": JOB_MODEL_STATUS.FINISHED,
                "progress": 100,
                "responseId": 1,
                "statusDescription": "already onBoarded"
            }
        }
        mock_vals = {
            "/api/nslcm/v1/vnfpackage":
                [0, json.JSONEncoder().encode(job_info_1), "200"],
            "/api/nslcm/v1/jobs/%s?responseId=%s" % ("test_1", 0):
                [0, json.JSONEncoder().encode(job_info_1), "200"],
            "/api/nslcm/v1/ns/ns_vnfs":
                [0, json.JSONEncoder().encode({"jobId": "test_2", "vnfInstId": ""}), "200"],
            "/api/nslcm/v1/jobs/%s?responseId=%s" % ("test_2", 0):
                [0, json.JSONEncoder().encode(job_info_2), "200"],
            "/openapi/vnfsdk/v1/functest/taskmanager/testtasks":
                [0, json.JSONEncoder().encode({"TaskID": "task_id"}), "200"],
            "/openapi/vnfsdk/v1/functest/taskmanager/testtasks/%s?responseId=%s" % ("task_id", 0):
                [0, json.JSONEncoder().encode(job_info_task), "200"],
            "/openapi/vnfsdk/v1/functest/taskmanager/testtasks/%s/result" % "task_id":
                [1, json.JSONEncoder().encode({"TaskID": "task_id"}), "200"],
        }

        def side_effect(*args):
            return mock_vals[args[4]]

        mock_call_req.side_effect = side_effect
        VerifyVnfs(self.data, self.job_id).run()
        self.assertEqual(JobModel.objects.get(jobid=self.job_id).progress, JOB_PROGRESS.ERROR)


class TestLcmNotifyViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.data = {
            "status": "START",
            "operation": "Instantiate",
            "jobId": "",
            "vnfdmodule": "",
            "affectedVnfc": [{"vnfcInstanceId": "vnfc_instance_id",
                              "vduId": "vdu_id",
                              "changeType": VNFC_CHANGE_TYPE.ADDED,
                              "vimId": "vim_id",
                              "vmId": "vm_id",
                              "vmName": "vm_name"
                              }],
            "affectedVl": [{"vlInstanceId": "vl_instance_id",
                            "vldId": "vld_id",
                            "changeType": VNFC_CHANGE_TYPE.ADDED,
                            "networkResource": {
                                "resourceType": NETWORK_RESOURCE_TYPE.NETWORK,
                                "resourceId": "resource_id",
                                "resourceName": "resource_name"
                            }
                            }],
            "affectedCp": [{"changeType": VNFC_CHANGE_TYPE.ADDED,
                            "virtualLinkInstanceId": "virtual_link_instance_id",
                            "cpInstanceId": "cp_instance_id",
                            "cpdId": "cpd_id",
                            "ownerType": 0,
                            "ownerId": "owner_id",
                            "portResource": {
                                "vimId": "vim_id",
                                "resourceId": "resource_id",
                                "resourceName": "resource_name",
                                "tenant": "tenant",
                                "ipAddress": "ip_address",
                                "macAddress": "mac_address",
                                "instId": "inst_id"
                            }
                            }],
            "affectedVirtualStorage": [{}]
        }
        self.nf_inst_id = "test_lcm_notify"
        self.m_nf_inst_id = "test_lcm_notify_m_nf_inst_id"
        self.vnfm_inst_id = "test_lcm_notify_vnfm_inst_id"
        self.vnfd_model = {"metadata": {"vnfdId": "1"}}
        self.url = "/api/nslcm/v1/ns/%s/vnfs/%s/Notify" % (self.m_nf_inst_id, self.vnfm_inst_id)
        NfInstModel.objects.all().delete()
        NfInstModel.objects.create(nfinstid=self.nf_inst_id,
                                   vnfm_inst_id=self.vnfm_inst_id,
                                   status=VNF_STATUS.NULL,
                                   mnfinstid=self.m_nf_inst_id,
                                   vnfd_model=self.vnfd_model
                                   )

    def tearDown(self):
        NfInstModel.objects.all().delete()
        VNFCInstModel.objects.all().delete()
        VmInstModel.objects.all().delete()
        VLInstModel.objects.all().delete()
        PortInstModel.objects.all().delete()
        CPInstModel.objects.all().delete()

    def test_lcm_notify_view_when_change_type_is_added(self):
        NotifyLcm(self.vnfm_inst_id, self.m_nf_inst_id, self.data).do_biz()
        vnfc_inst = VNFCInstModel.objects.get(vnfcinstanceid="vnfc_instance_id", vduid="vdu_id", vmid="vm_id",
                                              nfinstid=self.nf_inst_id)
        self.assertIsInstance(vnfc_inst, VNFCInstModel)
        vm_inst = VmInstModel.objects.get(vmid="vm_id", vimid="vim_id", resouceid="vm_id", insttype=INST_TYPE.VNF,
                                          instid=self.nf_inst_id, vmname="vm_name", hostid='1')
        self.assertIsInstance(vm_inst, VmInstModel)
        vl_inst = VLInstModel.objects.get(vlinstanceid="vl_instance_id", vldid="vld_id", vlinstancename="resource_name",
                                          ownertype=0, ownerid=self.nf_inst_id, relatednetworkid="resource_id",
                                          vltype=0)
        self.assertIsInstance(vl_inst, VLInstModel)
        port_inst = PortInstModel.objects.get(networkid='unknown', subnetworkid='unknown', vimid="vim_id",
                                              resourceid="resource_id", name="resource_name", instid="inst_id",
                                              cpinstanceid="cp_instance_id", bandwidth='unknown',
                                              operationalstate='active', ipaddress="ip_address",
                                              macaddress='mac_address', floatipaddress='unknown',
                                              serviceipaddress='unknown', typevirtualnic='unknown',
                                              sfcencapsulation='gre', direction='unknown', tenant="tenant")
        self.assertIsInstance(port_inst, PortInstModel)
        cp_inst = CPInstModel.objects.get(cpinstanceid="cp_instance_id", cpdid="cpd_id", ownertype=0,
                                          ownerid=self.nf_inst_id, relatedtype=2, status='active')
        self.assertIsInstance(cp_inst, CPInstModel)

    def test_lcm_notify_view__when_change_type_is_added_when_nf_not_exists(self):
        NfInstModel.objects.all().delete()
        data = {
            "status": "START",
            "operation": "Instantiate",
            "jobId": "",
            "vnfdmodule": "",
        }
        try:
            NotifyLcm(self.vnfm_inst_id, self.m_nf_inst_id, data).do_biz()
            self.assertEqual(1, 0)
        except Exception:
            self.assertEqual(1, 1)

    def test_lcm_notify_view_when_change_type_is_removeed(self):
        VNFCInstModel.objects.create(vnfcinstanceid="vnfc_instance_id")
        VLInstModel.objects.create(vlinstanceid="vl_instance_id", ownertype=0)
        CPInstModel.objects.create(cpinstanceid="cp_instance_id", cpdid="cpd_id", ownertype=0, ownerid=self.nf_inst_id,
                                   relatedtype=2, relatedport="related_port", status="active")
        data = {
            "status": "START",
            "operation": "Instantiate",
            "jobId": "",
            "vnfdmodule": "",
            "affectedVnfc": [{"vnfcInstanceId": "vnfc_instance_id",
                              "vduId": "vdu_id",
                              "changeType": VNFC_CHANGE_TYPE.REMOVED,
                              "vimId": "vim_id",
                              "vmId": "vm_id",
                              "vmName": "vm_name"
                              }],
            "affectedVl": [{"vlInstanceId": "vl_instance_id",
                            "vldId": "vld_id",
                            "changeType": VNFC_CHANGE_TYPE.REMOVED,
                            "networkResource": {
                                "resourceType": NETWORK_RESOURCE_TYPE.NETWORK,
                                "resourceId": "resource_id",
                                "resourceName": "resource_name"
                            }
                            }],
            "affectedCp": [{"changeType": VNFC_CHANGE_TYPE.REMOVED,
                            "virtualLinkInstanceId": "virtual_link_instance_id",
                            "cpInstanceId": "cp_instance_id",
                            "cpdId": "cpd_id",
                            "ownerType": 0,
                            "ownerId": "owner_id",
                            "portResource": {
                                "vimId": "vim_id",
                                "resourceId": "resource_id",
                                "resourceName": "resource_name",
                                "tenant": "tenant",
                                "ipAddress": "ip_address",
                                "macAddress": "mac_address",
                                "instId": "inst_id"
                            }
                            }],
            "affectedVirtualStorage": [{}]
        }
        NotifyLcm(self.vnfm_inst_id, self.m_nf_inst_id, data).do_biz()
        vnfc_inst = VNFCInstModel.objects.filter(vnfcinstanceid="vnfc_instance_id")
        self.assertEqual(len(vnfc_inst), 0)
        vl_inst = VLInstModel.objects.filter(vlinstanceid="vl_instance_id")
        self.assertEqual(len(vl_inst), 0)
        port_inst = PortInstModel.objects.get(networkid='unknown', subnetworkid='unknown', vimid="vim_id",
                                              resourceid="resource_id", name="resource_name", instid="inst_id",
                                              cpinstanceid="cp_instance_id", bandwidth='unknown',
                                              operationalstate='active', ipaddress="ip_address",
                                              macaddress='mac_address', floatipaddress='unknown',
                                              serviceipaddress='unknown', typevirtualnic='unknown',
                                              sfcencapsulation='gre', direction='unknown', tenant="tenant")
        self.assertIsInstance(port_inst, PortInstModel)
        cp_inst = CPInstModel.objects.filter(cpinstanceid="cp_instance_id")
        self.assertEqual(len(cp_inst), 0)

    def test_lcm_notify_view_when_change_type_is_modified(self):
        VNFCInstModel.objects.create(vnfcinstanceid="vnfc_instance_id")
        VLInstModel.objects.create(vlinstanceid="vl_instance_id", ownertype=0)
        CPInstModel.objects.create(cpinstanceid="cp_instance_id", cpdid="cpd_id", ownertype=0, ownerid=self.nf_inst_id,
                                   relatedtype=2, relatedport="related_port")
        data = {
            "status": "START",
            "operation": "Instantiate",
            "jobId": "",
            "vnfdmodule": "",
            "affectedVnfc": [{"vnfcInstanceId": "vnfc_instance_id",
                              "vduId": "vdu_id",
                              "changeType": VNFC_CHANGE_TYPE.MODIFIED,
                              "vimId": "vim_id",
                              "vmId": "vm_id",
                              "vmName": "vm_name"
                              }],
            "affectedVl": [{"vlInstanceId": "vl_instance_id",
                            "vldId": "vld_id",
                            "changeType": VNFC_CHANGE_TYPE.MODIFIED,
                            "networkResource": {
                                "resourceType": NETWORK_RESOURCE_TYPE.NETWORK,
                                "resourceId": "resource_id",
                                "resourceName": "resource_name"
                            }
                            }],
            "affectedCp": [{"changeType": VNFC_CHANGE_TYPE.MODIFIED,
                            "virtualLinkInstanceId": "virtual_link_instance_id",
                            "cpInstanceId": "cp_instance_id",
                            "cpdId": "cpd_id",
                            "ownerType": 0,
                            "ownerId": "owner_id",
                            "portResource": {
                                "vimId": "vim_id",
                                "resourceId": "resource_id",
                                "resourceName": "resource_name",
                                "tenant": "tenant",
                                "ipAddress": "ip_address",
                                "macAddress": "mac_address",
                                "instId": "inst_id"
                            }
                            }],
            "affectedVirtualStorage": [{}]
        }
        NotifyLcm(self.vnfm_inst_id, self.m_nf_inst_id, data).do_biz()
        vnfc_inst = VNFCInstModel.objects.get(vnfcinstanceid="vnfc_instance_id", vduid="vdu_id", vmid="vm_id",
                                              nfinstid=self.nf_inst_id)
        self.assertIsInstance(vnfc_inst, VNFCInstModel)
        vl_inst = VLInstModel.objects.get(vlinstanceid="vl_instance_id", vldid="vld_id", vlinstancename="resource_name",
                                          ownertype=0, ownerid=self.nf_inst_id, relatednetworkid="resource_id",
                                          vltype=0)
        self.assertIsInstance(vl_inst, VLInstModel)
        port_inst = PortInstModel.objects.get(networkid='unknown', subnetworkid='unknown', vimid="vim_id",
                                              resourceid="resource_id", name="resource_name", instid="inst_id",
                                              cpinstanceid="cp_instance_id", bandwidth='unknown',
                                              operationalstate='active', ipaddress="ip_address",
                                              macaddress='mac_address', floatipaddress='unknown',
                                              serviceipaddress='unknown', typevirtualnic='unknown',
                                              sfcencapsulation='gre', direction='unknown', tenant="tenant")
        self.assertIsInstance(port_inst, PortInstModel)
        cp_inst = CPInstModel.objects.get(cpinstanceid="cp_instance_id", cpdid="cpd_id", ownertype=0,
                                          ownerid=self.nf_inst_id, relatedtype=2)
        self.assertIsInstance(cp_inst, CPInstModel)


class TestVnfNotifyView(TestCase):
    def setUp(self):
        self.client = Client()
        self.nf_inst_id = "test_vnf_notify"
        self.m_nf_inst_id = "test_vnf_notify_m_nf_inst_id"
        self.vnfm_inst_id = "test_vnf_notify_vnfm_inst_id"
        self.vnfd_model = {"metadata": {"vnfdId": "1"}}
        self.url = "/api/nslcm/v2/ns/%s/vnfs/%s/Notify" % (self.vnfm_inst_id, self.m_nf_inst_id)
        self.data = {
            "id": "1111",
            "notificationType": "VnfLcmOperationOccurrenceNotification",
            "subscriptionId": "1111",
            "timeStamp": "1111",
            "notificationStatus": "START",
            "operationState": "STARTING",
            "vnfInstanceId": self.nf_inst_id,
            "operation": "INSTANTIATE",
            "isAutomaticInvocation": "1111",
            "vnfLcmOpOccId": "1111",
            "affectedVnfcs": [{"id": "vnfc_instance_id",
                              "vduId": "vdu_id",
                               "changeType": VNFC_CHANGE_TYPE.ADDED,
                               "computeResource": {
                                  "vimConnectionId": "vim_connection_id",
                                  "resourceId": "resource_id"
                               }
                               }],
            "affectedVirtualLinks": [{"id": "vl_instance_id",
                                      "virtualLinkDescId": "virtual_link_desc_id",
                                      "changeType": VNFC_CHANGE_TYPE.ADDED,
                                      "networkResource": {
                                          "vimLevelResourceType": "network",
                                          "resourceId": "resource_id"
                                      }}],
            "changedExtConnectivity": [{"id": "virtual_link_instance_id",
                                        "extLinkPorts": [{"cpInstanceId": "cp_instance_id",
                                                          "id": "cpd_id",
                                                          "resourceHandle": {
                                                              "vimConnectionId": "vim_connection_id",
                                                              "resourceId": "resource_id",
                                                              "resourceProviderId": "resourceProviderId",
                                                              "tenant": "tenant",
                                                              "ipAddress": "ipAddress",
                                                              "macAddress": "macAddress",
                                                              "instId": "instId",
                                                              "networkId": "networkId",
                                                              "subnetId": "subnetId"
                                                          }
                                                          }],
                                        }]
        }
        NfInstModel.objects.all().delete()
        VNFCInstModel.objects.all().delete()
        VmInstModel.objects.all().delete()
        NfInstModel.objects.create(nfinstid=self.nf_inst_id,
                                   vnfm_inst_id=self.vnfm_inst_id,
                                   status=VNF_STATUS.NULL,
                                   mnfinstid=self.m_nf_inst_id,
                                   vnfd_model=self.vnfd_model
                                   )

    def tearDown(self):
        NfInstModel.objects.all().delete()
        VNFCInstModel.objects.all().delete()
        VmInstModel.objects.all().delete()
        VLInstModel.objects.all().delete()
        PortInstModel.objects.all().delete()
        CPInstModel.objects.all().delete()

    def test_handle_vnf_lcm_ooc_notification_when_change_type_is_added(self):
        # response = self.client.post(self.url, data=self.data)
        HandleVnfLcmOocNotification(self.vnfm_inst_id, self.m_nf_inst_id, self.data).do_biz()
        vnfc_inst = VNFCInstModel.objects.get(vnfcinstanceid="vnfc_instance_id", vduid="vdu_id",
                                              nfinstid=self.nf_inst_id, vmid="resource_id")
        self.assertIsInstance(vnfc_inst, VNFCInstModel)
        vm_inst = VmInstModel.objects.get(vmid="resource_id", vimid="vim_connection_id", resouceid="resource_id",
                                          insttype=INST_TYPE.VNF, instid=self.nf_inst_id, vmname="resource_id",
                                          hostid='1')
        self.assertIsInstance(vm_inst, VmInstModel)
        vl_inst = VLInstModel.objects.get(vlinstanceid="vl_instance_id", vldid="virtual_link_desc_id",
                                          vlinstancename="resource_id", ownertype=0, ownerid=self.nf_inst_id,
                                          relatednetworkid="resource_id", vltype=0)
        self.assertIsInstance(vl_inst, VLInstModel)
        port_inst = PortInstModel.objects.get(networkid='networkId', subnetworkid='subnetId', vimid="vim_connection_id",
                                              resourceid="resource_id", name="resourceProviderId", instid="instId",
                                              cpinstanceid="cp_instance_id", bandwidth='unknown',
                                              operationalstate='active', ipaddress="ipAddress", macaddress='macAddress',
                                              floatipaddress='unknown', serviceipaddress='unknown',
                                              typevirtualnic='unknown', sfcencapsulation='gre', direction='unknown',
                                              tenant="tenant")
        self.assertIsInstance(port_inst, PortInstModel)
        cp_inst = CPInstModel.objects.get(cpinstanceid="cp_instance_id", cpdid="cpd_id", ownertype=0,
                                          ownerid=self.nf_inst_id, relatedtype=2, status='active')
        self.assertIsInstance(cp_inst, CPInstModel)

    def test_handle_vnf_lcm_ooc_notification_when_change_type_is_added_when_nf_not_exists(self):
        data = {
            "id": "1111",
            "notificationType": "VnfLcmOperationOccurrenceNotification",
            "subscriptionId": "1111",
            "timeStamp": "1111",
            "notificationStatus": "START",
            "operationState": "STARTING",
            "vnfInstanceId": "nf_not_exists",
            "operation": "INSTANTIATE",
            "isAutomaticInvocation": "1111",
            "vnfLcmOpOccId": "1111"
        }
        try:
            HandleVnfLcmOocNotification(self.vnfm_inst_id, self.m_nf_inst_id, data).do_biz()
            self.assertEqual(1, 0)
        except Exception:
            self.assertEqual(1, 1)

    def test_handle_vnf_lcm_ooc_notification_when_change_type_is_removed(self):
        VNFCInstModel.objects.create(vnfcinstanceid="vnfc_instance_id")
        VLInstModel.objects.create(vlinstanceid="vl_instance_id", ownertype=0)
        data = {
            "id": "1111",
            "notificationType": "VnfLcmOperationOccurrenceNotification",
            "subscriptionId": "1111",
            "timeStamp": "1111",
            "notificationStatus": "START",
            "operationState": "STARTING",
            "vnfInstanceId": self.nf_inst_id,
            "operation": "INSTANTIATE",
            "isAutomaticInvocation": "1111",
            "vnfLcmOpOccId": "1111",
            "affectedVnfcs": [{"id": "vnfc_instance_id",
                               "vduId": "vdu_id",
                               "changeType": VNFC_CHANGE_TYPE.REMOVED,
                               "computeResource": {
                                   "vimConnectionId": "vim_connection_id",
                                   "resourceId": "resource_id"
                               }}],
            "affectedVirtualLinks": [{"id": "vl_instance_id",
                                      "virtualLinkDescId": "virtual_link_desc_id",
                                      "changeType": VNFC_CHANGE_TYPE.REMOVED,
                                      "networkResource": {
                                          "vimLevelResourceType": "network",
                                          "resourceId": "resource_id"
                                      }}]
        }
        HandleVnfLcmOocNotification(self.vnfm_inst_id, self.m_nf_inst_id, data).do_biz()
        vnfc_inst = VNFCInstModel.objects.filter(vnfcinstanceid="vnfc_instance_id")
        self.assertEqual(len(vnfc_inst), 0)
        vl_inst = VLInstModel.objects.filter(vlinstanceid="vl_instance_id")
        self.assertEqual(len(vl_inst), 0)

    def test_handle_vnf_lcm_ooc_notification_when_change_type_is_modified(self):
        VNFCInstModel.objects.create(vnfcinstanceid="vnfc_instance_id")
        VLInstModel.objects.create(vlinstanceid="vl_instance_id", ownertype=0)
        data = {
            "id": "1111",
            "notificationType": "VnfLcmOperationOccurrenceNotification",
            "subscriptionId": "1111",
            "timeStamp": "1111",
            "notificationStatus": "START",
            "operationState": "STARTING",
            "vnfInstanceId": self.nf_inst_id,
            "operation": "INSTANTIATE",
            "isAutomaticInvocation": "1111",
            "vnfLcmOpOccId": "1111",
            "affectedVnfcs": [{"id": "vnfc_instance_id",
                               "vduId": "vdu_id",
                               "changeType": VNFC_CHANGE_TYPE.MODIFIED,
                               "computeResource": {
                                   "vimConnectionId": "vim_connection_id",
                                   "resourceId": "resource_id"
                               }}],
            "affectedVirtualLinks": [{"id": "vl_instance_id",
                                      "virtualLinkDescId": "virtual_link_desc_id",
                                      "changeType": VNFC_CHANGE_TYPE.MODIFIED,
                                      "networkResource": {
                                          "vimLevelResourceType": "network",
                                          "resourceId": "resource_id"
                                      }}],
            "changedExtConnectivity": [{"id": "virtual_link_instance_id",
                                        "extLinkPorts": [{"cpInstanceId": "cp_instance_id",
                                                          "id": "cpd_id",
                                                          "resourceHandle": {
                                                              "vimConnectionId": "vim_connection_id",
                                                              "resourceId": "resource_id",
                                                              "resourceProviderId": "resourceProviderId",
                                                              "tenant": "tenant",
                                                              "ipAddress": "ipAddress",
                                                              "macAddress": "macAddress",
                                                              "instId": "instId",
                                                              "networkId": "networkId",
                                                              "subnetId": "subnetId"
                                                          }
                                                          }],
                                        }]
        }
        HandleVnfLcmOocNotification(self.vnfm_inst_id, self.m_nf_inst_id, data).do_biz()
        vnfc_inst = VNFCInstModel.objects.get(vnfcinstanceid="vnfc_instance_id", vduid="vdu_id",
                                              nfinstid=self.nf_inst_id, vmid="resource_id")
        self.assertIsInstance(vnfc_inst, VNFCInstModel)
        vl_inst = VLInstModel.objects.get(vlinstanceid="vl_instance_id", vldid="virtual_link_desc_id",
                                          vlinstancename="resource_id", ownertype=0, ownerid=self.nf_inst_id,
                                          relatednetworkid="resource_id", vltype=0)
        self.assertIsInstance(vl_inst, VLInstModel)
        port_inst = PortInstModel.objects.get(networkid='networkId', subnetworkid='subnetId', vimid="vim_connection_id",
                                              resourceid="resource_id", name="resourceProviderId", instid="instId",
                                              cpinstanceid="cp_instance_id", bandwidth='unknown',
                                              operationalstate='active', ipaddress="ipAddress", macaddress='macAddress',
                                              floatipaddress='unknown', serviceipaddress='unknown',
                                              typevirtualnic='unknown', sfcencapsulation='gre', direction='unknown',
                                              tenant="tenant")
        self.assertIsInstance(port_inst, PortInstModel)
        cp_inst = CPInstModel.objects.get(cpinstanceid="cp_instance_id", cpdid="cpd_id", ownertype=0,
                                          ownerid=self.nf_inst_id, relatedtype=2, status='active')
        self.assertIsInstance(cp_inst, CPInstModel)

    def test_handle_vnf_identifier_creation_notification(self):
        vnfm_id = "vnfm_id"
        vnf_instance_id = "vnf_instance_id"
        data = {
            "timeStamp": "20190809",
        }
        HandleVnfIdentifierCreationNotification(vnfm_id, vnf_instance_id, data).do_biz()
        nf_inst = NfInstModel.objects.get(mnfinstid=vnf_instance_id, vnfm_inst_id=vnfm_id, create_time="20190809")
        self.assertIsInstance(nf_inst, NfInstModel)

    def test_handle_vnf_identifier_deletion_notification(self):
        nf_inst_id = "nf_inst_id"
        vnfm_id = "vnfm_id"
        vnf_instance_id = "vnf_instance_id"
        NfInstModel.objects.create(nfinstid=nf_inst_id,
                                   vnfm_inst_id=vnfm_id,
                                   status=VNF_STATUS.NULL,
                                   mnfinstid=vnf_instance_id,
                                   vnfd_model=self.vnfd_model
                                   )
        data = {
            "timeStamp": "20190809",
        }
        HandleVnfIdentifierDeletionNotification(vnfm_id, vnf_instance_id, data).do_biz()
        nf_inst = NfInstModel.objects.filter(mnfinstid=vnf_instance_id, vnfm_inst_id=vnfm_id)
        self.assertEqual(len(nf_inst), 0)

    def test_handle_vnf_identifier_deletion_notification_when_nf_not_exists(self):
        NfInstModel.objects.all().delete()
        vnfm_id = "nf_not_exists"
        vnf_instance_id = "nf_not_exists"
        data = {
            "timeStamp": "20190809",
        }
        try:
            HandleVnfIdentifierDeletionNotification(vnfm_id, vnf_instance_id, data).do_biz()
            self.assertEqual(1, 0)
        except Exception:
            self.assertEqual(1, 1)

    @mock.patch.object(restcall, "call_req")
    def test_handle_vnf_identifier_notification_when_save_ip_aai(self, mock_call_req):
        l_interface_info_aai = {
            "interface-name": "resourceProviderId",
            "is-port-mirrored": False,
            "resource-version": "1589506153510",
            "in-maint": False,
            "is-ip-unnumbered": False
        }
        l3_interface_ipv4_address_list = {
            "l3-interface-ipv4-address": "ipAddress",
            "resource-version": "1589527363970"
        }
        mock_vals = {
            "/network/generic-vnfs/generic-vnf/%s/l-interfaces/l-interface/%s"
            % ("test_vnf_notify", "resourceProviderId"):
                [0, json.JSONEncoder().encode(l_interface_info_aai), "200"],
            "/network/generic-vnfs/generic-vnf/%s/l-interfaces/l-interface/%s/l3-interface-ipv4-address-list/%s"
            % ("test_vnf_notify", "resourceProviderId", "ipAddress"):
                [0, json.JSONEncoder().encode(l3_interface_ipv4_address_list), "200"],
            "/network/l3-networks/l3-network/%s" % "vl_instance_id":
                [0, json.JSONEncoder().encode({}), "200"],

        }

        def side_effect(*args):
            return mock_vals[args[4]]

        mock_call_req.side_effect = side_effect

        data = {
            "id": "1111",
            "notificationType": "VnfLcmOperationOccurrenceNotification",
            "subscriptionId": "1111",
            "timeStamp": "1111",
            "notificationStatus": "START",
            "operationState": "STARTING",
            "vnfInstanceId": self.nf_inst_id,
            "operation": "INSTANTIATE",
            "isAutomaticInvocation": "1111",
            "vnfLcmOpOccId": "1111",
            "affectedVnfcs": [{"id": "vnfc_instance_id",
                               "vduId": "vdu_id",
                               "changeType": VNFC_CHANGE_TYPE.MODIFIED,
                               "computeResource": {
                                   "vimConnectionId": "vim_connection_id",
                                   "resourceId": "resource_id"
                               }}],
            "affectedVirtualLinks": [{"id": "vl_instance_id",
                                      "virtualLinkDescId": "virtual_link_desc_id",
                                      "changeType": VNFC_CHANGE_TYPE.MODIFIED,
                                      "networkResource": {
                                          "vimLevelResourceType": "network",
                                          "resourceId": "resource_id"
                                      }}],
            "changedExtConnectivity": [{"id": "virtual_link_instance_id",
                                        "extLinkPorts": [{"cpInstanceId": "cp_instance_id",
                                                          "id": "cpd_id",
                                                          "resourceHandle": {
                                                              "vimConnectionId": "vim_connection_id",
                                                              "resourceId": "resource_id",
                                                              "resourceProviderId": "resourceProviderId",
                                                              "tenant": "tenant",
                                                              "ipAddress": "ipAddress",
                                                              "macAddress": "macAddress",
                                                              "instId": "instId",
                                                              "networkId": "networkId",
                                                              "subnetId": "subnetId"
                                                          }
                                                          }],
                                        "changeType": VNFC_CHANGE_TYPE.MODIFIED
                                        }]
        }
        HandleVnfLcmOocNotification(self.vnfm_inst_id, self.m_nf_inst_id, data).do_biz()
        url = '/api/nslcm/v2/ns/%s/vnfs/%s/Notify' % (self.vnfm_inst_id, self.m_nf_inst_id)
        response = self.client.post(url, data)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code, response.content)
