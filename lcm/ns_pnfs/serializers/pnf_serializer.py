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

from rest_framework import serializers


class PnfInstanceSerializer(serializers.Serializer):
    pnfId = serializers.CharField(help_text="Identifier of the PNF.", required=True, allow_null=False)
    pnfName = serializers.CharField(help_text="Name of the PNF.", required=True, allow_null=True)
    pnfdId = serializers.CharField(help_text="Identifier of the PNFD on which the PNF is based.", required=True, allow_null=True)
    pnfdInfoId = serializers.CharField(help_text="Identifier of the PNFD information object related to this PNF.", required=False, allow_null=True, allow_blank=True)
    pnfProfileId = serializers.CharField(help_text="Identifier of the related PnfProfile in the NSD on which the PNF is based.", required=True, allow_null=True)
    cpInfo = serializers.CharField(help_text="Information on the external CP of the PNF.", required=False, allow_null=True, allow_blank=True)


class PnfInstancesSerializer(serializers.ListSerializer):
    child = PnfInstanceSerializer()
