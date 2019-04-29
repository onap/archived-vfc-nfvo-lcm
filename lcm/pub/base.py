# Copyright 2019 ZTE Corporation.
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


class ApiModelBase(object):
    def to_dict(self):
        r_dict = to_dict(self)
        return r_dict


def to_dict(obj, cls=ApiModelBase):
    r_dict = {}
    for k, v in obj.__dict__.iteritems():
        if isinstance(v, cls):
            r_dict[k] = to_dict(v)
        elif isinstance(v, list):
            r_dict[k] = [to_dict(obj) for obj in v]
        else:
            r_dict[k] = v
    return r_dict
