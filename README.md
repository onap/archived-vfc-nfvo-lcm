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
   ./         nslcm project files
   ./docker   nslcm docker related scripts
   ./logs     nslcm log file
   ./lcm      NS life cycle management
       ./ns      NS life cycle API& logic
             ./               API url and const
             ./views          API related NS views, each operation is a view
             ./serializers    API related request and response parametes.
                              Suggest related to sol003/sol005, each datatype is a file.
                              Common datatypes are put into the common file
             ./biz            NS LCM mangement busyness logic files
             ./tests          all the test case. At least each API should have a test case
        ./ns_sfcs  SFC of NS API & logic
        ./ns_vls   vl in NS API & logic
        ./ns_vnfs  vnf in NS API & logic, which is used to integrate with VNFM drivers.
       ./jobs      nslcm related job
       ./pub       common class, including database model, external micro service API, utils, and config parameters.
       ./samples   project micro service health check
       ./swagger   auto-generate nslcm swagger
