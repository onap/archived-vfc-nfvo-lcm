# Copyright 2017-2018 Intel Corporation.
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
import json

from lcm.pub.database.models import OOFDataModel

logger = logging.getLogger(__name__)


class PlaceVnfs(object):
    def __init__(self, data):
        self.data = data
        self.placements = ""

    def validateCallbackResponse(self):
        if self.data == "":
            logger.error("Error occurred in Homing: OOF Async Callback Response is empty")
            return False
        if self.data.get('requestStatus') == "completed":
            if self.data.get("solutions").get("placementSolutions") is not None:
                self.placements = self.data.get("solutions").get("placementSolutions")
                logger.debug("Got placement solutions in OOF Async Callback response")
                return True
            else:
                logger.error("Error occurred in Homing: OOF Async Callback Response "
                             "does not contain placement solution")
                return False
        else:
            if self.data.get("statusMessage"):
                logger.error(
                    "Error occurred in Homing: Request has not been completed, the request status is %s, "
                    "the status message is %s" % (self.data.get('requestStatus'), self.data.get("statusMessage")))
            else:
                logger.error(
                    "Error occurred in Homing: Request has not been completed, the request status is %s, "
                    % self.data.get('requestStatus'))
            return False

    def extract(self):
        params = ["locationId", "vimId", "oofDirectives"]
        vim_info = {}
        if not self.validateCallbackResponse():
            logger.error("OOF request Failed")
            self.update_response_to_db(self.data.get("requestId"), self.data.get("transactionId"),
                                       self.data.get("requestStatus"), "none", "none", "none", "none")
            return
        if self.placements == [] or self.placements == [[]]:
            logger.debug("No solution found for request %s " % self.data.get("requestId"))
            self.update_response_to_db(self.data.get("requestId"), self.data.get("transactionId"),
                                       self.data.get("requestStatus"), "no-solution", "no-solution",
                                       "no-solution", "no-solution")
            return
        for item in self.placements:
            if not isinstance(item, list):
                self.update_response_to_db(self.data.get("requestId"), self.data.get("transactionId"),
                                           self.data.get("requestStatus"), "no-solution", "no-solution",
                                           "no-solution", "no-solution")
                continue
            for placement in item:
                assignmentInfo = placement.get("assignmentInfo")
                if not assignmentInfo:
                    logger.debug(
                        "No assignment info inside Homing response for request %s" % self.data.get(
                            "requestId"))
                    self.update_response_to_db(self.data.get("requestId"),
                                               self.data.get("transactionId"),
                                               self.data.get("requestStatus"), "none", "none", "none",
                                               "none")
                    continue
                for info in assignmentInfo:
                    if info.get("key") in params:
                        vim_info[info.get("key")] = info.get("value")
                    if not vim_info.get("oofDirectives"):
                        logger.warn("Missing flavor info as no directive found in response")
                        self.update_response_to_db(self.data.get("requestId"),
                                                   self.data.get("transactionId"),
                                                   self.data.get("requestStatus"), "none", "none",
                                                   "none", "none")
                        continue
                    vduinfo = self.get_info_from_directives(
                        vim_info['oofDirectives'])
                    if not vduinfo:
                        self.update_response_to_db(self.data.get("requestId"),
                                                   self.data.get("transactionId"),
                                                   self.data.get("requestStatus"), "none", "none",
                                                   "none", "none")
                        return
                    else:
                        self.update_response_to_db(requestId=self.data.get("requestId"),
                                                   transactionId=self.data.get("transactionId"),
                                                   requestStatus=self.data.get("requestStatus"),
                                                   vimId=vim_info['vimId'],
                                                   cloudOwner=placement.get("solution").get("cloudOwner"),
                                                   cloudRegionId=vim_info['locationId'],
                                                   vduInfo=vduinfo
                                                   )
                        logger.debug(
                            "Placement solution has been stored for request %s "
                            % self.data.get("requestId"))
                        return "Done"

    def get_info_from_directives(self, directives):
        vduinfo = []
        for directive in directives.get("directives"):
            if directive.get("type") == "tocsa.nodes.nfv.Vdu.Compute":
                vdu = {"vduName": directive.get("id")}
                other_directives = []
                for item in directive.get("directives"):
                    if item.get("type") == "flavor_directive":
                        for attribute in item.get("attributes"):
                            vdu['flavorName'] = attribute.get("attribute_value")
                    else:
                        other_directives.append(item)
                if other_directives:
                    other_directives = json.dumps(other_directives)
                vdu['directive'] = other_directives
                vduinfo.append(vdu)
            else:
                logger.warn("Find unrecognized type %s " % directive.get("type"))
        if vduinfo:
            vduinfo = json.dumps(vduinfo)
            return vduinfo
        else:
            logger.warn("No OOF directive for VDU")
            return None

    def update_response_to_db(self, requestId, transactionId, requestStatus, vimId, cloudOwner,
                              cloudRegionId, vduInfo):
        OOFDataModel.objects.filter(request_id=requestId,
                                    transaction_id=transactionId).update(
            request_status=requestStatus,
            vim_id=vimId,
            cloud_owner=cloudOwner,
            cloud_region_id=cloudRegionId,
            vdu_info=vduInfo
        )
