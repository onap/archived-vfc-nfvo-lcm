import logging
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class InstantiateNsView(APIView):
    def post(self, request, id):
        # todo
        return


class HealNsView(APIView):

    def post(self, request, id):
        # todo
        return


class ScaleNsView(APIView):
    def post(self, request, id):
        # todo
        return


class UpdateNsView(APIView):
    def post(self, request, id):
        # todo
        return


class TerminateNsView(APIView):
    def post(self, request, id):
        # todo
        return
