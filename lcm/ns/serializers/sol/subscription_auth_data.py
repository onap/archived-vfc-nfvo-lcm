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

from lcm.ns.enum import AUTH_TYPE
from lcm.pub.utils.enumutil import enum_to_list


class OAuthCredentialsSerializer(serializers.Serializer):
    clientId = serializers.CharField(
        help_text="Client identifier to be used in the access token request of the OAuth 2.0 client credentials grant type.",
        required=False,
        max_length=255,
        allow_null=False)
    clientPassword = serializers.CharField(
        help_text="Client password to be used in the access token request of the OAuth 2.0 client credentials grant type.",
        required=False,
        max_length=255,
        allow_null=False)
    tokenEndpoint = serializers.CharField(
        help_text="The token endpoint from which the access token can be obtained.",
        required=False,
        max_length=255,
        allow_null=False)


class BasicAuthSerializer(serializers.Serializer):
    userName = serializers.CharField(
        help_text="Username to be used in HTTP Basic authentication.",
        max_length=255,
        required=False,
        allow_null=False)
    password = serializers.CharField(
        help_text="Password to be used in HTTP Basic authentication.",
        max_length=255,
        required=False,
        allow_null=False)


class SubscriptionAuthenticationSerializer(serializers.Serializer):
    authType = serializers.ListField(
        help_text="Defines the types of Authentication / Authorization which the API consumer is"
                  " willing to accept when receiving a notification.",
        child=serializers.ChoiceField(
            required=True,
            choices=enum_to_list(AUTH_TYPE)),
        required=True)
    paramsBasic = BasicAuthSerializer(
        help_text="Parameters for authentication/authorization using BASIC.",
        required=False,
        allow_null=False)
    paramsOauth2ClientCredentials = OAuthCredentialsSerializer(
        help_text="Parameters for authentication/authorization using OAUTH2_CLIENT_CREDENTIALS.",
        required=False,
        allow_null=False)
