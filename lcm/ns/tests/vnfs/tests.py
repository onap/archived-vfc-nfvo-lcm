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

import mock
from django.test import TestCase, Client
from rest_framework import status

from lcm.ns.vnfs import create_vnfs
from lcm.ns.vnfs.const import VNF_STATUS
from lcm.ns.vnfs.create_vnfs import CreateVnfs
from lcm.pub.database.models import NfInstModel, JobModel, NfPackageModel, NSInstModel
from lcm.pub.utils import restcall
from lcm.pub.utils.jobutil import JOB_MODEL_STATUS
from lcm.pub.utils.timeutil import now_time
from lcm.pub.utils.values import ignore_case_get
from lcm.ns.vnfs.terminate_nfs import TerminateVnfs
from lcm.ns.vnfs.scale_vnfs import NFManualScaleService
from lcm.ns.vnfs.heal_vnfs import NFHealService
from lcm.pub.utils.jobutil import JobUtil, JOB_TYPE
from lcm.pub.exceptions import NSLCMException

vnfm_info = {
    "vnfm-id": "example-vnfm-id-val-97336",
    "vim-id": "example-vim-id-val-35532",
    "certificate-url": "example-certificate-url-val-18046",
    "resource-version": "example-resource-version-val-42094",
    "esr-system-info-list": {
        "esr-system-info": [
            {
                "esr-system-info-id": "example-esr-system-info-id-val-7713",
                "system-name": "example-system-name-val-19801",
                "type": "ztevmanagerdriver",
                "vendor": "example-vendor-val-50079",
                "version": "example-version-val-93146",
                "service-url": "example-service-url-val-68090",
                "user-name": "example-user-name-val-14470",
                "password": "example-password-val-84190",
                "system-type": "example-system-type-val-42773",
                "protocal": "example-protocal-val-85736",
                "ssl-cacert": "example-ssl-cacert-val-33989",
                "ssl-insecure": True,
                "ip-address": "example-ip-address-val-99038",
                "port": "example-port-val-27323",
                "cloud-domain": "example-cloud-domain-val-55163",
                "default-tenant": "example-default-tenant-val-99383",
                "resource-version": "example-resource-version-val-15424"
            }
        ]
    }
}

class TestGetVnfViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.nf_inst_id = str(uuid.uuid4())
        NfInstModel(nfinstid=self.nf_inst_id, nf_name='vnf1', vnfm_inst_id='1', vnf_id='vnf_id1',
                    status=VNF_STATUS.ACTIVE, create_time=now_time(), lastuptime=now_time()).save()

    def tearDown(self):
        NfInstModel.objects.all().delete()

    def test_get_vnf(self):
        response = self.client.get("/api/nslcm/v1/ns/vnfs/%s" % self.nf_inst_id)
        self.failUnlessEqual(status.HTTP_200_OK, response.status_code)
        context = json.loads(response.content)
        self.failUnlessEqual(self.nf_inst_id, context['vnfInstId'])


class TestCreateVnfViews(TestCase):
    def setUp(self):
        self.ns_inst_id = str(uuid.uuid4())
        self.job_id = str(uuid.uuid4())
        self.data = {
            'nsInstanceId': self.ns_inst_id,
            'additionalParamForNs': {"inputs": json.dumps({})},
            'additionalParamForVnf': [{
                'vnfprofileid': 'VBras',
                'additionalparam': {
                    'inputs': json.dumps({'vnf_param1': '11', 'vnf_param2': '22'}),
                    'vnfminstanceid': "1"}}],
            'vnfIndex': '1'}
        self.client = Client()
        NfPackageModel(uuid=str(uuid.uuid4()), nfpackageid='package_id1', vnfdid='zte_vbras', vendor='zte',
                       vnfdversion='1.0.0', vnfversion='1.0.0', vnfdmodel=json.dumps(vnfd_model_dict)).save()
        NSInstModel(id=self.ns_inst_id, name='ns', nspackage_id='1', nsd_id='nsd_id', description='description',
                    status='instantiating', nsd_model=json.dumps(nsd_model_dict), create_time=now_time(),
                    lastuptime=now_time()).save()

    def tearDown(self):
        NfInstModel.objects.all().delete()
        JobModel.objects.all().delete()

    @mock.patch.object(CreateVnfs, 'run')
    def test_create_vnf(self, mock_run):
        response = self.client.post("/api/nslcm/v1/ns/vnfs", data=self.data)
        self.failUnlessEqual(status.HTTP_202_ACCEPTED, response.status_code)
        context = json.loads(response.content)
        self.assertTrue(NfInstModel.objects.filter(nfinstid=context['vnfInstId']).exists())

    @mock.patch.object(restcall, 'call_req')
    def test_create_vnf_thread(self, mock_call_req):
        mock_vals = {
            "/api/ztevmanagerdriver/v1/1/vnfs":
                [0, json.JSONEncoder().encode({"jobId": self.job_id, "vnfInstanceId": 3}), '200'],
            "/external-system/esr-vnfm-list/esr-vnfm/1":
                [0, json.JSONEncoder().encode(vnfm_info), '200'],
            "/api/resmgr/v1/vnf":
                [0, json.JSONEncoder().encode({}), '200'],
            "/api/resmgr/v1/vnfinfo":
                [0, json.JSONEncoder().encode({}), '200'],
            "/api/ztevmanagerdriver/v1/jobs/" + self.job_id + "&responseId=0":
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
                                                                           "errorcode": "0"}]}}), '200']}

        def side_effect(*args):
            return mock_vals[args[4]]
        mock_call_req.side_effect = side_effect
        data = {'ns_instance_id': ignore_case_get(self.data, 'nsInstanceId'),
                'additional_param_for_ns': ignore_case_get(self.data, 'additionalParamForNs'),
                'additional_param_for_vnf': ignore_case_get(self.data, 'additionalParamForVnf'),
                'vnf_index': ignore_case_get(self.data, 'vnfIndex')}
        nf_inst_id, job_id = create_vnfs.prepare_create_params()
        CreateVnfs(data, nf_inst_id, job_id).run()
        self.assertTrue(NfInstModel.objects.get(nfinstid=nf_inst_id).status, VNF_STATUS.ACTIVE)


class TestTerminateVnfViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.ns_inst_id = str(uuid.uuid4())
        self.nf_inst_id = '1'
        self.vnffg_id = str(uuid.uuid4())
        self.vim_id = str(uuid.uuid4())
        self.job_id = str(uuid.uuid4())
        self.nf_uuid = '111'
        self.tenant = "tenantname"
        NSInstModel.objects.all().delete()
        NfInstModel.objects.all().delete()
        NSInstModel(id=self.ns_inst_id, name="ns_name").save()
        NfInstModel.objects.create(nfinstid=self.nf_inst_id, nf_name='name_1', vnf_id='1',
                                   vnfm_inst_id='1', ns_inst_id='111,2-2-2',
                                   max_cpu='14', max_ram='12296', max_hd='101', max_shd="20", max_net=10,
                                   status='active', mnfinstid=self.nf_uuid, package_id='pkg1',
                                   vnfd_model='{"metadata": {"vnfdId": "1","vnfdName": "PGW001",'
                                              '"vnfProvider": "zte","vnfdVersion": "V00001","vnfVersion": "V5.10.20",'
                                              '"productType": "CN","vnfType": "PGW",'
                                              '"description": "PGW VNFD description",'
                                              '"isShared":true,"vnfExtendType":"driver"}}')

    def tearDown(self):
        NSInstModel.objects.all().delete()
        NfInstModel.objects.all().delete()

    @mock.patch.object(TerminateVnfs, 'run')
    def test_terminate_vnf_url(self, mock_run):
        req_data = {
            "terminationType": "forceful",
            "gracefulTerminationTimeout": "600"}

        response = self.client.post("/api/nslcm/v1/ns/vnfs/%s" % self.nf_inst_id, data=req_data)
        self.failUnlessEqual(status.HTTP_201_CREATED, response.status_code)


    @mock.patch.object(restcall, 'call_req')
    def test_terminate_vnf(self, mock_call_req):
        job_id = JobUtil.create_job("VNF", JOB_TYPE.TERMINATE_VNF, self.nf_inst_id)

        nfinst = NfInstModel.objects.filter(nfinstid=self.nf_inst_id)
        if nfinst:
            self.failUnlessEqual(1, 1)
        else:
            self.failUnlessEqual(1, 0)

        vnf_info = {
            "vnf-id": "vnf-id-test111",
            "vnf-name": "vnf-name-test111",
            "vnf-type": "vnf-type-test111",
            "in-maint": True,
            "is-closed-loop-disabled": False,
            "resource-version": "1505465356262"
        }
        job_info = {
            "jobId": job_id,
            "responsedescriptor": {
                "progress": "100",
                "status": JOB_MODEL_STATUS.FINISHED,
                "responseid": "3",
                "statusdescription": "creating",
                "errorcode": "0",
                "responsehistorylist": [
                    {
                        "progress": "0",
                        "status": JOB_MODEL_STATUS.PROCESSING,
                        "responseid": "2",
                        "statusdescription": "creating",
                        "errorcode": "0"
                    }
                ]
            }
        }

        mock_vals = {
            "/external-system/esr-vnfm-list/esr-vnfm/1?depth=all":
                [0, json.JSONEncoder().encode(vnfm_info), '200'],
            "/api/ztevmanagerdriver/v1/1/vnfs/111/terminate":
                [0, json.JSONEncoder().encode({"jobId": job_id}), '200'],
            "/api/resmgr/v1/vnf/1":
                [0, json.JSONEncoder().encode({"jobId": job_id}), '200'],
            "/api/ztevmanagerdriver/v1/1/jobs/" + job_id + "?responseId=0":
                [0, json.JSONEncoder().encode(job_info), '200'],
            "/network/generic-vnfs/generic-vnf/111?depth=all":
            [0, json.JSONEncoder().encode(vnf_info), '200'],
            "/network/generic-vnfs/generic-vnf/111?resource-version=1505465356262":
            [0, json.JSONEncoder().encode({}), '200']
        }

        def side_effect(*args):
            return mock_vals[args[4]]
        mock_call_req.side_effect = side_effect

        req_data = {
            "terminationType": "forceful",
            "gracefulTerminationTimeout": "600"}

        TerminateVnfs(req_data, self.nf_inst_id, job_id).run()
        nfinst = NfInstModel.objects.filter(nfinstid=self.nf_inst_id)
        if nfinst:
            self.failUnlessEqual(1, 0)
        else:
            self.failUnlessEqual(1, 1)

class TestScaleVnfViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.ns_inst_id = str(uuid.uuid4())
        self.nf_inst_id = str(uuid.uuid4())
        self.vnffg_id = str(uuid.uuid4())
        self.vim_id = str(uuid.uuid4())
        self.job_id = str(uuid.uuid4())
        self.nf_uuid = '111'
        self.tenant = "tenantname"
        NSInstModel(id=self.ns_inst_id, name="ns_name").save()
        NfInstModel.objects.create(nfinstid=self.nf_inst_id, nf_name='name_1', vnf_id='1',
                                   vnfm_inst_id='1', ns_inst_id='111,2-2-2',
                                   max_cpu='14', max_ram='12296', max_hd='101', max_shd="20", max_net=10,
                                   status='active', mnfinstid=self.nf_uuid, package_id='pkg1',
                                   vnfd_model='{"metadata": {"vnfdId": "1","vnfdName": "PGW001",'
                                              '"vnfProvider": "zte","vnfdVersion": "V00001","vnfVersion": "V5.10.20",'
                                              '"productType": "CN","vnfType": "PGW",'
                                              '"description": "PGW VNFD description",'
                                              '"isShared":true,"vnfExtendType":"driver"}}')

    def tearDown(self):
        NSInstModel.objects.all().delete()
        NfInstModel.objects.all().delete()

    @mock.patch.object(restcall, "call_req")
    def test_scale_vnf(self, mock_call_req):
        job_id = JobUtil.create_job("VNF", JOB_TYPE.TERMINATE_VNF, self.nf_inst_id)

        vnfd_info = {
            "vnf_flavours":[
                {
                    "flavour_id":"flavour1",
                    "description":"",
                    "vdu_profiles":[
                        {
                            "vdu_id":"vdu1Id",
                            "instances_minimum_number": 1,
                            "instances_maximum_number": 4,
                            "local_affinity_antiaffinity_rule":[
                                {
                                    "affinity_antiaffinity":"affinity",
                                    "scope":"node",
                                }
                            ]
                        }
                    ],
                    "scaling_aspects":[
                        {
                            "id": "demo_aspect",
                            "name": "demo_aspect",
                            "description": "demo_aspect",
                            "associated_group": "elementGroup1",
                            "max_scale_level": 5
                        }
                    ]
                }
            ],
            "element_groups": [
                  {
                      "group_id": "elementGroup1",
                      "description": "",
                      "properties":{
                          "name": "elementGroup1",
                      },
                      "members": ["gsu_vm","pfu_vm"],
                  }
            ]
        }

        req_data = {
            "scaleVnfData": [
                {
                    "type":"SCALE_OUT",
                    "aspectId":"demo_aspect1",
                    "numberOfSteps":1,
                    "additionalParam":vnfd_info
                },
                {
                    "type":"SCALE_OUT",
                    "aspectId":"demo_aspect2",
                    "numberOfSteps":1,
                    "additionalParam":vnfd_info
                }
            ]
        }


        mock_vals = {
            "/api/ztevmanagerdriver/v1/1/vnfs/111/terminate":
                [0, json.JSONEncoder().encode({"jobId": job_id}), '200'],
            "/api/ztevmanagerdriver/v1/1/vnfs/111/terminate":
                [0, json.JSONEncoder().encode({"jobId": job_id}), '200']
        }
        def side_effect(*args):
            return mock_vals[args[4]]
        mock_call_req.side_effect = side_effect

        NFManualScaleService(self.nf_inst_id, req_data).run()
        nsIns = NfInstModel.objects.filter(nfinstid=self.nf_inst_id)
        if nsIns:
            self.failUnlessEqual(1, 1)
        else:
            self.failUnlessEqual(1, 0)


class TestHealVnfViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.ns_inst_id = str(uuid.uuid4())
        self.nf_inst_id = str(uuid.uuid4())
        self.nf_uuid = '111'

        self.job_id = JobUtil.create_job("VNF", JOB_TYPE.HEAL_VNF, self.nf_inst_id)

        NSInstModel(id=self.ns_inst_id, name="ns_name").save()
        NfInstModel.objects.create(nfinstid=self.nf_inst_id, nf_name='name_1', vnf_id='1',
                                   vnfm_inst_id='1', ns_inst_id='111,2-2-2',
                                   max_cpu='14', max_ram='12296', max_hd='101', max_shd="20", max_net=10,
                                   status='active', mnfinstid=self.nf_uuid, package_id='pkg1',
                                   vnfd_model='{"metadata": {"vnfdId": "1","vnfdName": "PGW001",'
                                              '"vnfProvider": "zte","vnfdVersion": "V00001","vnfVersion": "V5.10.20",'
                                              '"productType": "CN","vnfType": "PGW",'
                                              '"description": "PGW VNFD description",'
                                              '"isShared":true,"vnfExtendType":"driver"}}')

    def tearDown(self):
        NSInstModel.objects.all().delete()
        NfInstModel.objects.all().delete()

    @mock.patch.object(restcall, "call_req")
    def test_heal_vnf(self, mock_call_req):


        mock_vals = {
            "/api/ztevmanagerdriver/v1/1/vnfs/111/heal":
                [0, json.JSONEncoder().encode({"jobId": self.job_id}), '200'],
            "/external-system/esr-vnfm-list/esr-vnfm/1":
                [0, json.JSONEncoder().encode(vnfm_info), '200'],
            "/api/resmgr/v1/vnf/1":
                [0, json.JSONEncoder().encode({"jobId": self.job_id}), '200'],
            "/api/ztevmanagerdriver/v1/1/jobs/" + self.job_id + "?responseId=0":
                [0, json.JSONEncoder().encode({"jobId": self.job_id,
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
                                                                           "errorcode": "0"}]}}), '200']}

        def side_effect(*args):
            return mock_vals[args[4]]

        mock_call_req.side_effect = side_effect

        req_data = {
            "action": "vmReset",
            "affectedvm": {
                "vmid": "1",
                "vduid": "1",
                "vmname": "name",
            }
        }

        NFHealService(self.nf_inst_id, req_data).run()

        self.assertEqual(NfInstModel.objects.get(nfinstid=self.nf_inst_id).status, VNF_STATUS.ACTIVE)

    @mock.patch.object(NFHealService, "run")
    def test_heal_vnf_non_existing_vnf(self, mock_biz):
        mock_biz.side_effect = NSLCMException("VNF Not Found")

        nf_inst_id = "1"

        req_data = {
            "action": "vmReset",
            "affectedvm": {
                "vmid": "1",
                "vduid": "1",
                "vmname": "name",
            }
        }

        self.assertRaises(NSLCMException, NFHealService(nf_inst_id, req_data).run)
        self.assertEqual(len(NfInstModel.objects.filter(nfinstid=nf_inst_id)), 0)

class TestGetVnfmInfoViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.vnfm_id = str(uuid.uuid4())

    def tearDown(self):
        pass

    @mock.patch.object(restcall, "call_req")
    def test_get_vnfm_info(self, mock_call_req):
        vnfm_info_aai = \
            {
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
        r1 = [0, json.JSONEncoder().encode(vnfm_info_aai), '200']
        mock_call_req.side_effect = [r1]
        esr_system_info = ignore_case_get(ignore_case_get(vnfm_info_aai, "esr-system-info-list"), "esr-system-info")
        expect_data = \
            {
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
                "createTime": "2016-07-06 15:33:18"
            }

        response = self.client.get("/api/nslcm/v1/vnfms/%s" % self.vnfm_id)
        self.failUnlessEqual(status.HTTP_200_OK, response.status_code)
        context = json.loads(response.content)
        self.assertEqual(expect_data, context)

class TestGetVimInfoViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.vim_id = "zte_test"

    def tearDown(self):
        pass

    @mock.patch.object(restcall, "call_req")
    def test_get_vim_info(self, mock_call_req):
        r1 = [0, json.JSONEncoder().encode(vim_info_aai), '200']
        mock_call_req.side_effect = [r1]
        esr_system_info = ignore_case_get(ignore_case_get(vim_info_aai, "esr-system-info-list"), "esr-system-info")
        expect_data = \
            {
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
                "createTime": "2016-07-18 12:22:53"
            }

        response = self.client.get("/api/nslcm/v1/vims/%s" % self.vim_id)
        self.failUnlessEqual(status.HTTP_200_OK, response.status_code)
        context = json.loads(response.content)
        self.assertEqual(expect_data["url"], context["url"])

vnfd_model_dict = {
    'local_storages': [],
    'vdus': [
        {
            'volumn_storages': [],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': u'2'},
            'local_storages': [],
            'vdu_id': u'vdu_omm.001',
            'image_file': u'opencos_sss_omm_img_release_20150723-1-disk1',
            'dependencies': [],
            'vls': [],
            'cps': [],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''},
                'inject_data_list': [],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''},
                'local_affinity_antiaffinity_rule': {},
                'template_id': u'omm.001',
                'manual_scale_select_vim': False},
            'description': u'singleommvm'},
        {
            'volumn_storages': [],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': u'4'},
            'local_storages': [],
            'vdu_id': u'vdu_1',
            'image_file': u'sss',
            'dependencies': [],
            'vls': [],
            'cps': [],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''},
                'inject_data_list': [],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''},
                'local_affinity_antiaffinity_rule': {},
                'template_id': u'1',
                'manual_scale_select_vim': False},
            'description': u'ompvm'},
        {
            'volumn_storages': [],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': u'14'},
            'local_storages': [],
            'vdu_id': u'vdu_2',
            'image_file': u'sss',
            'dependencies': [],
            'vls': [],
            'cps': [],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''},
                'inject_data_list': [],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''},
                'local_affinity_antiaffinity_rule': {},
                'template_id': u'2',
                'manual_scale_select_vim': False},
            'description': u'ompvm'},
        {
            'volumn_storages': [],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': u'14'},
            'local_storages': [],
            'vdu_id': u'vdu_3',
            'image_file': u'sss',
            'dependencies': [],
            'vls': [],
            'cps': [],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''},
                'inject_data_list': [],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''},
                'local_affinity_antiaffinity_rule': {},
                'template_id': u'3',
                'manual_scale_select_vim': False},
            'description': u'ompvm'},
        {
            'volumn_storages': [],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': u'4'},
            'local_storages': [],
            'vdu_id': u'vdu_10',
            'image_file': u'sss',
            'dependencies': [],
            'vls': [],
            'cps': [],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''},
                'inject_data_list': [],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''},
                'local_affinity_antiaffinity_rule': {},
                'template_id': u'10',
                'manual_scale_select_vim': False},
            'description': u'ppvm'},
        {
            'volumn_storages': [],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': u'14'},
            'local_storages': [],
            'vdu_id': u'vdu_11',
            'image_file': u'sss',
            'dependencies': [],
            'vls': [],
            'cps': [],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''},
                'inject_data_list': [],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''},
                'local_affinity_antiaffinity_rule': {},
                'template_id': u'11',
                'manual_scale_select_vim': False},
            'description': u'ppvm'},
        {
            'volumn_storages': [],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': u'14'},
            'local_storages': [],
            'vdu_id': u'vdu_12',
            'image_file': u'sss',
            'dependencies': [],
            'vls': [],
            'cps': [],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''},
                'inject_data_list': [],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''},
                'local_affinity_antiaffinity_rule': {},
                'template_id': u'12',
                'manual_scale_select_vim': False},
            'description': u'ppvm'}],
    'volumn_storages': [],
    'policies': {
        'scaling': {
            'targets': {},
            'policy_id': u'policy_scale_sss-vnf-template',
            'properties': {
                'policy_file': '*-vnfd.zip/*-vnf-policy.xml'},
            'description': ''}},
    'image_files': [
        {
            'description': '',
            'properties': {
                'name': u'opencos_sss_omm_img_release_20150723-1-disk1.vmdk',
                'checksum': '',
                'disk_format': u'VMDK',
                'file_url': u'./zte-cn-sss-main-image/OMM/opencos_sss_omm_img_release_20150723-1-disk1.vmdk',
                'container_type': 'vm',
                'version': '',
                'hypervisor_type': 'kvm'},
            'image_file_id': u'opencos_sss_omm_img_release_20150723-1-disk1'},
        {
            'description': '',
            'properties': {
                'name': u'sss.vmdk',
                'checksum': '',
                'disk_format': u'VMDK',
                'file_url': u'./zte-cn-sss-main-image/NE/sss.vmdk',
                'container_type': 'vm',
                'version': '',
                'hypervisor_type': 'kvm'},
            'image_file_id': u'sss'}],
    'vls': [],
    'cps': [],
    'metadata': {
        'vendor': u'zte',
        'is_shared': False,
        'description': '',
        'domain_type': u'CN',
        'version': u'v4.14.10',
        'vmnumber_overquota_alarm': False,
        'cross_dc': False,
        'vnf_type': u'SSS',
        'vnfd_version': u'V00000001',
        'id': u'sss-vnf-template',
        'name': u'sss-vnf-template'}}

