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


class JobHistorySerializer(serializers.Serializer):
    status = serializers.CharField(
        help_text="Status of job",
        required=True)
    progress = serializers.CharField(
        help_text="Progress of job",
        required=True)
    statusDescription = serializers.CharField(
        help_text="Description of job",
        required=False,
        allow_null=True)
    errorCode = serializers.CharField(
        help_text="Error code of job",
        required=False,
        allow_null=True)
    responseId = serializers.CharField(
        help_text="Response index of job",
        required=True)


class JobDescriptorSerializer(serializers.Serializer):
    status = serializers.CharField(
        help_text="Status of job",
        required=True)
    # progress = serializers.CharField(help_text="Progress of job", required=True)
    progress = serializers.IntegerField(
        help_text="Progress of job",
        required=True)
    statusDescription = serializers.CharField(
        help_text="Description of job",
        required=False,
        allow_null=True)
    errorCode = serializers.CharField(
        help_text="Error code of job",
        required=False,
        allow_null=True)
    responseId = serializers.CharField(
        help_text="Response index of job",
        required=True)
    responseHistoryList = JobHistorySerializer(
        help_text="History of job",
        many=True)


class JobQueryRespSerializer(serializers.Serializer):
    jobId = serializers.CharField(
        help_text="UUID of job",
        required=True)
    responseDescriptor = JobDescriptorSerializer(
        help_text="Descriptor of job",
        required=False)


class JobUpdReqSerializer(serializers.Serializer):
    progress = serializers.CharField(
        help_text="Progress of job",
        required=True)
    desc = serializers.CharField(
        help_text="Description of job",
        required=False)
    errcode = serializers.CharField(
        help_text="Error code of job",
        required=False)


class JobUpdRespSerializer(serializers.Serializer):
    result = serializers.CharField(
        help_text="Result of the job",
        required=True)
    msg = serializers.CharField(
        help_text="Detail of the job",
        required=False)
