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
import uuid

import mock
from django.test import TestCase, Client
from rest_framework import status

from lcm.pub.database.models import VLInstModel, NSInstModel, VNFFGInstModel
from lcm.pub.nfvi.vim import vimadaptor
from lcm.pub.utils import restcall
from lcm.ns_vnfs.tests.tests import vim_info


class TestVlViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.ns_inst_id = str(uuid.uuid4())
        self.vnffg_id = str(uuid.uuid4())
        self.vl_id_1 = 1
        self.vl_id_2 = 1
        self.vim_id = str(uuid.uuid4())
        self.tenant = "tenantname"
        properties = {"network_type": "vlan", "name": "externalMNetworkName", "dhcp_enabled": False,
                      "location_info": {"host": True, "vimid": self.vim_id, "region": True, "tenant": self.tenant},
                      "end_ip": "190.168.100.100", "gateway_ip": "190.168.100.1", "start_ip": "190.168.100.2",
                      "cidr": "190.168.100.0/24", "mtu": 1500, "network_name": "sub_mnet", "ip_version": 4}
        self.context = {
            "vls": [{"vl_id": self.vl_id_1, "description": "", "properties": properties, "route_external": False},
                    {"vl_id": self.vl_id_2, "description": "", "properties": properties, "route_external": False}],
            "vnffgs": [{"vnffg_id": self.vnffg_id, "description": "",
                        "properties": {"vendor": "zte", "version": "1.1.2", "number_of_endpoints": 7,
                                       "dependent_virtual_link": [self.vl_id_2, self.vl_id_1],
                                       "connection_point": ["CP01", "CP02"],
                                       "constituent_vnfs": ["VNF1", "VNF2", "VNF3"],
                                       "constituent_pnfs": ["pnf1", "pnf2"]},
                        "members": ["forwarding_path1", "forwarding_path2"]}]}
        NSInstModel(id=self.ns_inst_id, name="ns_name").save()
        VNFFGInstModel(vnffgdid=self.vnffg_id, vnffginstid="", nsinstid=self.ns_inst_id, endpointnumber=0, vllist="",
                       cplist="", vnflist="", fplist="", status="").save()

    def tearDown(self):
        VLInstModel.objects.all().delete()
        NSInstModel.objects.all().delete()
        VNFFGInstModel.objects.all().delete()

    '''
    @mock.patch.object(restcall, "call_req")
    @mock.patch.object(vimadaptor.VimAdaptor, "create_network")
    def test_create_vl(self, mock_create_network, mock_req_by_rest):
        network_id = str(uuid.uuid4())
        subnetwork_id = str(uuid.uuid4())
        mock_create_network.return_value = [0,
                                            {"status": "ACTIVE", "id": network_id, "name": "net1",
                                             "provider:segmentation_id": 204, "provider:network_type": "vlan",
                                             "res_type": 1,
                                             "subnet_list": [
                                                 {"id": subnetwork_id, "name": "subnet1", "res_type": 1}]}]
        mock_req_by_rest.return_value = [0, json.JSONEncoder().encode(vim_info), '200']

        self.create_vl(self.vl_id_1)
        self.create_vl(self.vl_id_2)
        vl_from_vl_1 = VLInstModel.objects.filter(vldid=self.vl_id_1, ownerid=self.ns_inst_id)
        self.assertEqual(network_id, vl_from_vl_1[0].relatednetworkid)
        self.assertEqual(subnetwork_id, vl_from_vl_1[0].relatedsubnetworkid)
        self.assertEqual(self.tenant, vl_from_vl_1[0].tenant)
        vl_from_vl_2 = VLInstModel.objects.filter(vldid=self.vl_id_2, ownerid=self.ns_inst_id)
        self.assertEqual(VNFFGInstModel.objects.filter(vnffgdid=self.vnffg_id, nsinstid=self.ns_inst_id)[0].vllist,
                         vl_from_vl_2[0].vlinstanceid + "," + vl_from_vl_1[0].vlinstanceid)
    '''

    def create_vl(self, vl_id):
        req_data = {
            "nsInstanceId": self.ns_inst_id,
            "context": json.JSONEncoder().encode(self.context),
            "vlIndex": vl_id}
        response = self.client.post("/api/nslcm/v1/ns/ns_vls", data=req_data)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(0, response.data["result"], response.data)

    '''
    @mock.patch.object(restcall, "call_req")
    @mock.patch.object(vimadaptor.VimAdaptor, "create_network")
    @mock.patch.object(uuid, "uuid4")
    def test_create_network_fail_when_send_to_vim(self, mock_uuid4, mock_create_network, mock_req_by_rest):
        req_data = {
            "nsInstanceId": self.ns_inst_id,
            "context": json.JSONEncoder().encode(self.context),
            "vlIndex": self.vl_id_1}
        mock_uuid4.return_value = '999'
        mock_req_by_rest.return_value = [0, json.JSONEncoder().encode(vim_info), '200']
        mock_create_network.return_value = [1, (1)]
        response = self.client.post("/api/nslcm/v1/ns/ns_vls", data=req_data)
        retinfo = {"detail": "vl instantiation failed, detail message: Send post vl request to vim failed."}
        self.assertEqual(retinfo["detail"], response.data["detail"])
    '''


class TestVlDetailViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.vl_inst_id = str(uuid.uuid4())
        self.vl_name = str(uuid.uuid4())
        self.ns_inst_id = str(uuid.uuid4())
        VLInstModel(vlinstanceid=self.vl_inst_id, vldid="", vlinstancename=self.vl_name, ownertype=1,
                    ownerid=self.ns_inst_id, relatednetworkid="network1", relatedsubnetworkid="subnet1,subnet2",
                    vimid='{"cloud_owner": "VCPE", "cloud_regionid": "RegionOne"}',
                    tenant="").save()
        VNFFGInstModel(vnffgdid="", vnffginstid="", nsinstid=self.ns_inst_id,
                       vllist="test1," + self.vl_inst_id + ",test2,test3", endpointnumber=0, cplist="", vnflist="",
                       fplist="", status="").save()

    def tearDown(self):
        VLInstModel.objects.all().delete()
        VNFFGInstModel.objects.all().delete()

    @mock.patch.object(restcall, "call_req")
    @mock.patch.object(vimadaptor.VimAdaptor, "delete_network")
    @mock.patch.object(vimadaptor.VimAdaptor, "delete_subnet")
    def test_delete_vl(self, mock_delete_subnet, mock_delete_network, mock_req_by_rest):
        mock_req_by_rest.return_value = [0, json.JSONEncoder().encode(vim_info), '200']
        response = self.client.delete("/api/nslcm/v1/ns/vls/%s" % self.vl_inst_id)
        self.assertEqual(status.HTTP_202_ACCEPTED, response.status_code)
        expect_resp_data = {"result": 0, "detail": "delete vl success"}
        self.assertEqual(expect_resp_data, response.data)

        for vnffg_info in VNFFGInstModel.objects.filter(nsinstid=self.ns_inst_id):
            self.assertEqual(vnffg_info.vllist, "test1,test2,test3")
        if VLInstModel.objects.filter(vlinstanceid=self.vl_inst_id):
            self.fail()

        response = self.client.delete("/api/nslcm/v1/ns/vls/%s" % "notExist")
        self.assertEqual(status.HTTP_202_ACCEPTED, response.status_code)
        expect_resp_data = {"result": 0, "detail": "vl is not exist or has been already deleted"}
        self.assertEqual(expect_resp_data, response.data)

    def test_query_vl(self):
        response = self.client.get("/api/nslcm/v1/ns/vls/%s" % self.vl_inst_id)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        expect_resp_data = {'vlId': self.vl_inst_id, 'vlName': self.vl_name, 'vlStatus': "active"}
        self.assertEqual(expect_resp_data, response.data)

        response = self.client.get("/api/nslcm/v1/ns/ns_vls/%s" % "notExist")
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
