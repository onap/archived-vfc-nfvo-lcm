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
from lcm.ns.vnfs.const import VNF_STATUS, INST_TYPE
from lcm.ns.vnfs.create_vnfs import CreateVnfs
from lcm.ns.vnfs.heal_vnfs import NFHealService
from lcm.ns.vnfs.scale_vnfs import NFManualScaleService
from lcm.ns.vnfs.terminate_nfs import TerminateVnfs
from lcm.pub.database.models import NfInstModel, JobModel, NSInstModel, VmInstModel
from lcm.pub.exceptions import NSLCMException
from lcm.pub.utils import restcall
from lcm.pub.utils.jobutil import JOB_MODEL_STATUS
from lcm.pub.utils.jobutil import JobUtil, JOB_TYPE
from lcm.pub.utils.timeutil import now_time
from lcm.pub.utils.values import ignore_case_get


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
            "nsInstanceId": self.ns_inst_id,
            "additionalParamForNs": {
                "inputs": json.dumps({

                })
            },
            "additionalParamForVnf": [
                {
                    "vnfprofileid": "VBras",
                    "additionalparam": {
                        "inputs": json.dumps({
                            "vnf_param1": "11",
                            "vnf_param2": "22"
                        }),
                        "vnfminstanceid": "1",
                        "vimId": "zte_test"
                    }
                }
            ],
            "vnfIndex": "1"
        }
        self.client = Client()
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
        nf_inst_id, job_id = create_vnfs.prepare_create_params()
        mock_vals = {
            "/api/ztevmanagerdriver/v1/1/vnfs":
                [0, json.JSONEncoder().encode({"jobId": self.job_id, "vnfInstanceId": 3}), '200'],
            "/api/catalog/v1/vnfpackages/zte_vbras":
                [0, json.JSONEncoder().encode(nf_package_info), '200'],
            "/external-system/esr-vnfm-list/esr-vnfm/1?depth=all":
                [0, json.JSONEncoder().encode(vnfm_info), '200'],
            "/api/resmgr/v1/vnf":
                [0, json.JSONEncoder().encode({}), '200'],
            "/api/resmgr/v1/vnfinfo":
                [0, json.JSONEncoder().encode({}), '200'],
            "/network/generic-vnfs/generic-vnf/%s" % nf_inst_id:
                [0, json.JSONEncoder().encode({}), '201'],
            "/cloud-infrastructure/cloud-regions/cloud-region/zte/test?depth=all":
                [0, json.JSONEncoder().encode(vim_info), '201'],
            "/cloud-infrastructure/cloud-regions/cloud-region/zte/test/tenants/tenant/admin/vservers/vserver/1":
                [0, json.JSONEncoder().encode({}), '201'],
            "/api/ztevmanagerdriver/v1/1/jobs/" + self.job_id + "?responseId=0":
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
        data = {
            'ns_instance_id': ignore_case_get(self.data, 'nsInstanceId'),
            'additional_param_for_ns': ignore_case_get(self.data, 'additionalParamForNs'),
            'additional_param_for_vnf': ignore_case_get(self.data, 'additionalParamForVnf'),
            'vnf_index': ignore_case_get(self.data, 'vnfIndex')
        }
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
        self.vnfd_model = {
            "metadata": {
                "vnfdId": "1",
                "vnfdName": "PGW001",
                "vnfProvider": "zte",
                "vnfdVersion": "V00001",
                "vnfVersion": "V5.10.20",
                "productType": "CN",
                "vnfType": "PGW",
                "description": "PGW VNFD description",
                "isShared": True,
                "vnfExtendType": "driver"
            }
        }
        NSInstModel.objects.all().delete()
        NfInstModel.objects.all().delete()
        VmInstModel.objects.all().delete()
        NSInstModel(id=self.ns_inst_id, name="ns_name").save()
        NfInstModel.objects.create(nfinstid=self.nf_inst_id,
                                   nf_name='name_1',
                                   vnf_id='1',
                                   vnfm_inst_id='1',
                                   ns_inst_id='111,2-2-2',
                                   max_cpu='14',
                                   max_ram='12296',
                                   max_hd='101',
                                   max_shd="20",
                                   max_net=10,
                                   status='active',
                                   mnfinstid=self.nf_uuid,
                                   package_id='pkg1',
                                   vnfd_model=self.vnfd_model)
        VmInstModel.objects.create(vmid="1",
                                   vimid="zte_test",
                                   resouceid="1",
                                   insttype=INST_TYPE.VNF,
                                   instid=self.nf_inst_id,
                                   vmname="test",
                                   hostid='1')

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
            "/cloud-infrastructure/cloud-regions/cloud-region/zte/test?depth=all":
                [0, json.JSONEncoder().encode(vim_info), '201'],
            "/cloud-infrastructure/cloud-regions/cloud-region/zte/test/tenants/tenant/admin/vservers/vserver/1?depth=all":
                [0, json.JSONEncoder().encode(vserver_info), '201'],
            "/cloud-infrastructure/cloud-regions/cloud-region/zte/test/tenants/tenant/admin/vservers/vserver/1?resource-version=1505465356263":
                [0, json.JSONEncoder().encode({}), '200'],
            "/api/ztevmanagerdriver/v1/1/jobs/" + job_id + "?responseId=0":
                [0, json.JSONEncoder().encode(job_info), '200'],
            "/network/generic-vnfs/generic-vnf/1?depth=all":
            [0, json.JSONEncoder().encode(vnf_info), '200'],
            "/network/generic-vnfs/generic-vnf/1?resource-version=1505465356262":
            [0, json.JSONEncoder().encode({}), '200']
        }

        def side_effect(*args):
            return mock_vals[args[4]]
        mock_call_req.side_effect = side_effect

        req_data = {
            "terminationType": "forceful",
            "gracefulTerminationTimeout": "600"
        }

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
            "vnf_flavours": [{
                "flavour_id": "flavour1",
                "description": "",
                "vdu_profiles": [
                    {
                        "vdu_id": "vdu1Id",
                        "instances_minimum_number": 1,
                        "instances_maximum_number": 4,
                        "local_affinity_antiaffinity_rule": [
                            {
                                "affinity_antiaffinity": "affinity",
                                "scope": "node",
                            }
                        ]
                    }
                ],
                "scaling_aspects": [
                    {
                        "id": "demo_aspect",
                        "name": "demo_aspect",
                        "description": "demo_aspect",
                        "associated_group": "elementGroup1",
                        "max_scale_level": 5
                    }
                ]
            }],
            "element_groups": [{
                "group_id": "elementGroup1",
                "description": "",
                "properties": {
                    "name": "elementGroup1",
                },
                "members": ["gsu_vm", "pfu_vm"]
            }]
        }

        req_data = {
            "scaleVnfData": [
                {
                    "type": "SCALE_OUT",
                    "aspectId": "demo_aspect1",
                    "numberOfSteps": 1,
                    "additionalParam": vnfd_info
                },
                {
                    "type": "SCALE_OUT",
                    "aspectId": "demo_aspect2",
                    "numberOfSteps": 1,
                    "additionalParam": vnfd_info
                }
            ]
        }

        mock_vals = {
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
        r1 = [0, json.JSONEncoder().encode(vnfm_info_aai), '200']
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
        r1 = [0, json.JSONEncoder().encode(vim_info), '200']
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
            'volumn_storages': [

            ],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': u'2'
            },
            'local_storages': [

            ],
            'vdu_id': u'vdu_omm.001',
            'image_file': u'opencos_sss_omm_img_release_20150723-1-disk1',
            'dependencies': [

            ],
            'vls': [

            ],
            'cps': [

            ],
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
                    'tenant': ''
                },
                'inject_data_list': [

                ],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''
                },
                'local_affinity_antiaffinity_rule': {

                },
                'template_id': u'omm.001',
                'manual_scale_select_vim': False
            },
            'description': u'singleommvm'
        },
        {
            'volumn_storages': [

            ],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': u'4'
            },
            'local_storages': [

            ],
            'vdu_id': u'vdu_1',
            'image_file': u'sss',
            'dependencies': [

            ],
            'vls': [

            ],
            'cps': [

            ],
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
                    'tenant': ''
                },
                'inject_data_list': [

                ],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''
                },
                'local_affinity_antiaffinity_rule': {

                },
                'template_id': u'1',
                'manual_scale_select_vim': False
            },
            'description': u'ompvm'
        },
        {
            'volumn_storages': [

            ],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': u'14'
            },
            'local_storages': [

            ],
            'vdu_id': u'vdu_2',
            'image_file': u'sss',
            'dependencies': [

            ],
            'vls': [

            ],
            'cps': [

            ],
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
                    'tenant': ''
                },
                'inject_data_list': [

                ],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''
                },
                'local_affinity_antiaffinity_rule': {

                },
                'template_id': u'2',
                'manual_scale_select_vim': False
            },
            'description': u'ompvm'
        },
        {
            'volumn_storages': [

            ],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': u'14'
            },
            'local_storages': [

            ],
            'vdu_id': u'vdu_3',
            'image_file': u'sss',
            'dependencies': [

            ],
            'vls': [

            ],
            'cps': [

            ],
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
                    'tenant': ''
                },
                'inject_data_list': [

                ],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''
                },
                'local_affinity_antiaffinity_rule': {

                },
                'template_id': u'3',
                'manual_scale_select_vim': False
            },
            'description': u'ompvm'
        },
        {
            'volumn_storages': [

            ],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': u'4'
            },
            'local_storages': [

            ],
            'vdu_id': u'vdu_10',
            'image_file': u'sss',
            'dependencies': [

            ],
            'vls': [

            ],
            'cps': [

            ],
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
                    'tenant': ''
                },
                'inject_data_list': [

                ],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''
                },
                'local_affinity_antiaffinity_rule': {

                },
                'template_id': u'10',
                'manual_scale_select_vim': False
            },
            'description': u'ppvm'
        },
        {
            'volumn_storages': [

            ],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': u'14'
            },
            'local_storages': [

            ],
            'vdu_id': u'vdu_11',
            'image_file': u'sss',
            'dependencies': [

            ],
            'vls': [

            ],
            'cps': [

            ],
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
                    'tenant': ''
                },
                'inject_data_list': [

                ],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''
                },
                'local_affinity_antiaffinity_rule': {

                },
                'template_id': u'11',
                'manual_scale_select_vim': False
            },
            'description': u'ppvm'
        },
        {
            'volumn_storages': [

            ],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': u'14'
            },
            'local_storages': [

            ],
            'vdu_id': u'vdu_12',
            'image_file': u'sss',
            'dependencies': [

            ],
            'vls': [

            ],
            'cps': [

            ],
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
                    'tenant': ''
                },
                'inject_data_list': [

                ],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''
                },
                'local_affinity_antiaffinity_rule': {

                },
                'template_id': u'12',
                'manual_scale_select_vim': False
            },
            'description': u'ppvm'
        }
    ],
    'volumn_storages': [

    ],
    'policies': {
        'scaling': {
            'targets': {

            },
            'policy_id': u'policy_scale_sss-vnf-template',
            'properties': {
                'policy_file': '*-vnfd.zip/*-vnf-policy.xml'
            },
            'description': ''
        }
    },
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
                'hypervisor_type': 'kvm'
            },
            'image_file_id': u'opencos_sss_omm_img_release_20150723-1-disk1'
        },
        {
            'description': '',
            'properties': {
                'name': u'sss.vmdk',
                'checksum': '',
                'disk_format': u'VMDK',
                'file_url': u'./zte-cn-sss-main-image/NE/sss.vmdk',
                'container_type': 'vm',
                'version': '',
                'hypervisor_type': 'kvm'
            },
            'image_file_id': u'sss'
        }
    ],
    'vls': [

    ],
    'cps': [

    ],
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
        'name': u'sss-vnf-template'
    }
}

