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
from rest_framework.urlpatterns import format_suffix_patterns
from lcm.packages import views

urlpatterns = [
    url(r'^openoapi/nslcm/v1/nspackage/(?P<csarId>[0-9a-zA-Z\-\_]+)$', views.ns_access_csar, name='ns_access_csar'),
    url(r'^openoapi/nslcm/v1/nspackage$', views.ns_on_boarding, name='ns_on_boarding'),
    url(r'^openoapi/nslcm/v1/nspackage/(?P<csarId>[0-9a-zA-Z\-\_]+)/deletionpending$',
        views.ns_delete_pending_csar, name='ns_delete_pending_csar'),
    url(r'^openoapi/nslcm/v1/nspackage/(?P<csarId>[0-9a-zA-Z\-\_]+)/(?P<operation>(disabled|enabled))$',
        views.ns_set_state_csar, name='ns_set_state_csar'),
    url(r'^openoapi/nslcm/v1/vnfpackage/(?P<csarId>[0-9a-zA-Z\-\_]+)$', views.nf_access_csar, name='nf_access_csar'),
    url(r'^openoapi/nslcm/v1/vnfpackage$', views.nf_on_boarding, name='nf_on_boarding'),
    url(r'^openoapi/nslcm/v1/vnfpackage/(?P<csarId>[0-9a-zA-Z\-\_]+)/deletionpending$',
        views.nf_delete_pending_csar, name='nf_delete_pending_csar'), ]

urlpatterns = format_suffix_patterns(urlpatterns)
