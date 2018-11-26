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
from lcm.pub.utils import values

logger = logging.getLogger(__name__)


class PlaceVnfs(object):
    def __init__(self, data):
        self.data = data
        self.placements = ""
        self.request_id = data.get("requestId")

    def validateCallbackResponse(self):
        if self.data == "":
            logger.error("Error occurred in Homing: OOF Async Callback Response is empty")
            return False
        if self.data.get('requestStatus') == "completed" and self.data.get("requestId"):
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
        params = ["locationId", "vimId", "oof_directives", "cloudOwner"]
        vim_info = {}
        if not self.validateCallbackResponse():
            logger.error("OOF request Failed")
            self.update_response_to_db(self.request_id, self.data.get("requestStatus"), "none", "none",
                                       "none", "none")
            return
        if self.placements == [] or self.placements == [[]]:
            logger.debug("No solution found for request %s " % self.request_id)
            self.update_response_to_db(self.request_id, self.data.get("requestStatus"), "none", "none",
                                       "none", "none")
            return
        for item in self.placements:
            if not isinstance(item, list):
                self.update_response_to_db(self.request_id, self.data.get("requestStatus"), "none", "none",
                                           "none", "none")
                continue
            for placement in item:
                assignmentInfo = placement.get("assignmentInfo")
                if not assignmentInfo or not placement.get("solution"):
                    logger.debug(
                        "No assignment info/Solution inside Homing response for request %s"
                        % self.request_id)
                    self.update_response_to_db(self.request_id, self.data.get("requestStatus"), "none", "none",
                                               "none", "none")
                    continue
                for info in assignmentInfo:
                    if info.get("key") in params:
                        vim_info[info.get("key")] = info.get("value")
                if not vim_info.get("oof_directives"):
                    logger.warn("Missing flavor info as no directive found in response")
                    self.update_response_to_db(self.request_id,
                                               self.data.get("requestStatus"), "none", "none",
                                               "none", "none")
                    continue
                vduinfo = self.get_info_from_directives(
                    vim_info['oof_directives'])
                if not vduinfo:
                    self.update_response_to_db(self.request_id,
                                               self.data.get("requestStatus"), "none", "none",
                                               "none", "none")
                    return
                else:
                    cloud_owner = placement.get("solution").get("cloudOwner") \
                        if placement.get("solution").get("cloudOwner") \
                        else vim_info.get("cloudOwner")
                    location_id = vim_info.get("locationId")
                    if not cloud_owner or not location_id:
                        self.update_response_to_db(self.request_id,
                                                   self.data.get("requestStatus"), "none", "none",
                                                   "none", "none")
                        return
                    vim_id = vim_info['vimId'] if vim_info.get('vimId') \
                        else cloud_owner + "_" + location_id
                    self.update_response_to_db(requestId=self.request_id,
                                               requestStatus=self.data.get("requestStatus"),
                                               vimId=vim_id,
                                               cloudOwner=cloud_owner,
                                               cloudRegionId=values.ignore_case_get(vim_info, "locationId"),
                                               vduInfo=vduinfo)
                    logger.debug(
                        "Placement solution has been stored for request %s " % self.request_id)
                    return "Done"

    def get_info_from_directives(self, directives):
        vduinfo = []
        for directive in directives.get("directives"):
            if directive.get("type") == "tosca.nodes.nfv.Vdu.Compute":
                vdu = {"vduName": directive.get("id")}
                other_directives = []
                for item in directive.get("directives"):
                    if item.get("type") == "flavor_directives":
                        for attribute in item.get("attributes"):
                            vdu[attribute.get("attribute_name")] = attribute.get("attribute_value")
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

    def update_response_to_db(self, requestId, requestStatus, vimId, cloudOwner,
                              cloudRegionId, vduInfo):
        OOFDataModel.objects.filter(request_id=requestId).update(
            request_status=requestStatus,
            vim_id=vimId,
            cloud_owner=cloudOwner,
            cloud_region_id=cloudRegionId,
            vdu_info=vduInfo
        )