nsd_model_dict = {
    "vnffgs": [

    ],
    "inputs": {
        "externalDataNetworkName": {
            "default": "",
            "type": "string",
            "description": ""
        }
    },
    "pnfs": [

    ],
    "fps": [

    ],
    "server_groups": [

    ],
    "ns_flavours": [

    ],
    "vnfs": [
        {
            "dependency": [

            ],
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
                    "get_input": "externalDataNetworkName"
                },
                "id": "zte_vbras",
                "name": "vbras"
            },
            "vnf_id": "VBras",
            "networks": [

            ],
            "description": ""
        }
    ],
    "ns_exposed": {
        "external_cps": [

        ],
        "forward_cps": [

        ]
    },
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
                    "dc": ""
                },
                "end_ip": "190.168.100.100",
                "gateway_ip": "190.168.100.1",
                "start_ip": "190.168.100.2",
                "cidr": "190.168.100.0/24",
                "mtu": 1500,
                "network_name": "sub_mnet",
                "ip_version": 4
            }
        }
    ],
    "cps": [

    ],
    "policies": [

    ],
    "metadata": {
        "invariant_id": "vbras_ns",
        "description": "vbras_ns",
        "version": 1,
        "vendor": "zte",
        "id": "vbras_ns",
        "name": "vbras_ns"
    }
}

