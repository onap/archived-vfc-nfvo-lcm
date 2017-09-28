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

from lcm.pub.database.models import FPInstModel

logger = logging.getLogger(__name__)


def sfc_inst_failed_handle(fp_inst_id, error_msg):
    logger.error('create sfc  failed, detail message: %s' % error_msg)
    FPInstModel.objects.filter(fpid=fp_inst_id).update(status="disabled").get()


def ignorcase_get(args, key):
    if not key:
        return ""
    if key in args:
        return args[key]
    for oldkey in args:
        if oldkey.upper() == key.upper():
            return args[oldkey]
    return ""


def ignor_dot(str):
    index = str.find('.')
    if index == -1:
        return str
    return str[0:index]


def get_fp_id(fpindex, ns_model):
    index = int(int(float(fpindex)) - 1)
    return ns_model['fps'][index].get("fp_id")


def update_fp_status(fp_inst_id, status_info):
    FPInstModel.objects.filter(fpinstid=fp_inst_id).update(status=status_info)


def get_fp_model_by_fp_inst_id(ns_model_data, fp_inst_id):
    fp_databas_info = FPInstModel.objects.filter(fpinstid=fp_inst_id).get()
    fps_model = ns_model_data["fps"]
    for fp_model in fps_model:
        if fp_model["fp_id"] == fp_databas_info.fpid:
            return fp_model
