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
import mock
from rest_framework import status
from django.test import TestCase
from django.test import Client

from lcm.pub.utils import restcall
from lcm.pub.database.models import NSDModel, NSInstModel, NfPackageModel


class TestNsPackage(TestCase):
    def setUp(self):
        self.client = Client()
        NSDModel.objects.filter().delete()
        NSInstModel.objects.filter().delete()
        NfPackageModel.objects.filter().delete()
        self.nsd_raw_data = {
            "rawData":{
                "instance":{
                    "metadata":{
                        "vendor":"ZTE",
                        "name":"VBRAS_NS",
                        "csarVersion":1,
                        "csarType":"NSAR",
                        "csarProvider":"ZTE",
                        "version":1,
                        "invariant_id":"VBRAS_NS_NO_SFC",
                        "id":"VBRAS_NS_ZTE_1.0",
                        "description":"VBRAS_ZTE_NS"
                    },
                    "nodes":[
                        {
                            "id":"VBras_yfye7lsgi73p8j4p2a6vbguzd",
                            "type_name":"tosca.nodes.nfv.ext.zte.VNF.VBras",
                            "template_name":"VBras",
                            "properties":{
                                "vendor":{
                                    "type_name":"string",
                                    "value":"zte"
                                },
                                "name":{
                                    "type_name":"string",
                                    "value":"vbras"
                                },
                                "version":{
                                    "type_name":"string",
                                    "value":"1.0"
                                },
                                "vnf_type":{
                                    "type_name":"string",
                                    "value":"vbras"
                                },
                                "vnfd_version":{
                                    "type_name":"string",
                                    "value":"1.0.0"
                                },
                                "id":{
                                    "type_name":"string",
                                    "value":"zte_vbras_1.0"
                                }
                            }
                        }
                    ]
                },
                "model":{
                    "metadata":{
                        "vendor":"ZTE",
                        "name":"VBRAS_NS",
                        "csarVersion":1,
                        "csarType":"NSAR",
                        "csarProvider":"ZTE",
                        "version":1,
                        "invariant_id":"VBRAS_NS_NO_SFC",
                        "id":"VBRAS_NS_ZTE_1.0",
                        "description":"VBRAS_ZTE_NS"
                    },
                    "node_templates":[
                        {
                            "name":"VBras",
                            "type_name":"tosca.nodes.nfv.ext.zte.VNF.VBras",
                            "default_instances":1,
                            "min_instances":0,
                            "properties":{
                                "vendor":{
                                    "type_name":"string",
                                    "value":"zte"
                                },
                                "name":{
                                    "type_name":"string",
                                    "value":"vbras"
                                },
                                "version":{
                                    "type_name":"string",
                                    "value":"1.0"
                                },
                                "vnf_type":{
                                    "type_name":"string",
                                    "value":"vbras"
                                },
                                "vnfd_version":{
                                    "type_name":"string",
                                    "value":"1.0.0"
                                },
                                "id":{
                                    "type_name":"string",
                                    "value":"zte_vbras_1.0"
                                }
                            },
                            "requirement_templates":[
                                {
                                    "name":"lb_mnet_vl_cp",
                                    "target_node_template_name":"ext_mnet_net",
                                    "target_capability_name":"virtual_linkable"
                                }
                            ]
                        }
                    ]
                }
            }
        }

    def tearDown(self):
        pass

    def set_nsd_metadata(self, key, val):
        self.nsd_raw_data["rawData"]["instance"]["metadata"][key] = val

    def set_nsd_vnf_id(self, val):
        self.nsd_raw_data["rawData"]["instance"]["nodes"][0]["properties"]["id"]["value"] = val

    @mock.patch.object(restcall, 'call_req')
    def test_ns_pkg_on_boarding_when_on_boarded(self, mock_call_req):
        mock_call_req.return_value = [0, json.JSONEncoder().encode({"onBoardState": "onBoarded"}), '200']
        resp = self.client.post("/openoapi/nslcm/v1/nspackage", {"csarId": "1"}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual("failed", resp.data["status"])
        self.assertEqual("CSAR(1) already onBoarded.", resp.data["statusDescription"])

    @mock.patch.object(restcall, 'call_req')
    def test_ns_pkg_on_boarding_when_nsd_already_exists(self, mock_call_req):
        self.set_nsd_metadata(key="id", val="2")
        mock_vals = {
            "/openoapi/catalog/v1/csars/2":
                [0, json.JSONEncoder().encode({"onBoardState": "non-onBoarded"}), '200'],
            "/openoapi/catalog/v1/servicetemplates/queryingrawdata":
                [0, json.JSONEncoder().encode(self.nsd_raw_data), '200']}

        def side_effect(*args):
            return mock_vals[args[4]]
        mock_call_req.side_effect = side_effect

        NSDModel(id="1", nsd_id="2").save()
        resp = self.client.post("/openoapi/nslcm/v1/nspackage", {"csarId": "2"}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual("failed", resp.data["status"])
        self.assertEqual("NSD(2) already exists.", resp.data["statusDescription"])

    @mock.patch.object(restcall, 'call_req')
    def test_ns_pkg_on_boarding_when_vnf_pkg_not_on_boarded(self, mock_call_req):
        self.set_nsd_metadata(key="id", val="2")
        self.set_nsd_vnf_id(val="3")
        mock_vals = {
            "/openoapi/catalog/v1/csars/3":
                [0, json.JSONEncoder().encode({"onBoardState": "non-onBoarded"}), '200'],
            "/openoapi/catalog/v1/servicetemplates/queryingrawdata":
                [0, json.JSONEncoder().encode(self.nsd_raw_data), '200']}

        def side_effect(*args):
            return mock_vals[args[4]]
        mock_call_req.side_effect = side_effect

        resp = self.client.post("/openoapi/nslcm/v1/nspackage", {"csarId": "3"}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual("failed", resp.data["status"])
        self.assertEqual("VNF package(3) is not onBoarded.", resp.data["statusDescription"])

    @mock.patch.object(restcall, 'call_req')
    def test_ns_pkg_on_boarding_when_vnf_pkg_not_on_boarded_on_catalog(self, mock_call_req):
        self.set_nsd_metadata(key="id", val="2")
        self.set_nsd_vnf_id(val="6")
        mock_vals = {
            "/openoapi/catalog/v1/csars/4":
                [0, json.JSONEncoder().encode({"onBoardState": "non-onBoarded"}), '200'],
            "/openoapi/catalog/v1/servicetemplates/queryingrawdata":
                [0, json.JSONEncoder().encode(self.nsd_raw_data), '200'],
            "/openoapi/catalog/v1/csars/5":
                [0, json.JSONEncoder().encode({"onBoardState": "non-onBoarded"}), '200'], }

        def side_effect(*args):
            return mock_vals[args[4]]
        mock_call_req.side_effect = side_effect

        NfPackageModel(uuid="1", nfpackageid="5", vnfdid="6").save()
        resp = self.client.post("/openoapi/nslcm/v1/nspackage", {"csarId": "4"}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual("failed", resp.data["status"])
        self.assertEqual("VNF package(5) is not onBoarded on catalog.", resp.data["statusDescription"])

    @mock.patch.object(restcall, 'call_req')
    def test_ns_pkg_on_boarding_when_on_board_success(self, mock_call_req):
        self.set_nsd_metadata(key="id", val="2")
        self.set_nsd_metadata(key="name", val="3")
        self.set_nsd_metadata(key="vendor", val="4")
        self.set_nsd_metadata(key="description", val="5")
        self.set_nsd_metadata(key="version", val="6")
        self.set_nsd_vnf_id(val="7")
        mock_vals = {
            "/openoapi/catalog/v1/csars/5":
                [0, json.JSONEncoder().encode({
                    "onBoardState": "non-onBoarded",
                    "createTime": "2016-05-15 12:30:34",
                    "modifyTime": "2016-05-15 12:30:34"}), '200'],
            "/openoapi/catalog/v1/servicetemplates/queryingrawdata":
                [0, json.JSONEncoder().encode(self.nsd_raw_data), '200'],
            "/openoapi/catalog/v1/csars/6":
                [0, json.JSONEncoder().encode({"onBoardState": "onBoarded"}), '200'],
            "/openoapi/catalog/v1/csars/5?operationalState=Enabled": [0, '{}', 200],
            "/openoapi/catalog/v1/csars/5?onBoardState=onBoarded": [0, "OK", '200']}

        def side_effect(*args):
            return mock_vals[args[4]]

        mock_call_req.side_effect = side_effect

        NfPackageModel(uuid="1", nfpackageid="6", vnfdid="7").save()
        resp = self.client.post("/openoapi/nslcm/v1/nspackage", {"csarId": "5"}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual("success", resp.data["status"])
        self.assertEqual("CSAR(5) onBoarded successfully.", resp.data["statusDescription"])
        nsds = NSDModel.objects.filter(id="5")
        self.assertEqual(1, len(nsds))
        self.assertEqual("2", nsds[0].nsd_id)

    ###############################################################################################################
    @mock.patch.object(restcall, 'call_req')
    def test_delete_csar_when_id_not_exist(self, mock_call_req):
        mock_call_req.return_value = [0, "", '204']
        resp = self.client.delete("/openoapi/nslcm/v1/nspackage/6")
        self.assertEqual(resp.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual("success", resp.data["status"])
        self.assertEqual("Delete CSAR(6) successfully.", resp.data["statusDescription"])

    @mock.patch.object(restcall, 'call_req')
    def test_delete_csar_when_ref_by_ns_inst(self, mock_call_req):
        mock_call_req.return_value = [0, "OK", '200']

        NSDModel(id="7", nsd_id="2").save()
        NSInstModel(id="1", nspackage_id="7").save()

        resp = self.client.delete("/openoapi/nslcm/v1/nspackage/7")
        self.assertEqual(resp.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual("success", resp.data["status"])
        self.assertEqual("Set deletionPending to True of CSAR(7) successfully.",
                         resp.data["statusDescription"])

    @mock.patch.object(restcall, 'call_req')
    def test_delete_csar_when_delete_success(self, mock_call_req):
        mock_call_req.return_value = [0, "OK", '204']

        NSDModel(id="8", nsd_id="2").save()

        resp = self.client.delete("/openoapi/nslcm/v1/nspackage/8")
        self.assertEqual(resp.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual("success", resp.data["status"])
        self.assertEqual("Delete CSAR(8) successfully.", resp.data["statusDescription"])

    ###############################################################################################################
    def test_delete_pending_csar_when_id_not_exist(self):
        resp = self.client.delete("/openoapi/nslcm/v1/nspackage/9/deletionpending")
        self.assertEqual(resp.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual("success", resp.data["status"])
        self.assertEqual("Delete pending CSAR(9) successfully.", resp.data["statusDescription"])

    @mock.patch.object(restcall, 'call_req')
    def test_delete_pending_csar_when_pending_is_false(self, mock_call_req):
        mock_call_req.return_value = [0, '{"deletionPending": "false"}', '200']
        NSDModel(id="10", nsd_id="2").save()
        resp = self.client.delete("/openoapi/nslcm/v1/nspackage/10/deletionpending")
        self.assertEqual(resp.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual("failed", resp.data["status"])
        self.assertEqual("CSAR(10) need not to be deleted.", resp.data["statusDescription"])

    @mock.patch.object(restcall, 'call_req')
    def test_delete_pending_csar_when_refed_by_ns(self, mock_call_req):
        mock_call_req.return_value = [0, '{"deletionPending": "true"}', '200']
        NSDModel(id="11", nsd_id="2").save()
        NSInstModel(id="1", nspackage_id="11").save()
        resp = self.client.delete("/openoapi/nslcm/v1/nspackage/11/deletionpending")
        self.assertEqual(resp.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual("failed", resp.data["status"])
        self.assertEqual("CSAR(11) is in using, cannot be deleted.", resp.data["statusDescription"])

    @mock.patch.object(restcall, 'call_req')
    def test_delete_pending_csar_when_delete_success(self, mock_call_req):
        mock_call_req.side_effect = [
            [0, '{"deletionPending": "true"}', '200'],
            [0, "OK", '204']]
        NSDModel(id="12", nsd_id="2").save()
        resp = self.client.delete("/openoapi/nslcm/v1/nspackage/12/deletionpending")
        self.assertEqual(resp.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual("success", resp.data["status"])
        self.assertEqual("Delete CSAR(12) successfully.", resp.data["statusDescription"])

    ###############################################################################################################
    @mock.patch.object(restcall, 'call_req')
    def test_get_csar_successfully(self, mock_call_req):
        mock_call_req.return_value = [0, json.JSONEncoder().encode({
            "name": "1",
            "provider": "2",
            "version": "3",
            "operationalState": "4",
            "usageState": "5",
            "onBoardState": "6",
            "processState": "7",
            "deletionPending": "8",
            "downloadUri": "9",
            "createTime": "10",
            "modifyTime": "11",
            "format": "12",
            "size": "13"
            }), '200']

        NSDModel(id="13", nsd_id="2", vendor="3", version="4").save()
        NSInstModel(id="1", nspackage_id="13", name="11").save()
        NSInstModel(id="2", nspackage_id="13", name="22").save()

        resp = self.client.get("/openoapi/nslcm/v1/nspackage/13")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        expect_data = {"nsInstanceInfo": [{"nsInstanceId": "1", "nsInstanceName": "11"},
                                          {"nsInstanceId": "2", "nsInstanceName": "22"}], "csarId": "13",
                       "packageInfo": {"nsdProvider": "3", "usageState": "5",
                                       "onBoardState": "6", "name": "1", "format": "12",
                                       "modifyTime": "11", "nsdId": "2", "nsdVersion": "4",
                                       "deletionPending": "8", "version": "3", "downloadUri": "9",
                                       "processState": "7", "provider": "2", "operationalState": "4",
                                       "createTime": "10", "size": "13"}}
        self.assertEqual(expect_data, resp.data)

    ###############################################################################################################
    def test_disable_csar_when_id_not_exist_table(self):
        resp = self.client.put("/openoapi/nslcm/v1/nspackage/14/disabled")
        self.assertEqual(resp.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual("failed", resp.data["status"])
        self.assertEqual("CSAR(14) does not exist.", resp.data["statusDescription"])

    @mock.patch.object(restcall, 'call_req')
    def test_disable_csar_when_csar_is_disabled(self, mock_call_req):
        NSDModel(id="15", nsd_id="2").save()
        mock_call_req.return_value = [0, json.JSONEncoder().encode({"operationalState": "Disabled"}), '200']
        resp = self.client.put("/openoapi/nslcm/v1/nspackage/15/disabled")
        self.assertEqual(resp.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual("failed", resp.data["status"])
        self.assertEqual("CSAR(15) already disabled.", resp.data["statusDescription"])

    @mock.patch.object(restcall, 'call_req')
    def test_disable_csar_successfully(self, mock_call_req):
        NSDModel(id="16", nsd_id="2").save()
        mock_vals = {
            "/openoapi/catalog/v1/csars/16":
                [0, json.JSONEncoder().encode({"operationalState": "Enabled"}), '200'],
            "/openoapi/catalog/v1/csars/16?operationState=Disabled":
                [0, "OK", '200']}

        def side_effect(*args):
            return mock_vals[args[4]]
        mock_call_req.side_effect = side_effect

        resp = self.client.put("/openoapi/nslcm/v1/nspackage/16/disabled")
        self.assertEqual(resp.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual("success", resp.data["status"])
        self.assertEqual("Set operationState to Disabled of CSAR(16) successfully.", resp.data["statusDescription"])

    ###############################################################################################################
    def test_enable_csar_when_id_not_exist_table(self):
        resp = self.client.put("/openoapi/nslcm/v1/nspackage/17/enabled")
        self.assertEqual(resp.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual("failed", resp.data["status"])
        self.assertEqual("CSAR(17) does not exist.", resp.data["statusDescription"])

    @mock.patch.object(restcall, 'call_req')
    def test_enable_csar_when_csar_is_enabled(self, mock_call_req):
        NSDModel(id="18", nsd_id="2").save()
        mock_call_req.return_value = [0, json.JSONEncoder().encode({"operationalState": "Enabled"}), '200']
        resp = self.client.put("/openoapi/nslcm/v1/nspackage/18/enabled")
        self.assertEqual(resp.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual("failed", resp.data["status"])
        self.assertEqual("CSAR(18) already enabled.", resp.data["statusDescription"])

    @mock.patch.object(restcall, 'call_req')
    def test_enable_csar_successfully(self, mock_call_req):
        NSDModel(id="19", nsd_id="2").save()
        mock_vals = {
            "/openoapi/catalog/v1/csars/19":
                [0, json.JSONEncoder().encode({"operationalState": "Disabled"}), '200'],
            "/openoapi/catalog/v1/csars/19?operationState=Enabled":
                [0, "OK", '200']}

        def side_effect(*args):
            return mock_vals[args[4]]
        mock_call_req.side_effect = side_effect

        resp = self.client.put("/openoapi/nslcm/v1/nspackage/19/enabled")
        self.assertEqual(resp.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual("success", resp.data["status"])
        self.assertEqual("Set operationState to Enabled of CSAR(19) successfully.", resp.data["statusDescription"])