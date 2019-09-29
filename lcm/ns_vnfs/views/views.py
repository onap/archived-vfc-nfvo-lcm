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
import logging
import traceback
import uuid

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from lcm.pub.exceptions import NSLCMException
from lcm.pub.msapi.extsys import get_vnfm_by_id, get_vim_by_id_vim_info
from lcm.pub.utils.jobutil import JobUtil
from lcm.jobs.enum import JOB_TYPE, JOB_ACTION
from lcm.pub.utils.values import ignore_case_get
from lcm.ns_vnfs.biz.create_vnfs import CreateVnfs
from lcm.ns_vnfs.biz.get_vnfs import GetVnf, GetVnfVms
from lcm.ns_vnfs.serializers.serializers import GetVnfRespSerializer
from lcm.ns_vnfs.serializers.serializers import GrantVnfReqSerializer
from lcm.ns_vnfs.serializers.serializers import GrantVnfRespSerializer
from lcm.ns_vnfs.biz.grant_vnfs import GrantVnfs
from lcm.ns_vnfs.serializers.serializers import InstVnfReqSerializer
from lcm.ns_vnfs.serializers.serializers import InstVnfRespSerializer
from lcm.ns_vnfs.biz.scale_vnfs import NFManualScaleService
from lcm.ns_vnfs.biz.notify_lcm import NotifyLcm
from lcm.ns_vnfs.serializers.serializers import NotifyLcmReqSerializer
from lcm.ns_vnfs.serializers.serializers import PlaceVnfReqSerializer
from lcm.ns_vnfs.biz.place_vnfs import PlaceVnfs
from lcm.ns_vnfs.serializers.serializers import ScaleVnfReqSerializer
from lcm.ns_vnfs.serializers.serializers import ScaleVnfRespSerializer
from lcm.ns_vnfs.serializers.serializers import TerminateVnfReqSerializer
from lcm.ns_vnfs.serializers.serializers import TerminateVnfRespSerializer
from lcm.ns_vnfs.biz.terminate_nfs import TerminateVnfs
from lcm.ns_vnfs.serializers.serializers import VerifyVnfReqSerializer
from lcm.ns_vnfs.serializers.serializers import VerifyVnfRespSerializer
from lcm.ns_vnfs.biz.verify_vnfs import VerifyVnfs
from lcm.ns_vnfs.serializers.serializers import VimInfoRespSerializer
from lcm.ns_vnfs.serializers.serializers import VnfmInfoRespSerializer
from lcm.ns_vnfs.biz import create_vnfs
from lcm.pub.exceptions import BadRequestException

logger = logging.getLogger(__name__)


