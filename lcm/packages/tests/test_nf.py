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

import mock
from django.test import Client
from django.test import TestCase
from rest_framework import status

from lcm.packages.nf_package import NfOnBoardingThread, NfPkgDeletePendingThread
from lcm.packages.nf_package import NfPkgDeleteThread
from lcm.pub.database.models import JobStatusModel, JobModel
from lcm.pub.database.models import NfPackageModel, VnfPackageFileModel, NfInstModel
from lcm.pub.nfvi.vim.vimadaptor import VimAdaptor
from lcm.pub.utils import fileutil
from lcm.pub.utils import restcall


class TestNfPackage(TestCase):
    def setUp(self):
        self.client = Client()
        NfPackageModel.objects.filter().delete()
        VnfPackageFileModel.objects.filter().delete()
        NfInstModel.objects.filter().delete()
        JobModel.objects.filter().delete()
        JobStatusModel.objects.filter().delete()
        self.vnfd_raw_data = {
            "rawData": {
                "instance": {
                    "metadata": {
                        "is_shared": False,
                        "plugin_info": "vbrasplugin_1.0",
                        "vendor": "zte",
                        "request_reclassification": False,
                        "name": "vbras",
                        "version": 1,
                        "vnf_type": "vbras",
                        "cross_dc": False,
                        "vnfd_version": "1.0.0",
                        "id": "zte_vbras_1.0",
                        "nsh_aware": True
                    },
                    "nodes": [
                        {
                            "id": "aaa_dnet_cp_0xu2j5sbigxc8h1ega3if0ld1",
                            "type_name": "tosca.nodes.nfv.ext.zte.CP",
                            "template_name": "aaa_dnet_cp",
                            "properties": {
                                "bandwidth": {
                                    "type_name": "integer",
                                    "value": 0
                                },
                                "direction": {
                                    "type_name": "string",
                                    "value": "bidirectional"
                                },
                                "vnic_type": {
                                    "type_name": "string",
                                    "value": "normal"
                                },
                                "sfc_encapsulation": {
                                    "type_name": "string",
                                    "value": "mac"
                                },
                                "order": {
                                    "type_name": "integer",
                                    "value": 2
                                }
                            },
                            "relationships": [
                                {
                                    "name": "guest_os",
                                    "source_requirement_index": 0,
                                    "target_node_id": "AAA_image_d8aseebr120nbm7bo1ohkj194",
                                    "target_capability_name": "feature"
                                }
                            ]
                        },
                        {
                            "id": "LB_Image_oj5l2ay8l2g6vcq6fsswzduha",
                            "type_name": "tosca.nodes.nfv.ext.ImageFile",
                            "template_name": "LB_Image",
                            "properties": {
                                "disk_format": {
                                    "type_name": "string",
                                    "value": "qcow2"
                                },
                                "file_url": {
                                    "type_name": "string",
                                    "value": "/SoftwareImages/image-lb"
                                },
                                "name": {
                                    "type_name": "string",
                                    "value": "image-lb"
                                }
                            }
                        }
                    ]
                },
                "model": {
                    "metadata": {
                        "is_shared": False,
                        "plugin_info": "vbrasplugin_1.0",
                        "vendor": "zte",
                        "request_reclassification": False,
                        "name": "vbras",
                        "version": 1,
                        "vnf_type": "vbras",
                        "cross_dc": False,
                        "vnfd_version": "1.0.0",
                        "id": "zte_vbras_1.0",
                        "nsh_aware": True
                    },
                    "node_templates": [
                        {
                            "name": "aaa_dnet_cp",
                            "type_name": "tosca.nodes.nfv.ext.zte.CP",
                            "default_instances": 1,
                            "min_instances": 0,
                            "properties": {
                                "bandwidth": {
                                    "type_name": "integer",
                                    "value": 0
                                }
                            },
                            "requirement_templates": [
                                {
                                    "name": "virtualbinding",
                                    "target_node_template_name": "AAA",
                                    "target_capability_name": "virtualbinding"
                                }
                            ]
                        }
                    ]
                }
            }
        }

    def tearDown(self):
        pass

    def assert_job_result(self, job_id, job_progress, job_detail):
        jobs = JobStatusModel.objects.filter(
            jobid=job_id,
            progress=job_progress,
            descp=job_detail)
        self.assertEqual(1, len(jobs))

    @mock.patch.object(NfOnBoardingThread, 'run')
    def test_nf_pkg_on_boarding_normal(self, mock_run):
        resp = self.client.post("/api/nslcm/v0/vnfpackage", {
            "csarId": "1",
            "vimIds": ["1"]
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_202_ACCEPTED)

    @mock.patch.object(restcall, 'call_req')
    def test_nf_pkg_on_boarding_when_on_boarded(self, mock_call_req):
        mock_call_req.return_value = [0, json.JSONEncoder().encode({"onBoardState": "onBoarded"}), '200']
        NfOnBoardingThread(csar_id="1",
                           vim_ids=["1"],
                           lab_vim_id="",
                           job_id="2").run()
        self.assert_job_result("2", 255, "CSAR(1) already onBoarded.")

    @mock.patch.object(restcall, 'call_req')
    def test_nf_pkg_on_boarding_when_on_boarding(self, mock_call_req):
        mock_call_req.return_value = [0, json.JSONEncoder().encode({
            "onBoardState": "non-onBoarded",
            "processState": "onBoarding"
        }), '200']
        NfOnBoardingThread(csar_id="2",
                           vim_ids=["1"],
                           lab_vim_id="",
                           job_id="3").run()
        self.assert_job_result("3", 255, "CSAR(2) is onBoarding now.")

    @mock.patch.object(restcall, 'call_req')
    def test_nf_on_boarding_when_nfd_already_exists(self, mock_call_req):
        mock_vals = {
            "/api/catalog/v1/csars/2":
                [0, json.JSONEncoder().encode({
                    "onBoardState": "onBoardFailed", "processState": "deleteFailed"}), '200'],
            "/api/catalog/v1/servicetemplates/queryingrawdata":
                [0, json.JSONEncoder().encode(self.vnfd_raw_data), '200']}

        def side_effect(*args):
            return mock_vals[args[4]]

        mock_call_req.side_effect = side_effect
        NfPackageModel(uuid="1", nfpackageid="2", vnfdid="zte_vbras_1.0").save()
        NfOnBoardingThread(csar_id="2", vim_ids=["1"], lab_vim_id="", job_id="4").run()
        self.assert_job_result("4", 255, "NFD(zte_vbras_1.0) already exists.")

    @mock.patch.object(restcall, 'call_req')
    @mock.patch.object(fileutil, 'download_file_from_http')
    @mock.patch.object(VimAdaptor, '__init__')
    @mock.patch.object(VimAdaptor, 'create_image')
    @mock.patch.object(VimAdaptor, 'get_image')
    def test_nf_on_boarding_when_successfully(self, mock_get_image, mock_create_image,
                                              mock__init__, mock_download_file_from_http, mock_call_req):
        mock_download_file_from_http.return_value = True, "/root/package"
        mock_vals = {
            "/api/catalog/v1/csars/2":
                [0, json.JSONEncoder().encode({
                    "onBoardState": "onBoardFailed", "processState": "deleteFailed"}), '200'],
            "/api/catalog/v1/servicetemplates/queryingrawdata":
                [0, json.JSONEncoder().encode(self.vnfd_raw_data), '200'],
            "/api/catalog/v1/csars/2/files?relativePath=/SoftwareImages/image-lb":
                [0, json.JSONEncoder().encode({
                    "csar_file_info": [{"downloadUri": "8"}, {"localPath": "9"}]}), '200'],
            "/cloud-infrastructure/cloud-regions?depth=all":
                [0, json.JSONEncoder().encode(vims_info), '200'],
            "/api/catalog/v1/csars/2?onBoardState=onBoarded": [0, '{}', 200],
            "/api/catalog/v1/csars/2?operationalState=Enabled": [0, '{}', 200],
            "/api/catalog/v1/csars/2?processState=normal": [0, '{}', 200]}
        mock_create_image.return_value = [0, {"id": "30", "name": "jerry", "res_type": 0}]
        mock__init__.return_value = None
        mock_get_image.return_value = [0, {"id": "30", "name": "jerry", "size": "60", "status": "active"}]

        def side_effect(*args):
            return mock_vals[args[4]]
        mock_call_req.side_effect = side_effect

        NfOnBoardingThread(csar_id="2", vim_ids=["1"], lab_vim_id="", job_id="4").run()
        self.assert_job_result("4", 100, "CSAR(2) onBoarding successfully.")

    # @mock.patch.object(restcall, 'call_req')
    # @mock.patch.object(fileutil, 'download_file_from_http')
    # @mock.patch.object(VimAdaptor, '__init__')
    # @mock.patch.object(VimAdaptor, 'create_image')
    # @mock.patch.object(VimAdaptor, 'get_image')
    # def test_nf_on_boarding_when_timeout(self, mock_get_image, mock_create_image,
    #                                      mock__init__, mock_download_file_from_http, mock_call_req):
    #     nf_package.MAX_RETRY_TIMES = 2
    #     nf_package.SLEEP_INTERVAL_SECONDS = 1
    #     mock_download_file_from_http.return_value = True, "/root/package"
    #     mock_vals = {
    #         "/api/catalog/v1/csars/3":
    #         [0, json.JSONEncoder().encode({"onBoardState": "onBoardFailed",
    #                                        "processState": "deleteFailed"}), '200'],
    #         "/api/catalog/v1/servicetemplates/queryingrawdata":
    #             [0, json.JSONEncoder().encode(self.vnfd_raw_data), '200'],
    #         "/api/catalog/v1/csars/3/files?relativePath=/SoftwareImages/image-lb":
    #             [0, json.JSONEncoder().encode({
    #                 "csar_file_info": [{"downloadUri": "8"}, {"localPath": "9"}]}), '200'],
    #         "/api/catalog/v1/csars/3?processState=onBoardFailed": [0, '{}', 200],
    #         "/cloud-infrastructure/cloud-regions?depth=all":
    #             [0, json.JSONEncoder().encode(vims_info), 200]}
    #     mock_create_image.return_value = [0, {"id": "30", "name": "jerry", "res_type": 0}]
    #     mock__init__.return_value = None
    #     mock_get_image.return_value = [0, {"id": "30", "name": "jerry", "size": "60", "status": "0"}]
    #
    #     def side_effect(*args):
    #         return mock_vals[args[4]]
    #
    #     mock_call_req.side_effect = side_effect
    #     NfOnBoardingThread(csar_id="3", vim_ids=["1"], lab_vim_id="", job_id="6").run()
    #     self.assert_job_result("6", 255, "Failed to create image:timeout(2 seconds.)")

    # @mock.patch.object(restcall, 'call_req')
    # @mock.patch.object(fileutil, 'download_file_from_http')
    # @mock.patch.object(VimAdaptor, '__init__')
    # @mock.patch.object(VimAdaptor, 'create_image')
    # def test_nf_on_boarding_when_failed_to_create_image(self, mock_create_image,
    #                                                     mock__init__, mock_download_file_from_http, mock_call_req):
    #     mock_download_file_from_http.return_value = True, "/root/package"
    #     mock_vals = {
    #         "/api/catalog/v1/csars/5":
    #             [0, json.JSONEncoder().encode({
    #                 "onBoardState": "onBoardFailed", "processState": "deleteFailed"}), '200'],
    #         "/api/catalog/v1/servicetemplates/queryingrawdata":
    #             [0, json.JSONEncoder().encode(self.vnfd_raw_data), '200'],
    #         "/api/catalog/v1/csars/5/files?relativePath=/SoftwareImages/image-lb":
    #             [0, json.JSONEncoder().encode({
    #                 "csar_file_info": [{"downloadUri": "8"}, {"localPath": "9"}]}), '200'],
    #         "/api/catalog/v1/csars/5?processState=onBoardFailed": [0, '{}', 200],
    #         "/cloud-infrastructure/cloud-regions?depth=all":
    #             [0, json.JSONEncoder().encode(vims_info), '200']}
    #     mock_create_image.return_value = [1, 'Unsupported image format.']
    #     mock__init__.return_value = None
    #
    #     def side_effect(*args):
    #         return mock_vals[args[4]]
    #     mock_call_req.side_effect = side_effect
    #     NfOnBoardingThread(csar_id="5", vim_ids=["1"], lab_vim_id="", job_id="8").run()
    #     self.assert_job_result("8", 255, "Failed to create image:Unsupported image format.")

    #########################################################################
    @mock.patch.object(restcall, 'call_req')
    def test_get_csar_successfully(self, mock_call_req):
        mock_call_req.return_value = [0, json.JSONEncoder().encode({
            "name": "1", "provider": "2", "version": "3", "operationalState": "4",
            "usageState": "5", "onBoardState": "6", "processState": "7",
            "deletionPending": "8", "downloadUri": "9", "createTime": "10",
            "modifyTime": "11", "format": "12", "size": "13"
        }), '200']
        NfPackageModel(uuid="1", vnfdid="001", vendor="vendor",
                       vnfdversion="1.2.0", vnfversion="1.1.0", nfpackageid="13").save()
        VnfPackageFileModel(id="1", filename="filename", imageid="00001",
                            vimid="1", vimuser="001", tenant="12", status="1", vnfpid="13").save()
        NfInstModel(nfinstid="1", mnfinstid="001", nf_name="name", package_id="13").save()
        resp = self.client.get("/api/nslcm/v0/vnfpackage/13")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        expect_data = {
            "csarId": '13',
            "packageInfo": {
                "vnfdId": "001",
                "vnfdProvider": "vendor",
                "vnfdVersion": "1.2.0",
                "vnfVersion": "1.1.0",
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
                "size": "13"},
            "imageInfo": [{
                "index": "0",
                "fileName": "filename",
                "imageId": "00001",
                "vimId": "1",
                "vimUser": "001",
                "tenant": "12",
                "status": "1"}],
            "vnfInstanceInfo": [{
                "vnfInstanceId": "1",
                "vnfInstanceName": "name"}]}
        self.assertEqual(expect_data, resp.data)

    #########################################################################
    @mock.patch.object(restcall, 'call_req')
    def test_delete_pending_csar_when_successfully(self, mock_call_req):
        mock_call_req.return_value = [0, json.JSONEncoder().encode({
            "processState": "deleting"}), "200"]
        NfPkgDeletePendingThread(csar_id="1", job_id='2').run()
        self.assert_job_result("2", 100, "Delete pending CSAR(1) successfully.")

    @mock.patch.object(restcall, 'call_req')
    def test_delete_pending_csar_when_deleting(self, mock_call_req):
        NfPackageModel(uuid="01", nfpackageid="1").save()
        mock_call_req.return_value = [0, json.JSONEncoder().encode({
            "processState": "deleting"}), "200"]
        NfPkgDeletePendingThread(csar_id="1", job_id='2').run()
        self.assert_job_result("2", 100, "CSAR(1) is deleting now.")

    @mock.patch.object(restcall, 'call_req')
    def test_delete_pending_csar_when_not_deletion_pending(self, mock_call_req):
        NfPackageModel(uuid="01", nfpackageid="1").save()
        mock_call_req.return_value = [0, json.JSONEncoder().encode({
            "deletionPending": "false"}), "200"]
        NfPkgDeletePendingThread(csar_id="1", job_id='2').run()
        self.assert_job_result("2", 100, "CSAR(1) need not to be deleted.")

    @mock.patch.object(restcall, 'call_req')
    def test_delete_pending_csar_when_in_using(self, mock_call_req):
        mock_call_req.return_value = [0, json.JSONEncoder().encode({
            "processState": "normal"}), "200"]
        NfPackageModel(uuid="01", nfpackageid="1").save()
        NfInstModel(nfinstid="01", package_id="1").save()
        NfPkgDeletePendingThread(csar_id="1", job_id='2').run()
        self.assert_job_result("2", 100, "CSAR(1) is in using, cannot be deleted.")

    @mock.patch.object(VimAdaptor, '__init__')
    @mock.patch.object(VimAdaptor, 'delete_image')
    @mock.patch.object(restcall, 'call_req')
    def test_delete_csarr_when_exception(self, mock_call_req, mock_delete_image, mock_init_):
        mock_vals = {
            ("/api/catalog/v1/csars/1", "DELETE"):
                [1, "{}", "400"],
            ("/api/catalog/v1/csars/1?processState=deleting", "PUT"):
                [0, "{}", "200"],
            ("/api/catalog/v1/csars/1?processState=deleteFailed", "PUT"):
                [0, "{}", "200"],
            ("/api/catalog/v1/csars/1", "GET"):
                [0, json.JSONEncoder().encode({"processState": "normal"}), "200"],
            ("/cloud-infrastructure/cloud-regions?depth=all", "GET"):
                [0, json.JSONEncoder().encode(vims_info), "200"]}
        mock_delete_image.return_value = [0, "", '200']

        def side_effect(*args):
            return mock_vals[(args[4], args[5])]

        mock_call_req.side_effect = side_effect
        mock_init_.return_value = None
        VnfPackageFileModel(vnfpid="1", imageid="001", vimid="002").save()
        NfPackageModel(uuid="01", nfpackageid="1").save()
        NfPkgDeletePendingThread(csar_id="1", job_id='2').run()
        self.assert_job_result("2", 255, "Failed to delete CSAR(1) from catalog.")

    @mock.patch.object(VimAdaptor, '__init__')
    @mock.patch.object(VimAdaptor, 'delete_image')
    @mock.patch.object(restcall, 'call_req')
    def test_delete_csar_when_successfully(self, mock_call_req, mock_delete_image, mock_init_):
        mock_vals = {
            ("/api/catalog/v1/csars/1", "DELETE"):
                [0, json.JSONEncoder().encode({"successfully": "successfully"}), "200"],
            ("/api/catalog/v1/csars/1?processState=deleting", "PUT"):
                [0, json.JSONEncoder().encode({"successfully": "successfully"}), "200"],
            ("/api/catalog/v1/csars/1?processState=deleteFailed", "PUT"):
                [0, json.JSONEncoder().encode({"successfully": "successfully"}), "200"],
            ("/api/catalog/v1/csars/1", "GET"):
                [0, json.JSONEncoder().encode({"notProcessState": "notProcessState"}), "200"],
            ("/cloud-infrastructure/cloud-regions?depth=all", "GET"):
                [0, json.JSONEncoder().encode(vims_info), "200"]}
        mock_delete_image.return_value = [0, json.JSONEncoder().encode({"test": "test"}), '200']

        def side_effect(*args):
            return mock_vals[(args[4], args[5])]

        mock_call_req.side_effect = side_effect
        mock_init_.return_value = None
        VnfPackageFileModel(vnfpid="1", imageid="001", vimid="002").save()
        NfPackageModel(uuid="01", nfpackageid="1").save()
        NfPkgDeletePendingThread(csar_id="1", job_id='2').run()
        self.assert_job_result("2", 100, "Delete CSAR(1) successfully.")

    #########################################################################
    @mock.patch.object(restcall, 'call_req')
    def test_delete_nf_pkg_when_deleting(self, mock_call_req):
        mock_call_req.return_value = [0, json.JSONEncoder().encode({"processState": "deleting"}), '200']
        NfPkgDeleteThread(csar_id="1", job_id="2").run()
        self.assert_job_result("2", 100, "CSAR(1) is deleting now.")

    def test_get_nf_csars_normal(self):
        NfPackageModel(uuid="01", nfpackageid="1", vnfdid="2").save()
        resp = self.client.get("/api/nslcm/v0/vnfpackage")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(resp.data["csars"]))
        self.assertEqual("1", resp.data["csars"][0]["csarId"])
        self.assertEqual("2", resp.data["csars"][0]["vnfdId"])


