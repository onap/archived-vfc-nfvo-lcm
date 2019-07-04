# Copyright (c) 2019, CMCC Technologies Co., Ltd.
# Copyright (c) 2019, ZTE Corporation.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import logging

from lcm.pub.database.models import NSLcmOpOccModel
from lcm.pub.exceptions import NSLCMException
from lcm.ns.const import NS_OCC_BASE_URI, NS_INSTANCE_BASE_URI

logger = logging.getLogger(__name__)
FILTERS = {
    'id': 'id',
    'operationState': 'operation_state',
    'stateEnteredTime': 'state_entered_time',
    'startTime': 'start_time',
    'nsInstanceId': 'ns_instance_id',
    'operation': 'operation'
}


class QueryNsLcmOpOcc:
    def __init__(self, data, lcm_op_occ_id=''):
        self.ns_lcm_op_occ_id = lcm_op_occ_id
        self.params = data

    def query_multi_ns_lcm_op_occ(self):
        query_data = {}
        logger.debug("QueryMultiNsLcmOpOccs--get--biz::> Check for filters in query params" % self.params)
        for query, value in list(self.params.items()):
            if query in FILTERS:
                query_data[FILTERS[query]] = value
        # Query the database with filters if the request has fields in request params, else fetch all records
        if query_data:
            lcm_ops = NSLcmOpOccModel.objects.filter(**query_data)
        else:
            lcm_ops = NSLcmOpOccModel.objects.all()
        if not lcm_ops.exists():
            return []
            # raise NSLCMException('LCM Operation Occurances do not exist')
        return [self.fill_resp_data(lcm_op) for lcm_op in lcm_ops]

    def fill_resp_data(self, lcm_op):
        NS_LCM_OP_OCC_URI = NS_OCC_BASE_URI % lcm_op.id
        resp_data = {
            'id': lcm_op.id,
            'operationState': lcm_op.operation_state,
            'stateEnteredTime': lcm_op.state_entered_time,
            'startTime': lcm_op.start_time,
            'nsInstanceId': lcm_op.ns_instance_id,
            'operation': lcm_op.operation,
            'isAutomaticInvocation': lcm_op.is_automatic_invocation,
            'operationParams': json.loads(lcm_op.operation_params),
            'isCancelPending': lcm_op.is_cancel_pending,
            'cancelMode': lcm_op.cancel_mode,
            'error': None if not lcm_op.error else json.loads(lcm_op.error),
            'resourceChanges': None if not lcm_op.resource_changes else json.loads(lcm_op.resource_changes),
            '_links': {
                'self': {'href': NS_LCM_OP_OCC_URI},
                'nsInstance': {'href': NS_INSTANCE_BASE_URI % lcm_op.ns_instance_id},
                'retry': {'href': NS_LCM_OP_OCC_URI + '/retry'},
                'rollback': {'href': NS_LCM_OP_OCC_URI + '/rollback'},
                'continue': {'href': NS_LCM_OP_OCC_URI + '/continue'},
                'fail': {'href': NS_LCM_OP_OCC_URI + '/fail'},
                'cancel': {'href': NS_LCM_OP_OCC_URI + '/cancel'}
            }  # json.loads(lcm_op.links)
        }
        return resp_data

    def query_single_ns_lcm_op_occ(self):
        lcm_op = NSLcmOpOccModel.objects.filter(id=self.ns_lcm_op_occ_id)
        if not lcm_op.exists():
            raise NSLCMException('LCM Operation Occurance does not exist')
        resp_data = self.fill_resp_data(lcm_op[0])
        return resp_data
