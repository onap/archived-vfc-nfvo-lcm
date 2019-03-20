import logging

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class NSInstancesView(APIView):
    def get(self, request):
        logger.debug(request.query_params)
        # todo

    def post(self, request):
        logger.debug("Enter NSInstancesView::POST ns_instances %s", request.data)
        # todo
        return Response(data={}, status=status.HTTP_201_CREATED)


class IndividualNsInstanceView(APIView):
    def get(self, request, id):
        logger.debug("Enter IndividualNsInstanceView::get ns(%s)", id)
        # todo
        return Response(data={}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=None,
        responses={
            status.HTTP_204_NO_CONTENT: None
        }
    )
    def delete(self, request, id):
        logger.debug("Enter IndividualNsInstanceView::DELETE ns_instance(%s)", id)
        # todo
        return Response(data={}, status=status.HTTP_204_NO_CONTENT)
