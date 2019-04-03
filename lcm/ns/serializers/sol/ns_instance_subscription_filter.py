# Copyright (c) 2019, CMCC Technologies Co., Ltd.
# Copyright 2019 ZTE Corporation.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from rest_framework import serializers


class NsInstanceSubscriptionFilter(serializers.Serializer):
    nsdIds = serializers.ListField(
        help_text="Match NS instances that were created based on a NSD identified by one of the nsdId values listed in this attribute.",
        child=serializers.CharField(),
        required=False,
        allow_null=False)
    vnfdIds = serializers.ListField(
        help_text="Match NS instances that contain VNF instances that were created based on"
                  " identified by one of the vnfdId values listed in this attribute.",
        child=serializers.CharField(),
        required=False,
        allow_null=False)
    pnfdIds = serializers.ListField(
        help_text="Match NS instances that contain PNFs that are represented by a PNFD"
                  " identified by one of the pnfdId values listed in this attribute",
        child=serializers.CharField(),
        required=False,
        allow_null=False)
    nsInstanceIds = serializers.ListField(
        help_text="Match NS instances with an instance identifier listed in this attribute",
        child=serializers.CharField(),
        required=False,
        allow_null=False)
    nsInstanceNames = serializers.ListField(
        help_text="Match NS instances with a NS Instance Name listed in this attribute.",
        child=serializers.CharField(),
        required=False,
        allow_null=False)
