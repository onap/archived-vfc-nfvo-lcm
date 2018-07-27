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

import uuid
import os
import mock
from django.test import Client
from django.test import TestCase
from rest_framework import status
from lcm.ns.const import NS_INST_STATUS
from lcm.ns.ns_manual_scale import NSManualScaleService
from lcm.pub.database.models import NSInstModel, JobModel, NfInstModel
from lcm.pub.exceptions import NSLCMException
from lcm.pub.utils import restcall
from lcm.pub.utils.jobutil import JobUtil, JOB_TYPE, JOB_MODEL_STATUS
from lcm.pub.msapi import catalog
from lcm.pub.utils.scaleaspect import get_json_data


SCALING_JSON = {
    "scale_options": [
        {
            "nsd_id": "ns_ims",
            "ns_scale_aspect": "TIC_CORE_IMS",
            "ns_scale_info": [
                {
                    "step": "1",
                    "scale_list": [
                        {
                            "vnfd_id": "zte_ims_cscf",
                            "vnf_scale_aspect": "mpu",
                            "numberOfSteps": "1"
                        },
                        {
                            "vnfd_id": "zte_ims_hss",
                            "vnf_scale_aspect": "fpu",
                            "numberOfSteps": "3"
                        }
                    ]
                },
                {
                    "step": "2",
                    "scale_list": [
                        {
                            "vnfd_id": "zte_ims_cscf",
                            "vnf_scale_aspect": "mpu",
                            "numberOfSteps": "2"
                        },
                        {
                            "vnfd_id": "zte_ims_hss",
                            "vnf_scale_aspect": "fpu",
                            "numberOfSteps": "6"
                        }
                    ]
                }
            ]
        },
        {
            "nsd_id": "ns_epc",
            "ns_scale_aspect": "TIC_EDGE_EPC",
            "ns_scale_info": [
                {
                    "step": "1",
                    "scale_list": [
                        {
                            "vnfd_id": "zte_epc_spgw",
                            "vnf_scale_aspect": "gpu",
                            "numberOfSteps": "1"
                        },
                        {
                            "vnfd_id": "zte_epc_tas",
                            "vnf_scale_aspect": "fpu",
                            "numberOfSteps": "2"
                        }
                    ]
                },
                {
                    "step": "2",
                    "scale_list": [
                        {
                            "vnfd_id": "zte_epc_spgw",
                            "vnf_scale_aspect": "mpu",
                            "numberOfSteps": "2"
                        },
                        {
                            "vnfd_id": "zte_epc_tas",
                            "vnf_scale_aspect": "fpu",
                            "numberOfSteps": "4"
                        }
                    ]
                }
            ]
        }
    ]
}


