# Copyright 2018 ZTE Corporation.
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

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from lcm.ns_vnfs.biz.grant_vnf import GrantVnf
from lcm.ns_vnfs.serializers.grant_vnf_serializer import GrantRequestSerializer
from lcm.ns_vnfs.serializers.grant_vnf_serializer import GrantSerializer
from lcm.ns_vnfs.biz.handle_notification import HandleVnfLcmOocNotification, HandleVnfIdentifierCreationNotification, HandleVnfIdentifierDeletionNotification
from lcm.ns_vnfs.serializers.grant_vnf_serializer import VnfLcmOperationOccurrenceNotificationSerializer, VnfIdentifierCreationNotificationSerializer, VnfIdentifierDeletionNotificationSerializer

logger = logging.getLogger(__name__)


class VnfGrantView(APIView):
    @swagger_auto_schema(
        request_body=GrantRequestSerializer(),
        responses={
            status.HTTP_201_CREATED: GrantSerializer(
                help_text="The grant was created successfully (synchronous mode)."
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Inner error"
        }
    )
    def post(self, request):
        logger.debug("VnfGrantView Post: %s" % request.data)
        try:
            grant_request = GrantRequestSerializer(data=request.data)
            if not grant_request.is_valid():
                raise Exception(grant_request.errors)

            grant_resp = GrantVnf(request.data).exec_grant()

            resp_serializer = GrantSerializer(data=grant_resp)
            if not resp_serializer.is_valid():
                raise Exception(grant_resp)

            return Response(data=grant_resp, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(traceback.format_exc())
            logger.error("Exception in VnfGrant: %s", e.args[0])
            return Response(data={'error': e.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VnfNotifyView(APIView):
    @swagger_auto_schema(
        request_body=VnfLcmOperationOccurrenceNotificationSerializer(
            help_text="A notification about lifecycle changes triggered by a VNF LCM operation occurrence."
        ),
        responses={
            status.HTTP_204_NO_CONTENT: "The notification was delivered successfully.",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Inner error"
        }
    )
    def post(self, request, vnfmId, vnfInstanceId):
        logger.debug("VnfNotifyView post: %s" % request.data)
        logger.debug("vnfmId: %s vnfInstanceId: %s", vnfmId, vnfInstanceId)
        notification_type = request.data['notificationType']
        try:
            if notification_type == 'VnfLcmOperationOccurrenceNotification':
                notification = VnfLcmOperationOccurrenceNotificationSerializer(data=request.data)
                if not notification.is_valid():
                    logger.warn(notification.errors)
                HandleVnfLcmOocNotification(vnfmId, vnfInstanceId, notification.data).do_biz()
            elif notification_type == 'VnfIdentifierCreationNotification':
                notification = VnfIdentifierCreationNotificationSerializer(data=request.data)
                if not notification.is_valid():
                    logger.warn(notification.errors)
                HandleVnfIdentifierCreationNotification(vnfmId, vnfInstanceId, notification.data).do_biz()
            elif notification_type == 'VnfIdentifierDeletionNotification':
                notification = VnfIdentifierDeletionNotificationSerializer(data=request.data)
                if not notification.is_valid():
                    logger.warn(notification.errors)
                HandleVnfIdentifierDeletionNotification(vnfmId, vnfInstanceId, notification.data).do_biz()
            else:
                raise Exception('Unexpected noitifcation type value.')
            return Response(data={}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(traceback.format_exc())
            logger.error("Exception in VnfLcmOoc Notification: %s", e.args[0])
            return Response(data={'error': e.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        responses={
            status.HTTP_204_NO_CONTENT: "The notification endpoint was tested successfully.",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Inner error"
        }
    )
    def get(self, request, vnfmId, vnfInstanceId):
        logger.debug("VnfNotifyView get")
        logger.debug("vnfmId: %s vnfInstanceId: %s", vnfmId, vnfInstanceId)
        return Response(data={}, status=status.HTTP_204_NO_CONTENT)