vims_info = {
    "cloud-region": [
        {
            "cloud-owner": "example-cloud-owner-val-60268",
            "cloud-region-id": "example-cloud-region-id-val-77704",
            "cloud-type": "example-cloud-type-val-20689",
            "owner-defined-type": "example-owner-defined-type-val-24237",
            "cloud-region-version": "example-cloud-region-version-val-95948",
            "identity-url": "example-identity-url-val-98336",
            "cloud-zone": "example-cloud-zone-val-67202",
            "complex-name": "example-complex-name-val-86264",
            "sriov-automation": True,
            "cloud-extra-info": "example-cloud-extra-info-val-44735",
            "cloud-epa-caps": "example-cloud-epa-caps-val-67134",
            "resource-version": "example-resource-version-val-47608",
            "volume-groups": {
                "volume-group": [
                    {
                        "volume-group-id": "example-volume-group-id-val-79555",
                        "volume-group-name": "example-volume-group-name-val-21888",
                        "heat-stack-id": "example-heat-stack-id-val-56926",
                        "vnf-type": "example-vnf-type-val-47890",
                        "orchestration-status": "example-orchestration-status-val-34971",
                        "model-customization-id": "example-model-customization-id-val-7851",
                        "vf-module-model-customization-id": "example-vf-module-model-customization-id-val-35365",
                        "resource-version": "example-resource-version-val-66022"
                    }
                ]
            },
            "tenants": {
                "tenant": [
                    {
                        "tenant-id": "example-tenant-id-val-30151",
                        "tenant-name": "example-tenant-name-val-12231",
                        "tenant-context": "example-tenant-context-val-80991",
                        "resource-version": "example-resource-version-val-5033",
                        "vservers": {
                            "vserver": [
                                {
                                    "vserver-id": "example-vserver-id-val-70581",
                                    "vserver-name": "example-vserver-name-val-63390",
                                    "vserver-name2": "example-vserver-name2-val-70924",
                                    "prov-status": "example-prov-status-val-24088",
                                    "vserver-selflink": "example-vserver-selflink-val-17737",
                                    "in-maint": True,
                                    "is-closed-loop-disabled": True,
                                    "resource-version": "example-resource-version-val-46166",
                                    "volumes": {
                                        "volume": [
                                            {
                                                "volume-id": "example-volume-id-val-9740",
                                                "volume-selflink": "example-volume-selflink-val-8411",
                                                "resource-version": "example-resource-version-val-41965"
                                            }
                                        ]
                                    },
                                    "l-interfaces": {
                                        "l-interface": [
                                            {
                                                "interface-name": "example-interface-name-val-67663",
                                                "interface-role": "example-interface-role-val-27132",
                                                "v6-wan-link-ip": "example-v6-wan-link-ip-val-85445",
                                                "selflink": "example-selflink-val-83317",
                                                "interface-id": "example-interface-id-val-98716",
                                                "macaddr": "example-macaddr-val-18235",
                                                "network-name": "example-network-name-val-45040",
                                                "management-option": "example-management-option-val-65761",
                                                "interface-description": "example-interface-description-val-32615",
                                                "is-port-mirrored": True,
                                                "resource-version": "example-resource-version-val-10801",
                                                "in-maint": True,
                                                "prov-status": "example-prov-status-val-5726",
                                                "is-ip-unnumbered": True,
                                                "allowed-address-pairs": "example-allowed-address-pairs-val-52679",
                                                "vlans": {
                                                    "vlan": [
                                                        {
                                                            "vlan-interface": "example-vlan-interface-val-61591",
                                                            "vlan-id-inner": 53472228,
                                                            "vlan-id-outer": 93087267,
                                                            "resource-version": "example-resource-version-val-52900",
                                                            "speed-value": "example-speed-value-val-69335",
                                                            "speed-units": "example-speed-units-val-72089",
                                                            "vlan-description": "example-vlan-description-val-96604",
                                                            "backdoor-connection": "example-backdoor-connection-val-42299",
                                                            "vpn-key": "example-vpn-key-val-50517",
                                                            "orchestration-status": "example-orchestration-status-val-66570",
                                                            "in-maint": True,
                                                            "prov-status": "example-prov-status-val-46495",
                                                            "is-ip-unnumbered": True,
                                                            "l3-interface-ipv4-address-list": [
                                                                {
                                                                    "l3-interface-ipv4-address": "example-l3-interface-ipv4-address-val-32173",
                                                                    "l3-interface-ipv4-prefix-length": 29740951,
                                                                    "vlan-id-inner": 93873764,
                                                                    "vlan-id-outer": 82615508,
                                                                    "is-floating": True,
                                                                    "resource-version": "example-resource-version-val-75216",
                                                                    "neutron-network-id": "example-neutron-network-id-val-77878",
                                                                    "neutron-subnet-id": "example-neutron-subnet-id-val-79062"
                                                                }
                                                            ],
                                                            "l3-interface-ipv6-address-list": [
                                                                {
                                                                    "l3-interface-ipv6-address": "example-l3-interface-ipv6-address-val-88548",
                                                                    "l3-interface-ipv6-prefix-length": 89047373,
                                                                    "vlan-id-inner": 95671681,
                                                                    "vlan-id-outer": 88533796,
                                                                    "is-floating": True,
                                                                    "resource-version": "example-resource-version-val-40990",
                                                                    "neutron-network-id": "example-neutron-network-id-val-81951",
                                                                    "neutron-subnet-id": "example-neutron-subnet-id-val-4218"
                                                                }
                                                            ]
                                                        }
                                                    ]
                                                },
                                                "sriov-vfs": {
                                                    "sriov-vf": [
                                                        {
                                                            "pci-id": "example-pci-id-val-12933",
                                                            "vf-vlan-filter": "example-vf-vlan-filter-val-90275",
                                                            "vf-mac-filter": "example-vf-mac-filter-val-13509",
                                                            "vf-vlan-strip": True,
                                                            "vf-vlan-anti-spoof-check": True,
                                                            "vf-mac-anti-spoof-check": True,
                                                            "vf-mirrors": "example-vf-mirrors-val-59746",
                                                            "vf-broadcast-allow": True,
                                                            "vf-unknown-multicast-allow": True,
                                                            "vf-unknown-unicast-allow": True,
                                                            "vf-insert-stag": True,
                                                            "vf-link-status": "example-vf-link-status-val-37662",
                                                            "resource-version": "example-resource-version-val-86970",
                                                            "neutron-network-id": "example-neutron-network-id-val-71727"
                                                        }
                                                    ]
                                                },
                                                "l-interfaces": {
                                                    "l-interface": [
                                                        {
                                                            "interface-name": "example-interface-name-val-91632",
                                                            "interface-role": "example-interface-role-val-59119",
                                                            "v6-wan-link-ip": "example-v6-wan-link-ip-val-21039",
                                                            "selflink": "example-selflink-val-16277",
                                                            "interface-id": "example-interface-id-val-77457",
                                                            "macaddr": "example-macaddr-val-49026",
                                                            "network-name": "example-network-name-val-3483",
                                                            "management-option": "example-management-option-val-16429",
                                                            "interface-description": "example-interface-description-val-50889",
                                                            "is-port-mirrored": True,
                                                            "resource-version": "example-resource-version-val-30308",
                                                            "in-maint": True,
                                                            "prov-status": "example-prov-status-val-69406",
                                                            "is-ip-unnumbered": True,
                                                            "allowed-address-pairs": "example-allowed-address-pairs-val-49123"
                                                        }
                                                    ]
                                                },
                                                "l3-interface-ipv4-address-list": [
                                                    {
                                                        "l3-interface-ipv4-address": "example-l3-interface-ipv4-address-val-63922",
                                                        "l3-interface-ipv4-prefix-length": 13823411,
                                                        "vlan-id-inner": 14316230,
                                                        "vlan-id-outer": 66559625,
                                                        "is-floating": True,
                                                        "resource-version": "example-resource-version-val-30766",
                                                        "neutron-network-id": "example-neutron-network-id-val-46636",
                                                        "neutron-subnet-id": "example-neutron-subnet-id-val-96658"
                                                    }
                                                ],
                                                "l3-interface-ipv6-address-list": [
                                                    {
                                                        "l3-interface-ipv6-address": "example-l3-interface-ipv6-address-val-21246",
                                                        "l3-interface-ipv6-prefix-length": 20226253,
                                                        "vlan-id-inner": 68200128,
                                                        "vlan-id-outer": 18442586,
                                                        "is-floating": True,
                                                        "resource-version": "example-resource-version-val-24602",
                                                        "neutron-network-id": "example-neutron-network-id-val-49811",
                                                        "neutron-subnet-id": "example-neutron-subnet-id-val-67505"
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
                        "flavor-id": "example-flavor-id-val-15058",
                        "flavor-name": "example-flavor-name-val-69485",
                        "flavor-vcpus": 92601,
                        "flavor-ram": 31468,
                        "flavor-disk": 58744,
                        "flavor-ephemeral": 84771,
                        "flavor-swap": "example-flavor-swap-val-66481",
                        "flavor-is-public": True,
                        "flavor-selflink": "example-flavor-selflink-val-48912",
                        "flavor-disabled": True,
                        "resource-version": "example-resource-version-val-55131"
                    }
                ]
            },
            "group-assignments": {
                "group-assignment": [
                    {
                        "group-id": "example-group-id-val-79234",
                        "group-type": "example-group-type-val-29164",
                        "group-name": "example-group-name-val-57605",
                        "group-description": "example-group-description-val-52975",
                        "resource-version": "example-resource-version-val-10280"
                    }
                ]
            },
            "snapshots": {
                "snapshot": [
                    {
                        "snapshot-id": "example-snapshot-id-val-60630",
                        "snapshot-name": "example-snapshot-name-val-90351",
                        "snapshot-architecture": "example-snapshot-architecture-val-3225",
                        "snapshot-os-distro": "example-snapshot-os-distro-val-31399",
                        "snapshot-os-version": "example-snapshot-os-version-val-16981",
                        "application": "example-application-val-34584",
                        "application-vendor": "example-application-vendor-val-97854",
                        "application-version": "example-application-version-val-20705",
                        "snapshot-selflink": "example-snapshot-selflink-val-84731",
                        "prev-snapshot-id": "example-prev-snapshot-id-val-77339",
                        "resource-version": "example-resource-version-val-19220"
                    }
                ]
            },
            "images": {
                "image": [
                    {
                        "image-id": "example-image-id-val-34721",
                        "image-name": "example-image-name-val-64106",
                        "image-architecture": "example-image-architecture-val-8247",
                        "image-os-distro": "example-image-os-distro-val-98534",
                        "image-os-version": "example-image-os-version-val-87444",
                        "application": "example-application-val-30758",
                        "application-vendor": "example-application-vendor-val-7048",
                        "application-version": "example-application-version-val-79678",
                        "image-selflink": "example-image-selflink-val-72836",
                        "resource-version": "example-resource-version-val-79432",
                        "metadata": {
                            "metadatum": [
                                {
                                    "metaname": "example-metaname-val-75188",
                                    "metaval": "example-metaval-val-64947",
                                    "resource-version": "example-resource-version-val-59427"
                                }
                            ]
                        }
                    }
                ]
            },
            "dvs-switches": {
                "dvs-switch": [
                    {
                        "switch-name": "example-switch-name-val-21335",
                        "vcenter-url": "example-vcenter-url-val-74348",
                        "resource-version": "example-resource-version-val-51253"
                    }
                ]
            },
            "oam-networks": {
                "oam-network": [
                    {
                        "network-uuid": "example-network-uuid-val-65686",
                        "network-name": "example-network-name-val-94383",
                        "cvlan-tag": 31041170,
                        "ipv4-oam-gateway-address": "example-ipv4-oam-gateway-address-val-15815",
                        "ipv4-oam-gateway-address-prefix-length": 65477,
                        "resource-version": "example-resource-version-val-21712"
                    }
                ]
            },
            "availability-zones": {
                "availability-zone": [
                    {
                        "availability-zone-name": "example-availability-zone-name-val-14569",
                        "hypervisor-type": "example-hypervisor-type-val-70481",
                        "operational-status": "example-operational-status-val-13589",
                        "resource-version": "example-resource-version-val-78031"
                    }
                ]
            },
            "esr-system-info-list": {
                "esr-system-info": [
                    {
                        "esr-system-info-id": "example-esr-system-info-id-val-58799",
                        "system-name": "example-system-name-val-78629",
                        "type": "example-type-val-4146",
                        "vendor": "example-vendor-val-11916",
                        "version": "example-version-val-60284",
                        "service-url": "example-service-url-val-85858",
                        "user-name": "example-user-name-val-23297",
                        "password": "example-password-val-33729",
                        "system-type": "example-system-type-val-54309",
                        "protocal": "example-protocal-val-86585",
                        "ssl-cacert": "example-ssl-cacert-val-95811",
                        "ssl-insecure": True,
                        "ip-address": "example-ip-address-val-62987",
                        "port": "example-port-val-83650",
                        "cloud-domain": "example-cloud-domain-val-9841",
                        "default-tenant": "example-default-tenant-val-52776",
                        "resource-version": "example-resource-version-val-61961"
                    }
                ]
            }
        }
    ]
}
