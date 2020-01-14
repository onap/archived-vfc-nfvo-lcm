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

import base64
import sys
import traceback
import logging
import urllib.request
import urllib.error
import urllib.parse
import uuid
import httplib2
import requests

from lcm.pub.config.config import MSB_SERVICE_IP, MSB_SERVICE_PORT

rest_no_auth, rest_oneway_auth, rest_bothway_auth = 0, 1, 2
HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_202_ACCEPTED = '200', '201', '204', '202'
status_ok_list = [HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_202_ACCEPTED]
HTTP_404_NOTFOUND, HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED, HTTP_400_BADREQUEST = '404', '403', '401', '400'

logger = logging.getLogger(__name__)


def call_req(base_url, user, passwd, auth_type, resource, method, content='', additional_headers={}):
    callid = str(uuid.uuid1())
    logger.debug("[%s]call_req('%s','%s','%s',%s,'%s','%s','%s')" % (
        callid, base_url, user, passwd, auth_type, resource, method, content))
    ret = None
    resp_Location = ''
    resp_status = ''
    try:
        full_url = combine_url(base_url, resource)
        headers = {'content-type': 'application/json', 'accept': 'application/json'}
        if user:
            headers['Authorization'] = 'Basic %s' % base64.b64encode(bytes('%s:%s' % (user, passwd), "utf-8")).decode()
        ca_certs = None
        if additional_headers:
            headers.update(additional_headers)
        for retry_times in range(3):
            http = httplib2.Http(ca_certs=ca_certs, disable_ssl_certificate_validation=(auth_type == rest_no_auth))
            http.follow_all_redirects = True
            try:
                resp, resp_content = http.request(full_url, method=method.upper(), body=content, headers=headers)
                resp_status, resp_body = resp['status'], resp_content
                resp_Location = resp.get('Location', "")
                logger.debug("[%s][%d]status=%s)" % (callid, retry_times, resp_status))
                if headers['accept'] == 'application/json':
                    resp_body = resp_content.decode('UTF-8')
                    logger.debug("resp_body=%s", resp_body)
                if resp_status in status_ok_list:
                    ret = [0, resp_body, resp_status, resp_Location]
                else:
                    ret = [1, resp_body, resp_status, resp_Location]
                break
            except Exception as ex:
                if 'httplib.ResponseNotReady' in str(sys.exc_info()):
                    logger.debug("retry_times=%d", retry_times)
                    logger.error(traceback.format_exc())
                    ret = [1, "Unable to connect to %s" % full_url, resp_status, resp_Location]
                    continue
                raise ex
    except urllib.error.URLError as err:
        ret = [2, str(err), resp_status, resp_Location]
    except Exception as ex:
        logger.error(traceback.format_exc())
        logger.error("[%s]ret=%s" % (callid, str(sys.exc_info())))
        res_info = str(sys.exc_info())
        if 'httplib.ResponseNotReady' in res_info:
            res_info = "The URL[%s] request failed or is not responding." % full_url
        ret = [3, res_info, resp_status, resp_Location]
    except:
        logger.error(traceback.format_exc())
        ret = [4, str(sys.exc_info()), resp_status, resp_Location]

    logger.debug("[%s]ret=%s" % (callid, str(ret)))
    return ret


def req_by_msb(resource, method, content=''):
    logger.debug("resource: %s, method: %s, content: %s" % (resource, method, content))
    base_url = "https://%s:%s/" % (MSB_SERVICE_IP, MSB_SERVICE_PORT)
    return call_req(base_url, "", "", rest_no_auth, resource, method, content)


def upload_by_msb(resource, method, file_data):
    headers = {'accept': 'application/json'}
    full_url = "https://%s:%s/%s" % (MSB_SERVICE_IP, MSB_SERVICE_PORT, resource)
    r = requests.post(full_url, files=file_data, headers=headers)
    resp_status, resp_body = str(r.status_code), r.text
    if resp_status not in status_ok_list:
        logger.error("Status code is %s, detail is %s.", resp_status, resp_body)
        return [1, "Failed to upload file.", resp_status]
    logger.debug("resp_body=%s", resp_body)
    return [0, resp_body, resp_status]


def combine_url(base_url, resource):
    full_url = None
    if base_url.endswith('/') and resource.startswith('/'):
        full_url = base_url[:-1] + resource
    elif base_url.endswith('/') and not resource.startswith('/'):
        full_url = base_url + resource
    elif not base_url.endswith('/') and resource.startswith('/'):
        full_url = base_url + resource
    else:
        full_url = base_url + '/' + resource
    return full_url
