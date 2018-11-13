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

from lcm.pub.database.models import SubscriptionModel
from lcm.pub.exceptions import NSLCMException
from lcm.pub.msapi.extsys import get_vnfm_by_id
from lcm.pub.utils.restcall import req_by_msb
from lcm.pub.utils.values import ignore_case_get
from lcm.pub.config import config as pub_config

logger = logging.getLogger(__name__)


class SubscriptionCreation(object):
    def __init__(self, data):
        self.data = data
        self.vnf_instance_id = self.data['vnfInstanceId']
        self.vnfm_id = self.data['vnfmId']
        self.subscription_request_data = {}
        self.subscription_response_data = {}
        pass

    def do_biz(self):
        logger.debug('Start subscribing...')
        self.prepare_lccn_subscription_request_data()
        self.send_subscription_request()
        self.save_subscription_response_data()
        logger.debug('Subscribing has completed.')

    def prepare_lccn_subscription_request_data(self):
        vnfm_info = get_vnfm_by_id(self.vnfm_id)
        call_back = "http://%s:%s/api/gvnfmdriver/v1/vnfs/lifecyclechangesnotification" % (pub_config.MSB_SERVICE_IP, pub_config.MSB_SERVICE_PORT)
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
                    # "vnfdIds": [],
                    "vnfInstanceIds": [self.vnf_instance_id],
                    # "vnfInstanceNames": [],
                    # "vnfProductsFromProviders": {}
                }
            },
            "callbackUri": call_back,  # TODO: need reconfirming
            "authentication": {
                "authType": ["BASIC"],
                "paramsBasic": {
                    # "userName": vnfm_info['userName'],
                    # "password": vnfm_info['password']
                }
            }
        }
        if vnfm_info['userName']:
            self.subscription_request_data["authentication"]["paramsBasic"]["userName"] = vnfm_info['userName']
        if vnfm_info['password']:
            self.subscription_request_data["authentication"]["paramsBasic"]["password"] = vnfm_info['password']

    def send_subscription_request(self):
        ret = req_by_msb('api/gvnfmdriver/v1/%s/subscriptions' % self.vnfm_id, 'POST', json.JSONEncoder().encode(self.subscription_request_data))
        if ret[0] != 0:
            logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
            raise NSLCMException("Failed to subscribe from vnfm(%s)." % self.vnfm_id)
        self.subscription_response_data = json.JSONDecoder().decode(ret[1])

    def save_subscription_response_data(self):
        logger.debug("Save subscription[%s] to the database" % self.subscription_response_data['id'])
        lccn_filter = self.subscription_response_data['filter']
        SubscriptionModel.objects.create(
            subscription_id=self.subscription_response_data['id'],
            notification_types=json.dumps(lccn_filter['notificationTypes']),
            operation_types=json.dumps(lccn_filter['operationTypes']),
            operation_states=json.dumps(lccn_filter['operationStates']),
            vnf_instance_filter=json.dumps(lccn_filter['vnfInstanceSubscriptionFilter']),
            callback_uri=self.subscription_response_data['callbackUri'],
            links=json.dumps(self.subscription_response_data['_links'])
        )
        logger.debug('Subscription[%s] has been created', self.subscription_response_data['id'])


class SubscriptionDeletion(object):
    def __init__(self, vnfm_id, vnf_instance_id):
        self.vnfm_id = vnfm_id
        self.vnf_instance_id = vnf_instance_id
        self.subscription_id = None
        self.subscription = None

    def do_biz(self):
        self.filter_subscription()
        self.send_subscription_deletion_request()
        self.delete_subscription_in_db()

    def filter_subscription(self):
        subscritptions = SubscriptionModel.objects.filter(vnf_instance_filter__contains=self.vnf_instance_id)
        if not subscritptions.exists():
            logger.debug("Subscription contains VNF(%s) does not exist." % self.vnf_instance_id)
        self.subscription = subscritptions.first()

    def send_subscription_deletion_request(self):
        if self.subscription:
            self.subscription_id = ignore_case_get(self.subscription, 'id')
            ret = req_by_msb('api/gvnfmdriver/v1/%s/subscriptions/%s' % (self.vnfm_id, self.subscription_id), 'DELETE')
            if ret[0] != 0:
                logger.error('Status code is %s, detail is %s.', ret[2], ret[1])
                raise NSLCMException("Failed to subscribe from vnfm(%s)." % self.vnfm_id)
            logger.debug('Subscripton(%s) in vnfm(%s) has been deleted.' % (self.subscription, self.vnfm_id))

    def delete_subscription_in_db(self):
        if self.subscription:
            self.subscription.delete()
