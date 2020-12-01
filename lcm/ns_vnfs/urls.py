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
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from lcm.ns_vnfs.views.views import LcmNotify, NfScaleView, NfVerifyView
from lcm.ns_vnfs.views.views import NfView, NfDetailView, NfPlacement, NfTerminate
from lcm.ns_vnfs.views.views import NfVnfmInfoView, NfVimInfoView
from lcm.ns_vnfs.views.vnf_views import VnfNotifyView

urlpatterns = [
    url(r'^api/nslcm/v1/ns/vnfs$', NfView.as_view()),
    url(r'^api/nslcm/v1/ns/vnfs/(?P<vnfinstid>[0-9a-zA-Z_-]+)$', NfDetailView.as_view()),
    url(r'^api/nslcm/v1/ns/terminatevnf/(?P<vnfinstid>[0-9a-zA-Z_-]+)$', NfTerminate.as_view()),
    url(r'^api/nslcm/v1/ns/placevnf$', NfPlacement.as_view()),
    url(r'^api/nslcm/v1/ns/(?P<vnfmid>[0-9a-zA-Z_-]+)/vnfs/(?P<vnfInstanceId>[0-9a-zA-Z_-]+)/Notify$', LcmNotify.as_view()),
    url(r'^api/nslcm/v1/ns/ns_vnfs/(?P<vnfinstid>[0-9a-zA-Z_-]+)/scaling$', NfScaleView.as_view()),
    url(r'^api/nslcm/v1/vnfonboarding$', NfVerifyView.as_view()),
    url(r'^api/nslcm/v1/vnfms/(?P<vnfmid>[0-9a-zA-Z_-]+)$', NfVnfmInfoView.as_view()),
    # url(r'^api/nslcm/v1/vims/(?P<vimid>[0-9a-zA-Z_-]+)', NfVimInfoView.as_view()),
    url(r'^api/nslcm/v1/vims/(?P<cloudowner>[0-9a-zA-Z_-]+)/(?P<cloudregionid>[0-9a-zA-Z_-]+)$', NfVimInfoView.as_view()),
    url(r'^api/nslcm/v2/ns/(?P<vnfmId>[0-9a-zA-Z_-]+)/vnfs/(?P<vnfInstanceId>[0-9a-zA-Z_-]+)/Notify$', VnfNotifyView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
