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

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from lcm.ns.vls.create_vls import CreateVls
from lcm.ns.vls.delete_vls import DeleteVls
from lcm.ns.vls.get_vls import GetVls

import logging

logger = logging.getLogger(__name__)


class VlView(APIView):
    def post(self, request):
        logger.debug("VlsCreateView--post::> %s" % request.data)
        resp = CreateVls(request.data).do()
        return Response(data=resp, status=status.HTTP_201_CREATED)


class VlDetailView(APIView):
    def get(self, request, vl_inst_id):
        logger.debug("VlDetailView--get::> %s" % vl_inst_id)
        vl_inst_info = GetVls(vl_inst_id).do()
        if not vl_inst_info:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_200_OK, data={'vlId': vl_inst_id,
                                                         'vlName': vl_inst_info[0].vlinstancename,
                                                         'vlStatus': "active"})

    def delete(self, request_paras, vl_inst_id):
        logger.debug("VlDetailView--delete::> %s" % vl_inst_id)
        resp = DeleteVls(vl_inst_id).do()
        return Response(data=resp, status=status.HTTP_202_ACCEPTED)
