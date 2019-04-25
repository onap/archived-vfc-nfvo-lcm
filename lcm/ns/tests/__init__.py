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
from lcm.pub.utils import fileutil

cur_path = os.path.dirname(os.path.abspath(__file__))
CREATE_NS_DICT = fileutil.read_json_file(cur_path + '/data/create_ns.json')
NS_INFO_AAI_DICT = fileutil.read_json_file(cur_path + '/data/ns_info_aai.json')
VNFD_MODEL_DICT = fileutil.read_json_file(cur_path + '/data/vnfd_model.json')
HEAL_NS_DICT = fileutil.read_json_file(cur_path + '/data/heal_ns.json')
HEAL_VNF_DICT = fileutil.read_json_file(cur_path + '/data/heal_vnf.json')
NSD_MODEL_DICT = fileutil.read_json_file(cur_path + '/data/nsd_model.json')
NSD_MODEL_WITH_PNF_DICT = fileutil.read_json_file(cur_path + '/data/nsd_model_with_pnf.json')
VNFM_LIST_IN_AAI_DICT = fileutil.read_json_file(cur_path + '/data/vnfm_list_in_aai.json')
VNFM_IN_AAI_DICT = fileutil.read_json_file(cur_path + '/data/vnfm_in_aai.json')
JOB_DICT = fileutil.read_json_file(cur_path + '/data/job.json')
INSTANTIATE_NS_WITH_PNF_DICT = fileutil.read_json_file(cur_path + '/data/instantiate_ns_with_pnf.json')
INSTANTIATE_NS_DICT = fileutil.read_json_file(cur_path + '/data/instantiate_ns.json')
SCALE_DICT = fileutil.read_json_file(cur_path + '/data/scale.json')
SCALING_MAP_DICT = fileutil.read_json_file(cur_path + '/data/scalemapping.json')
SCALE_NS_DICT = fileutil.read_json_file(cur_path + '/data/scale_ns.json')
OCCURRENCE_DICT = fileutil.read_json_file(cur_path + '/data/occurrence.json')
NSLCMOP_WITH_EXCLUDE_DEFAULT_DICT = fileutil.read_json_file(cur_path + '/data/occurrence_exclude_default.json')
SUBSCRIPTION_DICT = fileutil.read_json_file(cur_path + '/data/subscription.json')
SOL_REST_HEADER_DICT = fileutil.read_json_file(cur_path + '/data/sol_rest_header.json')
SOL_CREATE_NS_DICT = fileutil.read_json_file(cur_path + '/data/sol_create_ns.json')
NS_PACKAGE_INFO_DICT = fileutil.read_json_file(cur_path + '/data/ns_package_info.json')
SOL_INSTANTIATE_NS_DICT = fileutil.read_json_file(cur_path + '/data/sol_instantiate_ns.json')
SOL_INSTANTIATE_NS_VCPE_DICT = fileutil.read_json_file(cur_path + '/data/sol_instantiate_ns_vcpe.json')
SOL_INSTANTIATE_NS_WITH_PNF_DICT = fileutil.read_json_file(cur_path + '/data/sol_instantiate_ns_with_pnf.json')
VCPE_NS_MODEL_DICT = fileutil.read_json_file(cur_path + '/data/vcpe_ns_model.json')
SUBSCRIPTION_NS_OPERATION_DICT = fileutil.read_json_file(cur_path + '/data/subscription_ns_operation.json')
SUBSCRIPTION_NS_DELETION_DICT = fileutil.read_json_file(cur_path + '/data/subscription_ns_deletion.json')
