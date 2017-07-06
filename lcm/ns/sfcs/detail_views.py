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

from lcm.ns.sfcs.delete_sfcs import DeleteSfcs
from lcm.ns.sfcs.get_sfcs import GetSfcs


class SfcDetailView(APIView):
    def get(self, request, sfc_inst_id):
        print "SfcCreateView--get::> %s" % sfc_inst_id
        sfc_inst_info = GetSfcs(sfc_inst_id).do()
        if not sfc_inst_info:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_200_OK, data={'sfcInstId': sfc_inst_id,
                                                         'sfcName': "xxx",
                                                         'sfcStatus': sfc_inst_info[0].status})

    def delete(self, request_paras, sfc_inst_id):
        resp = DeleteSfcs(sfc_inst_id).do()
        return Response(data=resp, status=status.HTTP_202_ACCEPTED)


class SfcCreateView(APIView):
    def post(self, request):
        print "SfcCreateView--post::> %s" % request.stream.body
        return Response(data={"jobId": "1234", "sfcInstId": "1"}, status=status.HTTP_201_CREATED)