nsd_model_dict = {
    "vnffgs": [],
    "inputs": {
        "externalDataNetworkName": {
            "default": "",
            "type": "string",
            "description": ""}},
    "pnfs": [],
    "fps": [],
    "server_groups": [],
    "ns_flavours": [],
    "vnfs": [
        {
            "dependency": [],
            "properties": {
                "plugin_info": "vbrasplugin_1.0",
                "vendor": "zte",
                "is_shared": "False",
                "request_reclassification": "False",
                "vnfd_version": "1.0.0",
                "version": "1.0",
                "nsh_aware": "True",
                "cross_dc": "False",
                "externalDataNetworkName": {
                    "get_input": "externalDataNetworkName"},
                "id": "zte_vbras",
                "name": "vbras"},
            "vnf_id": "VBras",
            "networks": [],
            "description": ""}],
    "ns_exposed": {
        "external_cps": [],
        "forward_cps": []},
    "vls": [
        {
            "vl_id": "ext_mnet_network",
            "description": "",
            "properties": {
                "network_type": "vlan",
                "name": "externalMNetworkName",
                "dhcp_enabled": False,
                "location_info": {
                    "host": True,
                    "vimid": 2,
                    "region": True,
                    "tenant": "admin",
                    "dc": ""},
                "end_ip": "190.168.100.100",
                "gateway_ip": "190.168.100.1",
                "start_ip": "190.168.100.2",
                "cidr": "190.168.100.0/24",
                "mtu": 1500,
                "network_name": "sub_mnet",
                "ip_version": 4}}],
    "cps": [],
    "policies": [],
    "metadata": {
        "invariant_id": "vbras_ns",
        "description": "vbras_ns",
        "version": 1,
        "vendor": "zte",
        "id": "vbras_ns",
        "name": "vbras_ns"}}


