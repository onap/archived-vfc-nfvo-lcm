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

from lcm.pub.utils.toscaparser.nsdmodel import EtsiNsdInfoModel
from lcm.pub.utils.toscaparser.vnfdmodel import EtsiVnfdInfoModel


def parse_nsd(path, input_parameters=[]):
    tosca_obj = EtsiNsdInfoModel(path, input_parameters)
    strResponse = json.dumps(tosca_obj, default=lambda obj: obj.__dict__)
    strResponse = strResponse.replace(': null', ': ""')
    return strResponse


def parse_vnfd(path, input_parameters=[]):
    tosca_obj = EtsiVnfdInfoModel(path, input_parameters)
    strResponse = json.dumps(tosca_obj, default=lambda obj: obj.__dict__)
    strResponse = strResponse.replace(': null', ': ""')
    return strResponse
