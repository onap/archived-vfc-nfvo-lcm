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

from lcm.pub.utils.restcall import req_by_msb
from lcm.pub.exceptions import NSLCMException

logger = logging.getLogger(__name__)


def parse_nsd(csar_id, input_parameters=[]):
    req_param = json.JSONEncoder().encode({"csarId": csar_id, "inputs": input_parameters})
    ret = req_by_msb("/api/catalog/v1/parsernsd", "POST", req_param)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Failed to parsernsd of CSAR(%s) from catalog." % csar_id)
    ns_model = json.JSONDecoder().decode(ret[1])
    return ns_model.get("model")


def parse_vnfd(csar_id, input_parameters=[]):
    req_param = json.JSONEncoder().encode({"csarId": csar_id, "inputs": input_parameters})
    ret = req_by_msb("/api/catalog/v1/parservnfd", "POST", req_param)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Failed to parse_vnfd of CSAR(%s) from catalog." % csar_id)
    vnf_model = json.JSONDecoder().decode(ret[1])
    return vnf_model.get("model")


def query_nspackage_by_id(csar_id):
    ret = req_by_msb("/api/catalog/v1/nspackages/%s" % csar_id, "GET")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Failed to query ns CSAR(%s) from catalog." % csar_id)
    return json.JSONDecoder().decode(ret[1])


def query_vnfpackage_by_id(csar_id):
    ret = req_by_msb("/api/catalog/v1/vnfpackages/%s" % csar_id, "GET")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Failed to query vnf CSAR(%s) from catalog." % csar_id)
    return json.JSONDecoder().decode(ret[1])


def query_pnf_descriptor(filter=None):
    if filter:
        pnfdId = filter.get("pnfdId")
        ret = req_by_msb("/api/nsd/v1/pnf_descriptors?pnfdId=%s" % pnfdId, "GET")
    else:
        ret = req_by_msb("/api/nsd/v1/pnf_descriptors", "GET")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Failed to query pnf descriptor(%s) from catalog." % pnfdId)
    return json.JSONDecoder().decode(ret[1])


def modify_nsd_state(csar_id):
    req_param = json.JSONEncoder().encode({"usageState": 1})
    ret = req_by_msb("/api/catalog/v1/ns_descriptors/%s" % csar_id, "PUT", req_param)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Failed to modify nsd state of CSAR(%s) from catalog." % csar_id)