class TestNsManualScale(TestCase):
    def setUp(self):
        self.ns_inst_id = str(uuid.uuid4())
        self.job_id = JobUtil.create_job(
            "NS", JOB_TYPE.MANUAL_SCALE_VNF, self.ns_inst_id)
        self.package_id = "7"
        self.client = Client()
        NSInstModel(
            id=self.ns_inst_id,
            name="abc",
            nspackage_id=self.package_id,
            nsd_id="111").save()

        self.init_scaling_map_json()

    def tearDown(self):
        NSInstModel.objects.filter().delete()
        JobModel.objects.filter().delete()

    def init_scaling_map_json(self):
        curdir_path = os.path.dirname(
            os.path.dirname(
                os.path.dirname(
                    os.path.abspath(__file__))))
        filename = curdir_path + "/ns/data/scalemapping.json"
        self.scaling_map_json = get_json_data(filename)

    def insert_new_ns(self):
        ns_inst_id = str(uuid.uuid4())
        job_id = JobUtil.create_job(
            "NS", JOB_TYPE.MANUAL_SCALE_VNF, self.ns_inst_id)
        package_id = "23"
        NSInstModel(
            id=ns_inst_id,
            name="abc",
            nspackage_id=package_id,
            nsd_id=package_id).save()
        return ns_inst_id, job_id

    def insert_new_nf(self):
        # Create a third vnf instance
        self.nf_name = "name_1"
        self.vnf_id = "1"
        self.vnfm_inst_id = "1"
        nf_inst_id = "233"
        package_id = "nf_zte_hss"
        nf_uuid = "ab34-3g5j-de13-ab85-ij93"

        NfInstModel.objects.create(
            nfinstid=nf_inst_id,
            nf_name=self.nf_name,
            vnf_id=self.vnf_id,
            vnfm_inst_id=self.vnfm_inst_id,
            ns_inst_id=self.ns_inst_id,
            max_cpu='14',
            max_ram='12296',
            max_hd='101',
            max_shd="20",
            max_net=10,
            status='active',
            mnfinstid=nf_uuid,
            package_id=package_id,
            vnfd_model='{"metadata": {"vnfdId": "1","vnfdName": "PGW001",'
                       '"vnfProvider": "zte","vnfdVersion": "V00001","vnfVersion": "V5.10.20",'
                       '"productType": "CN","vnfType": "PGW",'
                       '"description": "PGW VNFD description",'
                       '"isShared":true,"vnfExtendType":"driver"}}')

    @mock.patch.object(NSManualScaleService, 'run')
    def test_ns_manual_scale(self, mock_run):
        data = {
            "scaleType": "SCALE_NS",
            "scaleNsData": [{
                "scaleNsByStepsData": [{
                    "aspectId": "1",
                    "numberOfSteps": 1,
                    "scalingDirection": "0"
                }]
            }]
        }
        response = self.client.post(
            "/api/nslcm/v1/ns/%s/scale" %
            self.ns_inst_id, data=data)
        self.failUnlessEqual(status.HTTP_202_ACCEPTED, response.status_code)

    def test_ns_manual_scale_error_scaletype(self):
        data = {
            "scaleType": "SCALE_ERR",
            "scaleNsData": [{
                "scaleNsByStepsData": [{
                    "aspectId": "sss_zte",
                    "numberOfSteps": 1,
                    "scalingDirection": "0"
                }]
            }]
        }
        NSManualScaleService(self.ns_inst_id, data, self.job_id).run()
        jobs = JobModel.objects.filter(jobid=self.job_id)
        self.assertEqual(255, jobs[0].progress)

    def test_ns_manual_scale_error_nsd_id(self):
        data = {
            "scaleType": "SCALE_NS",
            "scaleNsData": [{
                "scaleNsByStepsData": [{
                    "aspectId": "sss_zte",
                    "numberOfSteps": 1,
                    "scalingDirection": "0"
                }]
            }]
        }
        NSManualScaleService(self.ns_inst_id, data, self.job_id).run()
        jobs = JobModel.objects.filter(jobid=self.job_id)
        self.assertEqual(255, jobs[0].progress)

    def test_ns_manual_scale_error_aspect(self):
        data = {
            "scaleType": "SCALE_NS",
            "scaleNsData": [{
                "scaleNsByStepsData": [{
                    "aspectId": "sss_zte",
                    "numberOfSteps": 1,
                    "scalingDirection": "0"
                }]
            }]
        }
        ns_inst_id, job_id = self.insert_new_ns()
        job_id = JobUtil.create_job(
            "NS", JOB_TYPE.MANUAL_SCALE_VNF, ns_inst_id)
        NSManualScaleService(ns_inst_id, data, job_id).run()
        jobs = JobModel.objects.filter(jobid=job_id)
        self.assertEqual(255, jobs[0].progress)

    @mock.patch.object(catalog, 'get_scalingmap_json_package')
    @mock.patch.object(NSManualScaleService, 'do_vnfs_scale')
    def test_ns_manual_scale_success(self, mock_do_vnfs_scale, mock_get_scalingmap_json_package):
        data = {
            "scaleType": "SCALE_NS",
            "scaleNsData": [{
                "scaleNsByStepsData": [{
                    "aspectId": "TIC_EDGE_IMS",
                    "numberOfSteps": "1",
                    "scalingDirection": "0"
                }]
            }]
        }
        mock_get_scalingmap_json_package.return_value = self.scaling_map_json
        mock_do_vnfs_scale.return_value = JOB_MODEL_STATUS.FINISHED
        ns_inst_id, job_id = self.insert_new_ns()
        job_id = JobUtil.create_job(
            "NS", JOB_TYPE.MANUAL_SCALE_VNF, ns_inst_id)
        self.insert_new_nf()
        NSManualScaleService(ns_inst_id, data, job_id).run()
        jobs = JobModel.objects.filter(jobid=job_id)
        self.assertEqual(255, jobs[0].progress)

    @mock.patch.object(restcall, 'call_req')
    def test_ns_manual_scale_thread(self, mock_call):
        data = {
            "scaleType": "SCALE_NS",
            "scaleNsData": [{
                "scaleNsByStepsData": [{
                    "aspectId": "1",
                    "numberOfSteps": 1,
                    "scalingDirection": "0"
                }]
            }]
        }
        NSManualScaleService(self.ns_inst_id, data, self.job_id).run()
        self.assertTrue(
            NSInstModel.objects.get(
                id=self.ns_inst_id).status,
            NS_INST_STATUS.ACTIVE)

    # def test_swagger_ok(self):
    # resp = self.client.get("/api/nslcm/v1/swagger.json", format='json')
    # self.assertEqual(resp.status_code, status.HTTP_200_OK)

    @mock.patch.object(NSManualScaleService, 'start')
    def test_ns_manual_scale_empty_data(self, mock_start):
        mock_start.side_effect = NSLCMException("NS scale failed.")
        response = self.client.post(
            "/api/nslcm/v1/ns/%s/scale" %
            self.ns_inst_id, data={})
        self.assertEqual(
            response.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", response.data)

    @mock.patch.object(NSManualScaleService, 'start')
    def test_ns_manual_scale_when_ns_not_exist(self, mock_start):
        mock_start.side_effect = NSLCMException("NS scale failed.")
        data = {
            "scaleType": "SCALE_NS",
            "scaleNsData": [{
                "scaleNsByStepsData": [{
                    "aspectId": "1",
                    "numberOfSteps": 1,
                    "scalingDirection": "0"
                }]
            }]
        }
        response = self.client.post("/api/nslcm/v1/ns/11/scale", data=data)
        self.assertEqual(
            response.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", response.data)
