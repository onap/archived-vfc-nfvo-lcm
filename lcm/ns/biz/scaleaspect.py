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

import copy
import json
import logging
import os

from lcm.pub.database.models import NSInstModel
from lcm.pub.database.models import NfInstModel
from lcm.pub.utils.values import ignore_case_get
from lcm.ns_vnfs.enum import VNF_STATUS

logger = logging.getLogger(__name__)

scale_vnf_data_mapping = {
    "vnfInstanceId": "",
    "scaleByStepData": {
        "type": "",
        "aspectId": "",
        "numberOfSteps": ""
    }
}


def mapping_conv(keyword_map, rest_return):
    resp_data = {}
    for param in keyword_map:
        if keyword_map[param]:
            if isinstance(keyword_map[param], dict):
                resp_data[param] = mapping_conv(
                    keyword_map[param], ignore_case_get(
                        rest_return, param))
            else:
                resp_data[param] = ignore_case_get(rest_return, param)
    return resp_data


def get_vnf_scale_info(filename, ns_instanceId, aspect, step):
    json_data = get_json_data(filename)
    scale_options = ignore_case_get(json_data, "scale_options")
    for i in range(scale_options.__len__()):
        ns_scale_option = scale_options[i]
        if (ignore_case_get(ns_scale_option, "ns_instanceId") == ns_instanceId) \
                and (ignore_case_get(ns_scale_option, "ns_scale_aspect") == aspect):
            ns_scale_info_list = ignore_case_get(
                ns_scale_option, "ns_scale_info_list")
            for j in range(ns_scale_info_list.__len__()):
                ns_scale_info = ns_scale_info_list[j]
                if ns_scale_info["step"] == step:
                    return ns_scale_info["vnf_scale_info"]

    return None


def get_vnf_instance_id_list(vnfd_id):
    kwargs = {}
    kwargs['package_id'] = vnfd_id
    kwargs['status'] = VNF_STATUS.ACTIVE

    nf_model_list = NfInstModel.objects.filter(**kwargs)
    vnf_instance_id_list = list()
    nf_model_len = nf_model_list.__len__()
    if nf_model_len == 0:
        logger.error("No VNF instances found(vnfd_id=%s)" % vnfd_id)
    else:
        for i in range(nf_model_len):
            vnf_instance_id_list.append(nf_model_list[i].nfinstid)

    return vnf_instance_id_list


def get_json_data(filename):
    f = open(filename)
    json_str = f.read()
    data = json.JSONDecoder().decode(json_str)
    f.close()
    return data


def check_scale_list(vnf_scale_list, ns_instanceId, aspect, step):
    if vnf_scale_list is None or vnf_scale_list.__len__() == 0:
        logger.debug(
            "The scaling option[ns=%s, aspect=%s, step=%s] does not exist. Pls check the config file." %
            (ns_instanceId, aspect, step))
        raise Exception(
            "The scaling option[ns=%s, aspect=%s, step=%s] does not exist. Pls check the config file." %
            (ns_instanceId, aspect, step))
    else:
        return vnf_scale_list


def get_scale_vnf_data_list(filename, ns_instanceId, aspect, step, scale_type):

    vnf_scale_list = get_vnf_scale_info(filename, ns_instanceId, aspect, step)
    check_scale_list(vnf_scale_list, ns_instanceId, aspect, step)
    scaleVnfDataList = set_scaleVnfData_type(vnf_scale_list, scale_type)
    logger.debug("scaleVnfDataList = %s" % scaleVnfDataList)
    return scaleVnfDataList


# Get the nsd id according to the ns instance id.
def get_nsdId(ns_instanceId):
    if NSInstModel.objects.filter(id=ns_instanceId):
        nsd_id = NSInstModel.objects.filter(id=ns_instanceId)[0].nsd_id
        return nsd_id

    return None


def check_and_set_params(scaleNsData, ns_InstanceId):
    if scaleNsData is None:
        raise Exception("Error! scaleNsData in the request is Empty!")

    scaleNsByStepsData = scaleNsData["scaleNsByStepsData"]  # scaleNsData[0]["scaleNsByStepsData"][0]
    if scaleNsByStepsData is None:
        raise Exception("Error! scaleNsByStepsData in the request is Empty!")

    aspect = scaleNsByStepsData["aspectId"]
    numberOfSteps = scaleNsByStepsData["numberOfSteps"]
    scale_type = scaleNsByStepsData["scalingDirection"]

    return aspect, numberOfSteps, scale_type


def get_scale_vnf_data(scaleNsData, ns_InstanceId):
    curdir_path = os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__))))
    filename = curdir_path + "/ns/data/scalemapping.json"
    logger.debug("filename = %s" % filename)
    aspect, numberOfSteps, scale_type = check_and_set_params(
        scaleNsData, ns_InstanceId)
    return get_scale_vnf_data_list(
        filename,
        ns_InstanceId,
        aspect,
        numberOfSteps,
        scale_type)