vim_info_aai = {
    "cloud-owner": "example-cloud-owner-val-1140",
    "cloud-region-id": "example-cloud-region-id-val-73665",
    "cloud-type": "example-cloud-type-val-14605",
    "owner-defined-type": "example-owner-defined-type-val-84308",
    "cloud-region-version": "example-cloud-region-version-val-67581",
    "identity-url": "example-identity-url-val-98779",
    "cloud-zone": "example-cloud-zone-val-67799",
    "complex-name": "example-complex-name-val-62313",
    "sriov-automation": True,
    "cloud-extra-info": "example-cloud-extra-info-val-72366",
    "cloud-epa-caps": "example-cloud-epa-caps-val-6090",
    "volume-groups": {
        "volume-group": [
            {
                "volume-group-id": "example-volume-group-id-val-22419",
                "volume-group-name": "example-volume-group-name-val-41986",
                "heat-stack-id": "example-heat-stack-id-val-53241",
                "vnf-type": "example-vnf-type-val-19402",
                "orchestration-status": "example-orchestration-status-val-61478",
                "model-customization-id": "example-model-customization-id-val-82523",
                "vf-module-model-customization-id": "example-vf-module-model-customization-id-val-49214"
            }
        ]
    },
    "tenants": {
        "tenant": [
            {
                "tenant-id": "example-tenant-id-val-28032",
                "tenant-name": "example-tenant-name-val-65072",
                "tenant-context": "example-tenant-context-val-81984",
                "vservers": {
                    "vserver": [
                        {
                            "vserver-id": "example-vserver-id-val-25067",
                            "vserver-name": "example-vserver-name-val-16505",
                            "vserver-name2": "example-vserver-name2-val-84664",
                            "prov-status": "example-prov-status-val-1789",
                            "vserver-selflink": "example-vserver-selflink-val-6858",
                            "in-maint": True,
                            "is-closed-loop-disabled": True,
                            "volumes": {
                                "volume": [
                                    {
                                        "volume-id": "example-volume-id-val-69135",
                                        "volume-selflink": "example-volume-selflink-val-96457"
                                    }
                                ]
                            },
                            "l-interfaces": {
                                "l-interface": [
                                    {
                                        "interface-name": "example-interface-name-val-57532",
                                        "interface-role": "example-interface-role-val-10218",
                                        "v6-wan-link-ip": "example-v6-wan-link-ip-val-64941",
                                        "selflink": "example-selflink-val-80427",
                                        "interface-id": "example-interface-id-val-53136",
                                        "macaddr": "example-macaddr-val-35417",
                                        "network-name": "example-network-name-val-77107",
                                        "management-option": "example-management-option-val-19752",
                                        "interface-description": "example-interface-description-val-34461",
                                        "is-port-mirrored": True,
                                        "in-maint": True,
                                        "prov-status": "example-prov-status-val-39824",
                                        "is-ip-unnumbered": True,
                                        "allowed-address-pairs": "example-allowed-address-pairs-val-76052",
                                        "vlans": {
                                            "vlan": [
                                                {
                                                    "vlan-interface": "example-vlan-interface-val-81272",
                                                    "vlan-id-inner": 70939085,
                                                    "vlan-id-outer": 80445097,
                                                    "speed-value": "example-speed-value-val-47939",
                                                    "speed-units": "example-speed-units-val-90989",
                                                    "vlan-description": "example-vlan-description-val-96792",
                                                    "backdoor-connection": "example-backdoor-connection-val-74707",
                                                    "vpn-key": "example-vpn-key-val-73677",
                                                    "orchestration-status": "example-orchestration-status-val-93544",
                                                    "in-maint": True,
                                                    "prov-status": "example-prov-status-val-18854",
                                                    "is-ip-unnumbered": True,
                                                    "l3-interface-ipv4-address-list": [
                                                        {
                                                            "l3-interface-ipv4-address": "example-l3-interface-ipv4-address-val-46993",
                                                            "l3-interface-ipv4-prefix-length": 28216731,
                                                            "vlan-id-inner": 8589169,
                                                            "vlan-id-outer": 22167953,
                                                            "is-floating": True,
                                                            "neutron-network-id": "example-neutron-network-id-val-45028",
                                                            "neutron-subnet-id": "example-neutron-subnet-id-val-99844"
                                                        }
                                                    ],
                                                    "l3-interface-ipv6-address-list": [
                                                        {
                                                            "l3-interface-ipv6-address": "example-l3-interface-ipv6-address-val-8414",
                                                            "l3-interface-ipv6-prefix-length": 6761190,
                                                            "vlan-id-inner": 88349266,
                                                            "vlan-id-outer": 87459050,
                                                            "is-floating": True,
                                                            "neutron-network-id": "example-neutron-network-id-val-23050",
                                                            "neutron-subnet-id": "example-neutron-subnet-id-val-49448"
                                                        }
                                                    ]
                                                }
                                            ]
                                        },
                                        "sriov-vfs": {
                                            "sriov-vf": [
                                                {
                                                    "pci-id": "example-pci-id-val-9702",
                                                    "vf-vlan-filter": "example-vf-vlan-filter-val-94893",
                                                    "vf-mac-filter": "example-vf-mac-filter-val-40257",
                                                    "vf-vlan-strip": True,
                                                    "vf-vlan-anti-spoof-check": True,
                                                    "vf-mac-anti-spoof-check": True,
                                                    "vf-mirrors": "example-vf-mirrors-val-86932",
                                                    "vf-broadcast-allow": True,
                                                    "vf-unknown-multicast-allow": True,
                                                    "vf-unknown-unicast-allow": True,
                                                    "vf-insert-stag": True,
                                                    "vf-link-status": "example-vf-link-status-val-94678",
                                                    "neutron-network-id": "example-neutron-network-id-val-18823"
                                                }
                                            ]
                                        },
                                        "l-interfaces": {
                                            "l-interface": [
                                                {
                                                    "interface-name": "example-interface-name-val-42153",
                                                    "interface-role": "example-interface-role-val-38539",
                                                    "v6-wan-link-ip": "example-v6-wan-link-ip-val-12452",
                                                    "selflink": "example-selflink-val-38250",
                                                    "interface-id": "example-interface-id-val-68366",
                                                    "macaddr": "example-macaddr-val-76392",
                                                    "network-name": "example-network-name-val-58136",
                                                    "management-option": "example-management-option-val-88555",
                                                    "interface-description": "example-interface-description-val-66875",
                                                    "is-port-mirrored": True,
                                                    "in-maint": True,
                                                    "prov-status": "example-prov-status-val-9493",
                                                    "is-ip-unnumbered": True,
                                                    "allowed-address-pairs": "example-allowed-address-pairs-val-80407"
                                                }
                                            ]
                                        },
                                        "l3-interface-ipv4-address-list": [
                                            {
                                                "l3-interface-ipv4-address": "example-l3-interface-ipv4-address-val-57596",
                                                "l3-interface-ipv4-prefix-length": 90030728,
                                                "vlan-id-inner": 43361064,
                                                "vlan-id-outer": 18962103,
                                                "is-floating": True,
                                                "neutron-network-id": "example-neutron-network-id-val-55667",
                                                "neutron-subnet-id": "example-neutron-subnet-id-val-46585"
                                            }
                                        ],
                                        "l3-interface-ipv6-address-list": [
                                            {
                                                "l3-interface-ipv6-address": "example-l3-interface-ipv6-address-val-74591",
                                                "l3-interface-ipv6-prefix-length": 38739444,
                                                "vlan-id-inner": 65048885,
                                                "vlan-id-outer": 94802338,
                                                "is-floating": True,
                                                "neutron-network-id": "example-neutron-network-id-val-64105",
                                                "neutron-subnet-id": "example-neutron-subnet-id-val-65190"
                                            }
                                        ]
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        ]
    },
    "flavors": {
        "flavor": [
            {
                "flavor-id": "example-flavor-id-val-92555",
                "flavor-name": "example-flavor-name-val-35938",
                "flavor-vcpus": 88056,
                "flavor-ram": 18804,
                "flavor-disk": 2575,
                "flavor-ephemeral": 28190,
                "flavor-swap": "example-flavor-swap-val-76888",
                "flavor-is-public": True,
                "flavor-selflink": "example-flavor-selflink-val-33816",
                "flavor-disabled": True
            }
        ]
    },
    "group-assignments": {
        "group-assignment": [
            {
                "group-id": "example-group-id-val-6872",
                "group-type": "example-group-type-val-64490",
                "group-name": "example-group-name-val-67702",
                "group-description": "example-group-description-val-99149"
            }
        ]
    },
    "snapshots": {
        "snapshot": [
            {
                "snapshot-id": "example-snapshot-id-val-32009",
                "snapshot-name": "example-snapshot-name-val-47165",
                "snapshot-architecture": "example-snapshot-architecture-val-84769",
                "snapshot-os-distro": "example-snapshot-os-distro-val-70763",
                "snapshot-os-version": "example-snapshot-os-version-val-4220",
                "application": "example-application-val-12453",
                "application-vendor": "example-application-vendor-val-95617",
                "application-version": "example-application-version-val-77699",
                "snapshot-selflink": "example-snapshot-selflink-val-90202",
                "prev-snapshot-id": "example-prev-snapshot-id-val-10951"
            }
        ]
    },
    "images": {
        "image": [
            {
                "image-id": "example-image-id-val-17245",
                "image-name": "example-image-name-val-93251",
                "image-architecture": "example-image-architecture-val-21934",
                "image-os-distro": "example-image-os-distro-val-51699",
                "image-os-version": "example-image-os-version-val-92745",
                "application": "example-application-val-47760",
                "application-vendor": "example-application-vendor-val-67650",
                "application-version": "example-application-version-val-4499",
                "image-selflink": "example-image-selflink-val-70348",
                "metadata": {
                    "metadatum": [
                        {
                            "metaname": "example-metaname-val-57218",
                            "metaval": "example-metaval-val-39269"
                        }
                    ]
                }
            }
        ]
    },
    "dvs-switches": {
        "dvs-switch": [
            {
                "switch-name": "example-switch-name-val-31508",
                "vcenter-url": "example-vcenter-url-val-57139"
            }
        ]
    },
    "oam-networks": {
        "oam-network": [
            {
                "network-uuid": "example-network-uuid-val-93435",
                "network-name": "example-network-name-val-66722",
                "cvlan-tag": 54019733,
                "ipv4-oam-gateway-address": "example-ipv4-oam-gateway-address-val-3261",
                "ipv4-oam-gateway-address-prefix-length": 53725
            }
        ]
    },
    "availability-zones": {
        "availability-zone": [
            {
                "availability-zone-name": "example-availability-zone-name-val-71842",
                "hypervisor-type": "example-hypervisor-type-val-21339",
                "operational-status": "example-operational-status-val-18872"
            }
        ]
    },
    "esr-system-info-list": {
        "esr-system-info": [
            {
                "esr-system-info-id": "example-esr-system-info-id-val-42986",
                "system-name": "example-system-name-val-1117",
                "type": "example-type-val-28567",
                "vendor": "example-vendor-val-99666",
                "version": "example-version-val-9880",
                "service-url": "example-service-url-val-95838",
                "user-name": "example-user-name-val-88013",
                "password": "example-password-val-51483",
                "system-type": "example-system-type-val-24554",
                "protocal": "example-protocal-val-92250",
                "ssl-cacert": "example-ssl-cacert-val-80275",
                "ssl-insecure": True,
                "ip-address": "example-ip-address-val-49558",
                "port": "example-port-val-55636",
                "cloud-domain": "example-cloud-domain-val-77975",
                "default-tenant": "example-default-tenant-val-85499"
            }
        ]
    }
}