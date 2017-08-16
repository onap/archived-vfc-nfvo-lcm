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
from os import R_OK, access

from lcm.pub.exceptions import NSLCMException
from toscaparser.tosca_template import ToscaTemplate

def parse_nsd_model(path, input_parameters):
    isexist = check_file_exist(path)
    if isexist:
        nsd_tpl = parse_nsd_csar(path, input_parameters)
    else:
        raise NSLCMException('%s is not exist.' % path)
    return nsd_tpl


def parse_vnfd_model(path, input_parameters):
    isexist = check_file_exist(path)
    if isexist:
        vnfd_tpl = parse_vnfd_csar(path, input_parameters)
    else:
        raise NSLCMException('%s is not exist.' % path)
    return vnfd_tpl

def check_file_exist(path):
    if path.exists(path) and path.isfile(path) and access(path, R_OK):
        return True
    else:
        return False

def parse_nsd_csar(path, input_parameters=[], a_file=True):
    nsd_object = None
    nsd_object = ToscaTemplate(path, input_parameters)
    return nsd_object


def parse_vnfd_csar(path, input_parameters=[], a_file=True):
    vnfd_object = None
    vnfd_object = ToscaTemplate(path, input_parameters)
    return vnfd_object