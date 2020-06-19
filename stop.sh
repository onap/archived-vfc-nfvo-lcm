#!/bin/bash
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
ps auxww | grep "manage.py runserver 0.0.0.0:8403" | awk '{print $1}' | xargs kill -9
# ps auxww |grep 'uwsgi --http' |awk '{print $1}' |xargs kill -9
if [ "${SSL_ENABLED}" = "true" ]; then
   ps auxww |grep 'uwsgi --https :8403' |awk '{print $1}' |xargs kill -9
else
   ps auxww |grep 'uwsgi --http :8403' |awk '{print $1}' |xargs kill -9
fi