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

from lcm.ns.views.deprecated.create_ns_view import CreateNSView
from lcm.ns.views.deprecated.get_del_ns_view import NSDetailView
from lcm.ns.views.deprecated.inst_ns_post_deal_view import NSInstPostDealView
from lcm.ns.views.deprecated.inst_ns_view import NSInstView
from lcm.ns.views.deprecated.term_ns_view import NSTerminateView
from lcm.ns.views.deprecated.heal_ns_view import NSHealView
from lcm.ns.views.deprecated.scale_ns_views import NSManualScaleView
from lcm.ns.views.deprecated.update_ns_view import NSUpdateView

from lcm.ns.views.sol.lcm_op_occs_view import QueryMultiNsLcmOpOccs, QuerySingleNsLcmOpOcc
from lcm.ns.views.sol.ns_instances_views import NSInstancesView, IndividualNsInstanceView
from lcm.ns.views.sol.instantiate_ns_views import InstantiateNsView
from lcm.ns.views.sol.terminate_ns_view import TerminateNsView
from lcm.ns.views.sol.subscriptions_view import SubscriptionsView
from lcm.ns.views.sol.update_ns_view import UpdateNSView
from lcm.ns.views.sol.scale_ns_views import ScaleNSView
from lcm.ns.views.sol.heal_ns_view import HealNSView
from lcm.ns.views.sol.health_check import HealthCheckView

urlpatterns = [
    # API will be deprecated in the future release
    url(r'^api/nslcm/v1/ns$', CreateNSView.as_view()),
    url(r'^api/nslcm/v1/ns/(?P<ns_instance_id>[0-9a-zA-Z_-]+)/instantiate$', NSInstView.as_view()),
    url(r'^api/nslcm/v1/ns/(?P<ns_instance_id>[0-9a-zA-Z_-]+)/terminate$', NSTerminateView.as_view()),
    url(r'^api/nslcm/v1/ns/(?P<ns_instance_id>[0-9a-zA-Z_-]+)$', NSDetailView.as_view()),
    url(r'^api/nslcm/v1/ns/(?P<ns_instance_id>[0-9a-zA-Z_-]+)/postdeal$', NSInstPostDealView.as_view()),
    url(r'^api/nslcm/v1/ns/(?P<ns_instance_id>[0-9a-zA-Z_-]+)/scale$', NSManualScaleView.as_view()),
    url(r'^api/nslcm/v1/ns/(?P<ns_instance_id>[0-9a-zA-Z_-]+)/heal$', NSHealView.as_view()),
    url(r'^api/nslcm/v1/ns/(?P<ns_instance_id>[0-9a-zA-Z_-]+)/update$', NSUpdateView.as_view()),

    # SOL005 URL API definition
    url(r'^api/nslcm/v1/ns_instances$', NSInstancesView.as_view()),
    url(r'^api/nslcm/v1/ns_instances/(?P<ns_instance_id>[0-9a-zA-Z_-]+)$', IndividualNsInstanceView.as_view()),
    url(r'^api/nslcm/v1/ns_instances/(?P<ns_instance_id>[0-9a-zA-Z_-]+)/instantiate$', InstantiateNsView.as_view()),
    url(r'^api/nslcm/v1/ns_instances/(?P<ns_instance_id>[0-9a-zA-Z_-]+)/update$', UpdateNSView.as_view()),
    url(r'^api/nslcm/v1/ns_instances/(?P<ns_instance_id>[0-9a-zA-Z_-]+)/scale$', ScaleNSView.as_view()),
    url(r'^api/nslcm/v1/ns_instances/(?P<ns_instance_id>[0-9a-zA-Z_-]+)/heal$', HealNSView.as_view()),
    url(r'^api/nslcm/v1/ns_instances/(?P<ns_instance_id>[0-9a-zA-Z_-]+)/terminate$', TerminateNsView.as_view()),
    url(r'^api/nslcm/v1/ns_lcm_op_occs/(?P<lcmopoccid>[0-9a-zA-Z_-]+)$', QuerySingleNsLcmOpOcc.as_view()),
    url(r'^api/nslcm/v1/subscriptions$', SubscriptionsView.as_view()),
    url(r'^api/nslcm/v1/ns_lcm_op_occs$', QueryMultiNsLcmOpOccs.as_view()),

    # health check
    url(r'^api/nslcm/v1/health_check$', HealthCheckView.as_view())

]

urlpatterns = format_suffix_patterns(urlpatterns)