vserver_info = {
    "vserver-id": "example-vserver-id-val-70924",
    "vserver-name": "example-vserver-name-val-61674",
    "vserver-name2": "example-vserver-name2-val-19234",
    "prov-status": "example-prov-status-val-94916",
    "vserver-selflink": "example-vserver-selflink-val-26562",
    "in-maint": True,
    "is-closed-loop-disabled": True,
    "resource-version": "1505465356263",
    "volumes": {
        "volume": [
            {
                "volume-id": "example-volume-id-val-71854",
                "volume-selflink": "example-volume-selflink-val-22433"
            }
        ]
    },
    "l-interfaces": {
        "l-interface": [
            {
                "interface-name": "example-interface-name-val-24351",
                "interface-role": "example-interface-role-val-43242",
                "v6-wan-link-ip": "example-v6-wan-link-ip-val-4196",
                "selflink": "example-selflink-val-61295",
                "interface-id": "example-interface-id-val-95879",
                "macaddr": "example-macaddr-val-37302",
                "network-name": "example-network-name-val-44254",
                "management-option": "example-management-option-val-49009",
                "interface-description": "example-interface-description-val-99923",
                "is-port-mirrored": True,
                "in-maint": True,
                "prov-status": "example-prov-status-val-4698",
                "is-ip-unnumbered": True,
                "allowed-address-pairs": "example-allowed-address-pairs-val-5762",
                "vlans": {
                    "vlan": [
                        {
                            "vlan-interface": "example-vlan-interface-val-58193",
                            "vlan-id-inner": 54452151,
                            "vlan-id-outer": 70239293,
                            "speed-value": "example-speed-value-val-18677",
                            "speed-units": "example-speed-units-val-46185",
                            "vlan-description": "example-vlan-description-val-81675",
                            "backdoor-connection": "example-backdoor-connection-val-44608",
                            "vpn-key": "example-vpn-key-val-7946",
                            "orchestration-status": "example-orchestration-status-val-33611",
                            "in-maint": True,
                            "prov-status": "example-prov-status-val-8288",
                            "is-ip-unnumbered": True,
                            "l3-interface-ipv4-address-list": [
                                {
                                    "l3-interface-ipv4-address": "example-l3-interface-ipv4-address-val-25520",
                                    "l3-interface-ipv4-prefix-length": 69931928,
                                    "vlan-id-inner": 86628520,
                                    "vlan-id-outer": 62729236,
                                    "is-floating": True,
                                    "neutron-network-id": "example-neutron-network-id-val-64021",
                                    "neutron-subnet-id": "example-neutron-subnet-id-val-95049"
                                }
                            ],
                            "l3-interface-ipv6-address-list": [
                                {
                                    "l3-interface-ipv6-address": "example-l3-interface-ipv6-address-val-64310",
                                    "l3-interface-ipv6-prefix-length": 57919834,
                                    "vlan-id-inner": 79150122,
                                    "vlan-id-outer": 59789973,
                                    "is-floating": True,
                                    "neutron-network-id": "example-neutron-network-id-val-31713",
                                    "neutron-subnet-id": "example-neutron-subnet-id-val-89568"
                                }
                            ]
                        }
                    ]
                },
                "sriov-vfs": {
                    "sriov-vf": [
                        {
                            "pci-id": "example-pci-id-val-16747",
                            "vf-vlan-filter": "example-vf-vlan-filter-val-4613",
                            "vf-mac-filter": "example-vf-mac-filter-val-68168",
                            "vf-vlan-strip": True,
                            "vf-vlan-anti-spoof-check": True,
                            "vf-mac-anti-spoof-check": True,
                            "vf-mirrors": "example-vf-mirrors-val-6270",
                            "vf-broadcast-allow": True,
                            "vf-unknown-multicast-allow": True,
                            "vf-unknown-unicast-allow": True,
                            "vf-insert-stag": True,
                            "vf-link-status": "example-vf-link-status-val-49266",
                            "neutron-network-id": "example-neutron-network-id-val-29493"
                        }
                    ]
                },
                "l-interfaces": {
                    "l-interface": [
                        {
                            "interface-name": "example-interface-name-val-98222",
                            "interface-role": "example-interface-role-val-78360",
                            "v6-wan-link-ip": "example-v6-wan-link-ip-val-76921",
                            "selflink": "example-selflink-val-27117",
                            "interface-id": "example-interface-id-val-11260",
                            "macaddr": "example-macaddr-val-60378",
                            "network-name": "example-network-name-val-16258",
                            "management-option": "example-management-option-val-35097",
                            "interface-description": "example-interface-description-val-10475",
                            "is-port-mirrored": True,
                            "in-maint": True,
                            "prov-status": "example-prov-status-val-65203",
                            "is-ip-unnumbered": True,
                            "allowed-address-pairs": "example-allowed-address-pairs-val-65028"
                        }
                    ]
                },
                "l3-interface-ipv4-address-list": [
                    {
                        "l3-interface-ipv4-address": "example-l3-interface-ipv4-address-val-72779",
                        "l3-interface-ipv4-prefix-length": 55956636,
                        "vlan-id-inner": 98174431,
                        "vlan-id-outer": 20372128,
                        "is-floating": True,
                        "neutron-network-id": "example-neutron-network-id-val-39596",
                        "neutron-subnet-id": "example-neutron-subnet-id-val-51109"
                    }
                ],
                "l3-interface-ipv6-address-list": [
                    {
                        "l3-interface-ipv6-address": "example-l3-interface-ipv6-address-val-95203",
                        "l3-interface-ipv6-prefix-length": 57454747,
                        "vlan-id-inner": 53421060,
                        "vlan-id-outer": 16006050,
                        "is-floating": True,
                        "neutron-network-id": "example-neutron-network-id-val-54216",
                        "neutron-subnet-id": "example-neutron-subnet-id-val-1841"
                    }
                ]
            }
        ]
    }
}


