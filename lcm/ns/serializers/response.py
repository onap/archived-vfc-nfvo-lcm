# Copyright (c) 2019, CMCC Technologies Co., Ltd.

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


class ProblemDetailsSerializer(serializers.Serializer):
    type = serializers.CharField(help_text="Type", required=False, allow_null=True)
    title = serializers.CharField(help_text="Title", required=False, allow_null=True)
    status = serializers.IntegerField(help_text="Status", required=True)
    detail = serializers.CharField(help_text="Detail", required=True, allow_null=True)
    instance = serializers.CharField(help_text="Instance", required=False, allow_null=True)
    additional_details = serializers.ListField(help_text="Any number of additional attributes, as defined"
                                                         " in a specification or by an implementation.",
                                               required=False, allow_null=True)
