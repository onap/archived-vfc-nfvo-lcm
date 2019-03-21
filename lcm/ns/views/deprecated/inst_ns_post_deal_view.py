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
import traceback

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from lcm.ns.serializers.deprecated.ns_serializers import _InstNsPostDealReqSerializer
from lcm.pub.database.models import NSInstModel, ServiceBaseInfoModel
from lcm.pub.exceptions import NSLCMException
from lcm.pub.utils.restcall import req_by_msb
from lcm.pub.utils.values import ignore_case_get

logger = logging.getLogger(__name__)


class NSInstPostDealView(APIView):
    @swagger_auto_schema(
        request_body=_InstNsPostDealReqSerializer(help_text="NS instant post deal"),
        responses={
            status.HTTP_202_ACCEPTED: "NS instant post deal success",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Inner error"
        }
    )
    def post(self, request, ns_instance_id):
        logger.debug("Enter NSInstPostDealView::post %s, %s", request.data, ns_instance_id)
        ns_post_status = ignore_case_get(request.data, 'status')
        ns_status = 'ACTIVE' if ns_post_status == 'true' else 'FAILED'
        ns_opr_status = 'success' if ns_post_status == 'true' else 'failed'
        try:
            req_serializer = _InstNsPostDealReqSerializer(data=request.data)
            if not req_serializer.is_valid():
                raise NSLCMException(req_serializer.errors)
            NSInstModel.objects.filter(id=ns_instance_id).update(status=ns_status)
            ServiceBaseInfoModel.objects.filter(service_id=ns_instance_id).update(
                active_status=ns_status, status=ns_opr_status)
            nsd_info = NSInstModel.objects.filter(id=ns_instance_id)
            nsd_id = nsd_info[0].nsd_id
            nsd_model = json.loads(nsd_info[0].nsd_model)
            if "policies" in nsd_model and nsd_model["policies"]:
                policy = nsd_model["policies"][0]
                if "properties" in policy and policy["properties"]:
                    file_url = ignore_case_get(policy["properties"][0], "drl_file_url")
                else:
                    file_url = ""
                self.send_policy_request(ns_instance_id, nsd_id, file_url)
        except:
            logger.error(traceback.format_exc())
            return Response(data={'error': 'Failed to update status of NS(%s)' % ns_instance_id},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        logger.debug("*****NS INST %s, %s******", ns_status, ns_opr_status)
        return Response(data={'success': 'Update status of NS(%s) to %s' % (ns_instance_id, ns_status)},
                        status=status.HTTP_202_ACCEPTED)

    def send_policy_request(self, ns_instance_id, nsd_id, file_url):
        input_data = {
            "nsid": ns_instance_id,
            "nsdid": nsd_id,
            "fileUri": file_url
        }
        req_param = json.JSONEncoder().encode(input_data)
        policy_engine_url = 'api/polengine/v1/policyinfo'
        ret = req_by_msb(policy_engine_url, "POST", req_param)
        if ret[0] != 0:
            logger.error("Failed to send ns policy req")