def view_safe_call_with_log(logger):
    def view_safe_call(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except BadRequestException as e:
                logger.error(e.args[0])
                return make_error_resp(
                    detail=e.args[0],
                    status=status.HTTP_400_BAD_REQUEST
                )
            except NSLCMException as e:
                logger.error(e.args[0])
                return make_error_resp(
                    detail=e.args[0],
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            except Exception as e:
                logger.error(e.args[0])
                logger.error(traceback.format_exc())
                return make_error_resp(
                    detail='Unexpected exception',
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return wrapper
    return view_safe_call


def make_error_resp(status, detail):
    return Response(
        data={
            'error': detail
        },
        status=status
    )


class NfView(APIView):
    @swagger_auto_schema(
        request_body=InstVnfReqSerializer(),
        responses={
            status.HTTP_202_ACCEPTED: InstVnfRespSerializer()
        }
    )
    def post(self, request):
        logger.debug("VnfCreateView--post::> %s" % request.data)

        req_serializer = InstVnfReqSerializer(data=request.data)
        if not req_serializer.is_valid():
            logger.error(req_serializer.errors)

        data = {'ns_instance_id': ignore_case_get(request.data, 'nsInstanceId'),
                'additional_param_for_vnf': ignore_case_get(request.data, 'additionalParamForVnf'),
                'vnf_index': ignore_case_get(request.data, 'vnfIndex')}
        nf_inst_id, job_id = create_vnfs.prepare_create_params()
        CreateVnfs(data, nf_inst_id, job_id).start()
        rsp = {
            "vnfInstId": nf_inst_id,
            "jobId": job_id}

        resp_serializer = InstVnfRespSerializer(data=rsp)
        if not resp_serializer.is_valid():
            logger.error(resp_serializer.errors)

        return Response(data=rsp, status=status.HTTP_202_ACCEPTED)


class NfDetailView(APIView):
    @swagger_auto_schema(
        request_body=None,
        responses={
            status.HTTP_200_OK: GetVnfRespSerializer(),
            status.HTTP_404_NOT_FOUND: "VNF not found"
        }
    )
    def get(self, request, vnfinstid):
        logger.debug("VnfQueryView--get::> %s" % vnfinstid)
        nf_inst_info = GetVnf(vnfinstid).do_biz()
        if not nf_inst_info:
            return Response(status=status.HTTP_404_NOT_FOUND)

        vnf_vms = GetVnfVms(vnfinstid).do_biz()

        rsp = {
            'vnfInstId': nf_inst_info[0].nfinstid,
            'vnfName': nf_inst_info[0].nf_name,
            'vnfStatus': nf_inst_info[0].status,
            'vnfVms': [{
                'vmId': vm.vmid,
                'vmName': vm.vmname
            } for vm in vnf_vms]
        }
        resp_serializer = GetVnfRespSerializer(data=rsp)
        if not resp_serializer.is_valid():
            logger.error(resp_serializer.errors)

        return Response(status=status.HTTP_200_OK, data=rsp)


class NfTerminate(APIView):
    @swagger_auto_schema(
        request_body=TerminateVnfReqSerializer(),
        responses={
            status.HTTP_202_ACCEPTED: TerminateVnfRespSerializer(),
            status.HTTP_409_CONFLICT: "Inner error"
        }
    )
    def post(self, request, vnfinstid):
        logger.debug("NfTerminate--post::> %s, %s", vnfinstid, request.data)

        req_serializer = TerminateVnfReqSerializer(data=request.data)
        if not req_serializer.is_valid():
            logger.error(req_serializer.errors)

        vnf_inst_id = vnfinstid
        terminationType = ignore_case_get(request.data, 'terminationType')
        gracefulTerminationTimeout = ignore_case_get(request.data, 'gracefulTerminationTimeout')
        job_id = JobUtil.create_job(JOB_TYPE.VNF, JOB_ACTION.TERMINATE, vnf_inst_id)
        data = {'terminationType': terminationType, 'gracefulTerminationTimeout': gracefulTerminationTimeout}
        logger.debug("data=%s", data)
        try:
            TerminateVnfs(data, vnf_inst_id, job_id).start()
        except Exception as e:
            logger.error(e.args[0])
            return Response(data={'error': '%s' % e.args[0]}, status=status.HTTP_409_CONFLICT)
        rsp = {'jobId': job_id}

        resp_serializer = TerminateVnfRespSerializer(data=rsp)
        if not resp_serializer.is_valid():
            logger.error(resp_serializer.errors)

        return Response(data=rsp, status=status.HTTP_202_ACCEPTED)


class NfGrant(APIView):
    @swagger_auto_schema(
        request_body=GrantVnfReqSerializer(),
        responses={
            status.HTTP_201_CREATED: GrantVnfRespSerializer(),
            status.HTTP_409_CONFLICT: "Inner error"
        }
    )
    def post(self, request):
        logger.debug("NfGrant--post::> %s" % request.data)
        try:
            req_serializer = GrantVnfReqSerializer(data=request.data)
            if not req_serializer.is_valid():
                raise Exception(req_serializer.errors)

            vnf_inst_id = ignore_case_get(request.data, 'vnfInstanceId')
            job_id = JobUtil.create_job(JOB_TYPE.VNF, JOB_ACTION.GRANT, vnf_inst_id)
            rsp = GrantVnfs(request.data, job_id).send_grant_vnf_to_resMgr()
            """
            rsp = {
                "vim": {
                    "vimid": ignore_case_get(ignore_case_get(request.data, 'additionalparam'), 'vimid'),
                    "accessinfo": {
                        "tenant": "admin"
                    }
                }
            }
            """
            # resp_serializer = GrantVnfRespSerializer(data=rsp)
            # if not resp_serializer.is_valid():
            # raise Exception(resp_serializer.errors)

            return Response(data=rsp, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(e.args[0])
            logger.error(traceback.format_exc())
            return Response(data={'error': '%s' % e.args[0]}, status=status.HTTP_409_CONFLICT)


class NfPlacement(APIView):
    @swagger_auto_schema(
        request_body=PlaceVnfReqSerializer(),
        response={
            status.HTTP_201_CREATED: PlaceVnfReqSerializer(),
            status.HTTP_404_NOT_FOUND: "Placement not found"
        }
    )
    def post(self, request):
        logger.debug("NfPlacement--post::> %s" % request.data)
        try:
            req_serializer = PlaceVnfReqSerializer(data=request.data)
            if not req_serializer.is_valid():
                raise Exception(req_serializer.errors)
            PlaceVnfs(request.data).extract()
            return Response(data={}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e.args[0])
            logger.error(traceback.format_exc())
            return Response(data={'error': '%s' % e.args[0]}, status=status.HTTP_409_CONFLICT)


class LcmNotify(APIView):
    @swagger_auto_schema(
        request_body=NotifyLcmReqSerializer(),
        responses={
            status.HTTP_201_CREATED: 'successful',
            status.HTTP_409_CONFLICT: "Inner error"
        }
    )
    def post(self, request, vnfmid, vnfInstanceId):
        logger.debug("LcmNotify--post::> %s" % request.data)
        try:
            req_serializer = NotifyLcmReqSerializer(data=request.data)
            if not req_serializer.is_valid():
                raise Exception(req_serializer.errors)

            NotifyLcm(vnfmid, vnfInstanceId, request.data).do_biz()
            return Response(data={}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(e.ars[0])
            return Response(data={'error': '%s' % e.args[0]}, status=status.HTTP_409_CONFLICT)


class NfScaleView(APIView):
    @swagger_auto_schema(
        request_body=ScaleVnfReqSerializer(),
        responses={
            status.HTTP_202_ACCEPTED: ScaleVnfRespSerializer(),
            status.HTTP_409_CONFLICT: "Inner error"
        }
    )
    @view_safe_call_with_log(logger)
    def post(self, request, vnfinstid):
        logger.debug("NfScaleView--post::> %s" % request.data)
        try:
            req_serializer = ScaleVnfReqSerializer(data=request.data)
            if not req_serializer.is_valid():
                raise BadRequestException(req_serializer.errors)
            NFManualScaleService(vnfinstid, request.data).start()
            return Response(data={}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            logger.error(e.args[0])
            return Response(data={'error': '%s' % e.args[0]}, status=status.HTTP_409_CONFLICT)


class NfVerifyView(APIView):
    @swagger_auto_schema(
        request_body=VerifyVnfReqSerializer(),
        responses={
            status.HTTP_202_ACCEPTED: VerifyVnfRespSerializer(),
            status.HTTP_409_CONFLICT: "Inner error"
        }
    )
    @view_safe_call_with_log(logger)
    def post(self, request):
        job_id = "VNFSDK_" + str(uuid.uuid4())
        logger.debug("NfVerifyView--post::%s> %s", job_id, request.data)
        try:
            req_serializer = VerifyVnfReqSerializer(data=request.data)
            if not req_serializer.is_valid():
                raise BadRequestException(req_serializer.errors)

            VerifyVnfs(request.data, job_id).start()

            rsp = {"jobId": job_id}
            resp_serializer = VerifyVnfRespSerializer(data=rsp)
            if not resp_serializer.is_valid():
                raise Exception(resp_serializer.errors)

            return Response(data=rsp, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            logger.error(e.args[0])
            return Response(data={'error': '%s' % e.args[0]}, status=status.HTTP_409_CONFLICT)


class NfVnfmInfoView(APIView):
    @swagger_auto_schema(
        request_body=None,
        responses={
            status.HTTP_200_OK: VnfmInfoRespSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Inner error"
        }
    )
    def get(self, request, vnfmid):
        logger.debug("NfVnfmInfoView--get::> %s" % vnfmid)
        try:
            vnfm_info = get_vnfm_by_id(vnfmid)

            resp_serializer = VnfmInfoRespSerializer(data=vnfm_info)
            if not resp_serializer.is_valid():
                raise Exception(resp_serializer.errors)

        except NSLCMException as e:
            logger.error(e.args[0])
            return Response(data={'error': '%s' % e.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(e.args[0])
            logger.error(traceback.format_exc())
            return Response(data={'error': 'Failed to get vnfm info.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(data=vnfm_info, status=status.HTTP_200_OK)


class NfVimInfoView(APIView):
    @swagger_auto_schema(
        request_body=None,
        responses={
            status.HTTP_200_OK: VimInfoRespSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Inner error"
        }
    )
    # def get(self, request, vimid):
    def get(self, request, cloudowner, cloudregionid):
        logger.debug("NfVimInfoView--get::> %s,%s" % (cloudowner, cloudregionid))
        try:
            # vim_info = get_vim_by_id(vimid)
            vim_info = get_vim_by_id_vim_info(cloudowner, cloudregionid)

            resp_serializer = VimInfoRespSerializer(data=vim_info)
            if not resp_serializer.is_valid():
                raise Exception(resp_serializer.errors)

        except NSLCMException as e:
            logger.error(e.args[0])
            return Response(data={'error': '%s' % e.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(e.args[0])
            logger.error(traceback.format_exc())
            return Response(data={'error': 'Failed to get vim info.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(data=vim_info, status=status.HTTP_200_OK)
