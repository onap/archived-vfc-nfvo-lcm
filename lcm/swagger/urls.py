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
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

swagger_info = openapi.Info(
    title="vfc-nfvo-lcm API",
    default_version='v1',
    description="""

The `swagger-ui` view can be found [here](/api/nslcm/v1/swagger).
The `ReDoc` view can be found [here](/api/nslcm/v1/redoc).
The swagger YAML document can be found [here](/api/nslcm/v1/swagger.json).
The swagger YAML document can be found [here](/api/nslcm/v1/swagger.yaml)."""
)

SchemaView = get_schema_view(
    validators=['ssv', 'flex'],
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # url(r'^api/nslcm/v1/swagger.json$', SwaggerJsonView.as_view()),
    url(r'^api/nslcm/v1/swagger(?P<format>.json|.yaml)$', SchemaView.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^api/nslcm/v1/swagger$', SchemaView.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^api/nslcm/v1/redoc$', SchemaView.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
