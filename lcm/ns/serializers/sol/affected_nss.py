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

from lcm.ns import const


CHANGE_TYPE = [
    const.CHANGE_TYPES.ADD,
    const.CHANGE_TYPES.REMOVE,
    const.CHANGE_TYPES.INSTANTIATE,
    const.CHANGE_TYPES.SCALE,
    const.CHANGE_TYPES.UPDATE,
    const.CHANGE_TYPES.HEAL,
    const.CHANGE_TYPES.TERMINATE
]

CHANGE_RESULT = [
    const.CHANGE_RESULTS.COMPLETED,
    const.CHANGE_RESULTS.ROLLED_BACK,
    const.CHANGE_RESULTS.FAILED,
    const.CHANGE_RESULTS.PARTIALLY_COMPLETED
]


class AffectedNssSerializer(serializers.Serializer):
    nsInstanceId = serializers.UUIDField(
        help_text="Identifier of the nested NS instance.",
        required=True
    )
    nsdId = serializers.UUIDField(
        help_text="Identifier of the NSD of the nested NS instance.",
        required=True
    )
    changeType = serializers.ChoiceField(
        help_text="Signals the type of lifecycle change.",
        required=True,
        choices=CHANGE_TYPE
    )
    changeResult = serializers.ChoiceField(
        help_text="Signals the result of change identified by the 'changeType' attribute.",
        required=True,
        choices=CHANGE_RESULT
    )
