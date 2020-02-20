# Copyright (c) 2019, CMCC Technologies Co., Ltd.
# Licensed under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import httplib2
ud_data = {'csarId': '20c28260-5078-4729-847f-f8b0a3bff8d9'}
headers = {'content-type': 'application/json', 'accept': 'application/json'}
http = httplib2.Http()
resp, resp_content = http.request('http://159.138.61.203:30280/api/catalog/v1/vnfpackages',
                                  method="POST",
                                  body=json.dumps(ud_data),
                                  headers=headers)
print(resp['status'], resp_content)