vnfm_info = {
    "vnfm-id": "example-vnfm-id-val-97336",
    "vim-id": "zte_test",
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

vim_info = {
    "cloud-owner": "example-cloud-owner-val-97336",
    "cloud-region-id": "example-cloud-region-id-val-35532",
    "cloud-type": "example-cloud-type-val-18046",
    "owner-defined-type": "example-owner-defined-type-val-9413",
    "cloud-region-version": "example-cloud-region-version-val-85706",
    "identity-url": "example-identity-url-val-71252",
    "cloud-zone": "example-cloud-zone-val-27112",
    "complex-name": "example-complex-name-val-85283",
    "sriov-automation": True,
    "cloud-extra-info": "example-cloud-extra-info-val-90854",
    "cloud-epa-caps": "example-cloud-epa-caps-val-2409",
    "resource-version": "example-resource-version-val-42094",
    "esr-system-info-list": {
        "esr-system-info": [
            {
                "esr-system-info-id": "example-esr-system-info-id-val-7713",
                "system-name": "example-system-name-val-19801",
                "type": "example-type-val-24477",
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
                "default-tenant": "admin",
                "resource-version": "example-resource-version-val-15424"
            }
        ]
    }
}

nf_package_info = {
    "csarId": "zte_vbras",
    "packageInfo": {
        "vnfdId": "1",
        "vnfPackageId": "zte_vbras",
        "vnfdProvider": "1",
        "vnfdVersion": "1",
        "vnfVersion": "1",
        "csarName": "1",
        "vnfdModel": vnfd_model_dict,
        "downloadUrl": "1"
    },
    "imageInfo": []
}
