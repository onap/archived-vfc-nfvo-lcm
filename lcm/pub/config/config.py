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
import os

# [MSB]
MSB_SERVICE_IP = '127.0.0.1'
MSB_SERVICE_PORT = '80'

# [IMAGE LOCAL PATH]
ROOT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
IMAGE_ROOT_PATH = os.path.join(ROOT_PATH, "/VmNfvo/VnfProduct")

# [REDIS]
REDIS_HOST = '127.0.0.1'
REDIS_PORT = '6379'
REDIS_PASSWD = ''

# [mysql]
DB_IP = "127.0.0.1"
DB_PORT = 3306
DB_NAME = "vfcnfvolcm"
DB_USER = "vfcnfvolcm"
DB_PASSWD = "vfcnfvolcm"

# [register]
REG_TO_MSB_WHEN_START = True
REG_TO_MSB_REG_URL = "/api/microservices/v1/services"
REG_TO_MSB_REG_PARAM = {
    "serviceName": "nslcm",
    "version": "v1",
    "url": "/api/nslcm/v1",
    "protocol": "REST",
    "visualRange": "1",
    "nodes": [{
        "ip": "127.0.0.1",
        "port": "8403",
        "ttl": 0
    }]
}

# delete image from vim option when delete csar
IGNORE_DEL_IMG_WEHN_DEL_CSAR = True

# catalog path(values is defined in settings.py)
CATALOG_ROOT_PATH = None
CATALOG_URL_PATH = None

# [aai config]
AAI_BASE_URL = "https://127.0.0.1:8443/aai/v11"
AAI_USER = "AAI"
AAI_PASSWD = "AAI"
REPORT_TO_AAI = False

# [sdc config]
SDC_BASE_URL = "https://127.0.0.1:8443/api/sdc/v1"
SDC_USER = "SDC"
SDC_PASSWD = "SDC"

# [workflow]
DEPLOY_WORKFLOW_WHEN_START = True
# Support option: activiti/wso2/buildin
WORKFLOW_OPTION = "buildin"






