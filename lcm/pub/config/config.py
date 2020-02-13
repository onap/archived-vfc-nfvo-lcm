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

# [MSB]
MSB_SERVICE_PROTOCOL = 'http'
MSB_SERVICE_IP = '10.0.14.1'
MSB_SERVICE_PORT = '443'
MSB_BASE_URL = "%s://%s:%s" % (MSB_SERVICE_PROTOCOL, MSB_SERVICE_IP, MSB_SERVICE_PORT)

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

# [MDC]
SERVICE_NAME = "nslcm"
FORWARDED_FOR_FIELDS = ["HTTP_X_FORWARDED_FOR", "HTTP_X_FORWARDED_HOST",
                        "HTTP_X_FORWARDED_SERVER"]

# [register]
REG_TO_MSB_WHEN_START = False
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
MSB_SVC_URL = "/api/microservices/v1/services/nslcm/version/%s"


# [aai config]
AAI_BASE_URL = "http://10.0.14.1:80/aai/v11"
AAI_USER = "AAI"
AAI_PASSWD = "AAI"
REPORT_TO_AAI = True

# [sdc config]
SDC_BASE_URL = "http://10.0.14.1:80/api"
SDC_USER = "SDC"
SDC_PASSWD = "SDC"

# [DMaaP]
MR_IP = '127.0.0.1'
MR_PORT = '3904'

# [workflow]
DEPLOY_WORKFLOW_WHEN_START = False
# Support option: activiti/wso2/buildin/grapflow
WORKFLOW_OPTION = "buildin"

# [OOF config]
OOF_BASE_URL = "https://oof-osdf.onap:8698"
OOF_USER = "vfc_test"
OOF_PASSWD = "vfc_testpwd"

# [Customer information]
CUST_NAME = "some_company"
CUST_LAT = "32.897480"
CUST_LONG = "97.040443"
