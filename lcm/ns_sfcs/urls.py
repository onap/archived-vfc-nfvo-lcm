# Copyright 2016 ZTE Corporation.
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
from lcm.ns_sfcs.views.detail_views import SfcDetailView
from rest_framework.urlpatterns import format_suffix_patterns

from lcm.ns_sfcs.views.views import SfcView, SfcInstanceView, PortPairGpView, FlowClaView, PortChainView

urlpatterns = [
    url(r'^api/nslcm/v1/ns/sfcs$', SfcView.as_view()),
    url(r'^api/nslcm/v1/ns/sfcs/(?P<sfc_inst_id>[0-9a-zA-Z_-]+)$', SfcDetailView.as_view()),
    url(r'^api/nslcm/v1/ns/sfc_instance$', SfcInstanceView.as_view()),
    url(r'^api/nslcm/v1/ns/create_port_pair_group$', PortPairGpView.as_view()),
    url(r'^api/nslcm/v1/ns/create_flow_classifier$', FlowClaView.as_view()),
    url(r'^api/nslcm/v1/ns/create_port_chain$', PortChainView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
