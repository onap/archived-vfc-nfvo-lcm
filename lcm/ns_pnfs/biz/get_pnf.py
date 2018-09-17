# Copyright 2018 ZTE Corporation.
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

from lcm.pub.database.models import PNFInstModel


class GetPnf(object):
    def __init__(self, filter=None, isIndividual=False):
        self.filter = filter
        self.isIndividual = isIndividual

    def do_biz(self):
        if self.filter and "pnfId" in self.filter:
            pnf_instances = PNFInstModel.objects.filter(pnfId=self.filter["pnfId"])
            if pnf_instances and self.isIndividual:
                return pnf_instances[0]
            else:
                return pnf_instances
        elif self.filter and "nsInstanceId" in self.filter:
            return PNFInstModel.objects.filter(nsInstances__contains=self.filter["nsInstanceId"])
        else:
            return PNFInstModel.objects.all()
