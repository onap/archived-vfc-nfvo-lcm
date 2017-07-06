# Copyright 2016-2017 ZTE Corporation.
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
from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns

from lcm.ns.vnfs.views import NfView, NfDetailView, NfGrant, LcmNotify, NfScaleView, NfVerifyView

urlpatterns = patterns('',
                       url(r'^openoapi/nslcm/v1/ns/vnfs$', NfView.as_view()),
                       url(r'^openoapi/nslcm/v1/ns/vnfs/(?P<vnfinstid>[0-9a-zA-Z_-]+)$', NfDetailView.as_view()),
                       url(r'^openoapi/nslcm/v1/ns/grantvnf$', NfGrant.as_view()),
                       url(r'^openoapi/nslcm/v1/ns/(?P<vnfmid>[0-9a-zA-Z_-]+)'
                           r'/vnfs/(?P<vnfInstanceId>[0-9a-zA-Z_-]+)/Notify$',
                           LcmNotify.as_view()),
                       url(r'^openoapi/nslcm/v1/ns/vnfs/(?P<vnfinstid>[0-9a-zA-Z_-]+)/scaling$', NfScaleView.as_view()),
                       url(r'^openoapi/nslcm/v1/vnfonboarding$', NfVerifyView.as_view()),
                       )

urlpatterns = format_suffix_patterns(urlpatterns)
