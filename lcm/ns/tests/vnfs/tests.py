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
from lcm.pub.utils.jobutil import JobUtil, JOB_TYPE


class TestGetVnfViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.nf_inst_id = str(uuid.uuid4())
        NfInstModel(nfinstid=self.nf_inst_id, nf_name='vnf1', vnfm_inst_id='1', vnf_id='vnf_id1',
                    status=VNF_STATUS.ACTIVE, create_time=now_time(), lastuptime=now_time()).save()

    def tearDown(self):
        NfInstModel.objects.all().delete()

    def test_get_vnf(self):
        response = self.client.get("/openoapi/nslcm/v1/ns/vnfs/%s" % self.nf_inst_id)
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
        response = self.client.post("/openoapi/nslcm/v1/ns/vnfs", data=self.data)
        self.failUnlessEqual(status.HTTP_202_ACCEPTED, response.status_code)
        context = json.loads(response.content)
        self.assertTrue(NfInstModel.objects.filter(nfinstid=context['vnfInstId']).exists())

    @mock.patch.object(restcall, 'call_req')
    def test_create_vnf_thread(self, mock_call_req):
        mock_vals = {
            "/openoapi/ztevmanagerdriver/v1/1/vnfs":
                [0, json.JSONEncoder().encode({"jobId": self.job_id, "vnfInstanceId": 3}), '200'],
            "/openoapi/extsys/v1/vnfms/1":
                [0, json.JSONEncoder().encode({"name": 'vnfm1'}), '200'],
            "/openoapi/resmgr/v1/vnf":
                [0, json.JSONEncoder().encode({}), '200'],
            "/openoapi/resmgr/v1/vnfinfo":
                [0, json.JSONEncoder().encode({}), '200'],
            "/openoapi/ztevmanagerdriver/v1/jobs/" + self.job_id + "&responseId=0":
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

        response = self.client.post("/openoapi/nslcm/v1/ns/vnfs/%s" % self.nf_inst_id, data=req_data)
        self.failUnlessEqual(status.HTTP_201_CREATED, response.status_code)

    @mock.patch.object(restcall, "call_req")
    def test_terminate_vnf(self, mock_call_req):
        job_id = JobUtil.create_job("VNF", JOB_TYPE.TERMINATE_VNF, self.nf_inst_id)

        nfinst = NfInstModel.objects.filter(nfinstid=self.nf_inst_id)
        if nfinst:
            self.failUnlessEqual(1, 1)
        else:
            self.failUnlessEqual(1, 0)

        mock_vals = {
            "/openoapi/ztevmanagerdriver/v1/1/vnfs/111/terminate":
                [0, json.JSONEncoder().encode({"jobId": job_id}), '200'],
            "/openoapi/extsys/v1/vnfms/1":
                [0, json.JSONEncoder().encode({"name": 'vnfm1', "type": 'ztevmanagerdriver'}), '200'],
            "/openoapi/resmgr/v1/vnf/1":
                [0, json.JSONEncoder().encode({"jobId": job_id}), '200'],
            "/openoapi/ztevmanagerdriver/v1/1/jobs/" + job_id + "?responseId=0":
                [0, json.JSONEncoder().encode({"jobId": job_id,
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

        req_data = {
            "terminationType": "forceful",
            "gracefulTerminationTimeout": "600"}

        def side_effect(*args):
            return mock_vals[args[4]]
        mock_call_req.side_effect = side_effect

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
            "/openoapi/ztevmanagerdriver/v1/1/vnfs/111/terminate":
                [0, json.JSONEncoder().encode({"jobId": job_id}), '200'],
            "/openoapi/ztevmanagerdriver/v1/1/vnfs/111/terminate":
                [0, json.JSONEncoder().encode({"jobId": job_id}), '200']
        }
        NFManualScaleService(self.nf_inst_id, req_data).run()
        nsIns = NfInstModel.objects.filter(nfinstid=self.nf_inst_id)
        if nsIns:
            self.failUnlessEqual(1, 1)
        else:
            self.failUnlessEqual(1, 0)

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
