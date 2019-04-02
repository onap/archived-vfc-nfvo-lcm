# Copyright 2019 ZTE Corporation.
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

import logging
import datetime
import uuid
import json

from lcm.pub.database.models import NSLcmOpOccModel
from lcm.pub.utils.values import update_value


logger = logging.getLogger(__name__)


class NsLcmOpOcc(object):
    @staticmethod
    def create(nsInstanceId, lcmOperationType, operationState, isAutomaticInvocation, operationParams):
        logger.debug("lcm_op_occ(%s,%s,%s,%s,%s) create begin." % (nsInstanceId, lcmOperationType, operationState, isAutomaticInvocation, operationParams))
        cur_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        lcm_op_occ = NSLcmOpOccModel.objects.create(
            id=str(uuid.uuid4()),
            operation_state=operationState,
            state_entered_time=cur_time,
            start_time=cur_time,
            ns_instance_id=nsInstanceId,
            operation=lcmOperationType,
            is_automatic_invocation=isAutomaticInvocation,
            # operation_params=operationParams,
            operation_params=json.dumps(operationParams),
            is_cancel_pending=False
        )
        logger.debug("lcm_op_occ(%s) create successfully." % lcm_op_occ.id)
        return lcm_op_occ.id

    @staticmethod
    def update(occ_id, operationState=None, isCancelPending=None, cancelMode=None, error=None, resourceChanges=None):
        lcm_op_occ = NSLcmOpOccModel.objects.get(id=occ_id)
        if operationState:
            lcm_op_occ.operation_state = operationState
            lcm_op_occ.state_entered_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if isCancelPending:
            lcm_op_occ.is_cancel_pending = isCancelPending
        if cancelMode:
            lcm_op_occ.cancel_mode = cancelMode
        if error:
            lcm_op_occ.error = error
        if resourceChanges:
            lcm_op_occ.resource_changes = update_value(lcm_op_occ.resourceChanges if lcm_op_occ.resourceChanges else {}, resourceChanges)
        lcm_op_occ.save()
        logger.debug("lcm_op_occ(%s) update successfully." % lcm_op_occ.id)
        return lcm_op_occ.id
