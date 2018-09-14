# Copyright 2018 ZTE Corporation.
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

import json
import logging

from lcm.pub.exceptions import NSLCMException
from lcm.pub.msapi.extsys import get_vnfm_by_id
from lcm.pub.utils.restcall import req_by_msb

logger = logging.getLogger(__name__)


class Subscription(object):
    def __init__(self, data):
        self.data = data
        self.vnf_instance_id = self.data['vnfInstanceId']
        self.vnfm_id = self.data['vnfmId']
        self.subscription_request_data = {}
        self.subscription_response_data = {}
        pass

    def do_biz(self):
        logger.debug('Start subscribing...')
        self.prepare_subscription_request_data()
        self.subscribe_lccn_notification()
        self.save_subscription_response_data()
        logger.debug('Subscribing has completed.')

    def prepare_lccn_subscription_request_data(self):
        vnfm_info = get_vnfm_by_id(self.vnfm_id)
        self.subscription_request_data = {
            "filter": {
                "notificationTypes": ["VnfLcmOperationOccurrenceNotification"],
                "operationTypes": [
                    "INSTANTIATE",
                    "SCALE",
                    "SCALE_TO_LEVEL",
                    "CHANGE_FLAVOUR",
                    "TERMINATE",
                    "HEAL",
                    "OPERATE",
                    "CHANGE_EXT_CONN",
                    "MODIFY_INFO"
                ],
                "operationStates": [
                    "STARTING",
                    "PROCESSING",
                    "COMPLETED",
                    "FAILED_TEMP",
                    "FAILED",
                    "ROLLING_BACK",
                    "ROLLED_BACK"
                ],
                "vnfInstanceSubscriptionFilter": {
                    "vnfdIds": [],
                    "vnfInstanceIds": [self.vnf_instance_id],
                    "vnfInstanceNames": [],
                    "vnfProductsFromProviders": {}
                }
            },
            "callbackUri": "api/gvnfmdriver/v1/vnfs/lifecyclechangesnotification",  # TODO: need reconfirming
            "authentication": {
                "authType": ["BASIC"],
                "paramsBasic": {
                    "userName": vnfm_info['userName'],
                    "password": vnfm_info['password']
                }
            }
        }

    def subscribe_lccn_notification(self):
        ret = req_by_msb('api/gvnfmdrvier/v1/%s/subscriptions' % self.vnfm_id, self.subscription_request_data)
        if ret[0] != 0:
            logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
            raise NSLCMException("Failed to subscribe from vnfm(%s)." % self.vnfm_id)
        self.subscription_response_data = json.JSONDecoder().decode(ret[1])

    def save_subscription_response_data(self):
        pass