# Get scaling vnf data info list according to the ns instance id and request ScaleNsData.
def get_scale_vnf_data_info_list(scaleNsData, ns_InstanceId):
    # Gets the nsd id accordign to the ns instance id.
    nsd_id = get_nsdId(ns_InstanceId)

    # Gets the scalingmap json data from the package according to the ns instance id.
    # scalingmap_json = catalog.get_scalingmap_json_package(ns_InstanceId)
    base_path = os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )
    )
    scalingmap_filename = base_path + "/ns/data/scalemapping.json"
    scalingmap_json = get_json_data(scalingmap_filename)

    # Gets and checks the values of parameters.
    aspect, numberOfSteps, scale_type = check_and_set_params(
        scaleNsData, ns_InstanceId)

    # Firstly, gets the scaling vnf data info list from the scaling map json data.
    scale_vnf_data_info_list_from_json = get_scale_vnf_data_from_json(scalingmap_json, nsd_id, aspect, numberOfSteps)
    check_scale_list(scale_vnf_data_info_list_from_json, ns_InstanceId, aspect, numberOfSteps)

    # Secondly, adds the property of vnfInstanceId to the list according to the vnfd id.
    scale_vnf_data_info_list = set_scacle_vnf_instance_id(scale_vnf_data_info_list_from_json)
    check_scale_list(scale_vnf_data_info_list, ns_InstanceId, aspect, numberOfSteps)

    # Lastly, adds the property of type to the list acoording to the request ScaleNsData.
    scale_vnf_data_info_list = set_scaleVnfData_type(scale_vnf_data_info_list, scale_type)
    check_scale_list(scale_vnf_data_info_list, ns_InstanceId, aspect, numberOfSteps)

    return scale_vnf_data_info_list


# Get the vnf scaling info from the scaling_map.json according to the ns package id.
def get_scale_vnf_data_from_json(scalingmap_json, nsd_id, aspect, step):
    scale_options = ignore_case_get(scalingmap_json, "scale_options")
    for i in range(scale_options.__len__()):
        ns_scale_option = scale_options[i]
        if (ignore_case_get(ns_scale_option, "nsd_id") == nsd_id) and (
                ignore_case_get(ns_scale_option, "ns_scale_aspect") == aspect):
            ns_scale_info_list = ignore_case_get(
                ns_scale_option, "ns_scale_info")
            for j in range(ns_scale_info_list.__len__()):
                ns_scale_info = ns_scale_info_list[j]
                if ns_scale_info["step"] == step:
                    vnf_scale_info_list = ns_scale_info["vnf_scale_info"]

                    return vnf_scale_info_list

    logger.error("get_scale_vnf_data_from_json method retuan null")
    return None


# Gets the vnf instance id according to the vnfd_id and modify the list of scaling vnf info accrodingly.
def set_scacle_vnf_instance_id(vnf_scale_info_list):
    scale_vnf_data_info_list = []
    for i in range(vnf_scale_info_list.__len__()):
        vnf_scale_info = vnf_scale_info_list[i]
        vnfd_id = vnf_scale_info["vnfd_id"]
        vnf_instance_id_list = get_vnf_instance_id_list(vnfd_id)
        index = 0
        while index < vnf_instance_id_list.__len__():
            copy_vnf_scale_info = copy.deepcopy(vnf_scale_info)
            copy_vnf_scale_info.pop("vnfd_id")
            copy_vnf_scale_info["vnfInstanceId"] = vnf_instance_id_list[index]
            index += 1
            scale_vnf_data_info_list.append(copy_vnf_scale_info)

    return scale_vnf_data_info_list


# Sets the scaling type of vnf data info list.
def set_scaleVnfData_type(vnf_scale_list, scale_type):
    logger.debug(
        "vnf_scale_list = %s, type = %s" %
        (vnf_scale_list, scale_type))
    scaleVnfDataList = []
    if vnf_scale_list is not None:
        for i in range(vnf_scale_list.__len__()):
            scaleVnfData = copy.deepcopy(scale_vnf_data_mapping)
            scaleVnfData["vnfInstanceId"] = vnf_scale_list[i]["vnfInstanceId"]
            scaleVnfData["scaleByStepData"]["type"] = scale_type
            scaleVnfData["scaleByStepData"]["aspectId"] = vnf_scale_list[i]["vnf_scaleAspectId"]
            scaleVnfData["scaleByStepData"]["numberOfSteps"] = vnf_scale_list[i]["numberOfSteps"]
            scaleVnfDataList.append(scaleVnfData)
    logger.debug("scaleVnfDataList = %s" % scaleVnfDataList)
    return scaleVnfDataList
