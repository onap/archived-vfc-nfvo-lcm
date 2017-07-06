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

import logging
import traceback

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from lcm.pub.database import models


logger = logging.getLogger(__name__)


class SampleList(APIView):
    """
    List all samples.
    """
    def get(self, request, format=None):
        logger.debug("get")
        return Response({"status": "active"})

class TablesList(APIView):
    def delete(self, request, modelName):
        logger.debug("Start delete model %s", modelName)
        try:
            modelNames = modelName.split("-")
            for name in modelNames:
                model_obj = eval("models.%s.objects" % name)
                model_obj.filter().delete()
                logger.debug("End delete model %s", name)
        except:
            logger.error(traceback.format_exc())
            return Response(data={"error": "failed"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(data={}, status=status.HTTP_204_NO_CONTENT)


    def get(self, request, modelName):
        logger.debug("Get model %s", modelName)
        count = 0
        try:
            model_obj = eval("models.%s.objects" % modelName)
            count = len(model_obj.filter())
        except:
            logger.error(traceback.format_exc())
            return Response(data={"error": "failed"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(data={"count": count}, status=status.HTTP_200_OK)




