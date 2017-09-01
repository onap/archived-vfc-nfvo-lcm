# Copyright 2017 ZTE Corporation.
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
import uuid

from lcm.pub.exceptions import NSLCMException
from lcm.pub.utils import restcall
from lcm.pub.config.config import AAI_BASE_URL, AAI_USER, AAI_PASSWD

logger = logging.getLogger(__name__)


def call_aai(resource, method, content=''):
    additional_headers = {
        'X-FromAppId': 'VFC-NFVO-LCM',
        'X-TransactionId': str(uuid.uuid1())
    }
    return restcall.call_req(base_url=AAI_BASE_URL, 
        user=AAI_USER, 
        passwd=AAI_PASSWD, 
        auth_type=restcall.rest_no_auth, 
        resource=resource, 
        method=method, 
        content=content,
        additional_headers=additional_headers)

def create_ns_aai(global_customer_id, service_type, service_instance_id, data):
    resource = "/business/customers/customer/%s/service-subscriptions/service-subscription/" \
               "%s/service-instances/service-instance/%s" % \
               (global_customer_id, service_type, service_instance_id)
    ret = call_aai(resource, "PUT", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Ns instance creation exception in AAI")
    return json.JSONDecoder().decode(ret[1])

def delete_ns_aai(global_customer_id, service_type, service_instance_id, data):
    resource = "/business/customers/customer/%s/service-subscriptions/service-subscription/" \
               "%s/service-instances/service-instance/%s" % \
               (global_customer_id, service_type, service_instance_id)
    ret = call_aai(resource, "DELETE", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Ns instance delete exception in AAI")
    return json.JSONDecoder().decode(ret[1])

def query_ns_aai(global_customer_id, service_type, service_instance_id, data):
    resource = "/business/customers/customer/%s/service-subscriptions/service-subscription/" \
               "%s/service-instances/service-instance/%s" % \
               (global_customer_id, service_type, service_instance_id)
    ret = call_aai(resource, "GET", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Ns instance query exception in AAI")
    return json.JSONDecoder().decode(ret[1])

def create_vnf_aai(vnf_id, data):
    resource = "/network/generic-vnfs/generic-vnf/%s" % vnf_id
    ret = call_aai(resource, "PUT", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Vnf instance creation exception in AAI")
    return json.JSONDecoder().decode(ret[1])

def delete_vnf_aai(vnf_id, data=''):
    resource = "/network/generic-vnfs/generic-vnf/%s" % vnf_id
    ret = call_aai(resource, "DELETE", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Vnf instance delete exception in AAI")
    return json.JSONDecoder().decode(ret[1])

def query_vnf_aai(vnf_id, data):
    resource = "/network/generic-vnfs/generic-vnf/%s" % vnf_id
    ret = call_aai(resource, "GET", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Vnf instance query exception in AAI")
    return json.JSONDecoder().decode(ret[1])
