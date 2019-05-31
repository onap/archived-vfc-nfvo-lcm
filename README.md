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

# Micro service of network service life cycle management.

1. Code structure guide
   ./           nslcm project root dir files, including license, pom, tox, start/stop scripts, log configuration, etc
   ./docker     nslcm docker related scripts
   ./docs       nslcm project documents
   ./lcm        NS life cycle management
       ./jobs      nslcm related job
       ./ns        NS life cycle API&logic
             ./               API url, const, enum files
             ./biz            NS LCM management busyness logic files
             ./data           NS LCM workflow plans
             ./serializers    API related request and response definitions.
             ./tests          Test cases
             ./views          API related NS views
       ./ns_pnfs   PNF related API&logic in NS layer
       ./ns_sfcs   SFC related API&logic in NS layer
       ./ns_vls    VL related API&logic in NS layer
       ./ns_vnfs   VNF related API&logic in NS layer
       ./pub       common class, including database model, external micro service API, utils, and config parameters.
       ./samples   project micro service health check
       ./swagger   auto-generate nslcm swagger
       ./workflows workflow related logic
   ./logs       nslcm log file
   ./resources  nslcm resources, including database scripts
