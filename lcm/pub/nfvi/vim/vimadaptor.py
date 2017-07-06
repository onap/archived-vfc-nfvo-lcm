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

import logging
import sys
import traceback

from requests import RequestException

from lcm.pub.nfvi.vim.lib.syscomm import fun_name
from lcm.pub.nfvi.vim import const
from lcm.pub.nfvi.vim.lib.vimexception import VimException

logger = logging.getLogger(__name__)


class VimAdaptor:
    def __init__(self, connectInfo):
        logger.info("[VimAdaptor]connectInfo=%s" % connectInfo)
        self.apiImpl, self.authInfo = None, [1, "No auth info"]
        self.create_api(connectInfo)
        self.force_login(connectInfo)

    def create_api(self, connectInfo):
        vimtype = connectInfo['vimtype'] if 'vimtype' in connectInfo else None
        logger.info("call %s, vimtype=%s" % (fun_name(), vimtype))
        if vimtype == const.VIM_OPENSTACK:
            from lcm.pub.nfvi.vim.api.openstack.api import OpenstackApi
            self.apiImpl = OpenstackApi()
        elif vimtype == const.VIM_VMWARE:
            from lcm.pub.nfvi.vim.api.multivim.api import MultiVimApi
            self.apiImpl = MultiVimApi()
        else:
            self.authInfo = [1, "Unsupported vimtype(%s)" % vimtype]

    def api_call(self, funname, fun, *args):
        logger.info("call %s%s" % (funname, str(args)))
        ret = None
        try:
            ret = fun(self.authInfo[1], *args) if self.authInfo[0] == 0 else self.authInfo
        except VimException as e:
            ret = [1, e.message]
        except RequestException as e:
            logger.error("request=%s, url=%s" % (e.request.headers._store, e.request.url))
            logger.error(traceback.format_exc())
            ret = [1, e.message if e.message else str(sys.exc_info())]
        except Exception as ex:
            logger.error(traceback.format_exc())
            ret = [1, ex.message if ex.message else str(sys.exc_info())]
        except:
            logger.error(traceback.format_exc())
            ret = [1, str(sys.exc_info())]
        logger.info("[%s]ret=%s" % (funname, ret))
        return ret

    def force_login(self, connectInfo):
        if self.apiImpl:
            logger.info("call %s(%s)" % (fun_name(), connectInfo))
            try:
                self.authInfo = self.apiImpl.login(connectInfo)
            except VimException as e:
                self.authInfo = [1, e.message]
            except Exception as ex:
                logger.error(traceback.format_exc())
                logger.error(str(sys.exc_info()))
                self.authInfo = [1, ex.message if ex.message else str(sys.exc_info())]
            except:
                logger.error(traceback.format_exc())
                self.authInfo = [1, str(sys.exc_info())]
            logger.info("self.authInfo=%s" % self.authInfo)

    def query_net(self, net_id):
        return self.api_call(fun_name(), self.apiImpl.query_net, net_id)

    def query_nets(self):
        return self.api_call(fun_name(), self.apiImpl.query_nets)

    def query_subnet(self, subnet_id):
        return self.api_call(fun_name(), self.apiImpl.query_subnet, subnet_id)

    def query_port(self, port_id):
        return self.api_call(fun_name(), self.apiImpl.query_port, port_id)

    def create_image(self, data):
        return self.api_call(fun_name(), self.apiImpl.create_image, data)

    def get_image(self, image_id):
        return self.api_call(fun_name(), self.apiImpl.get_image, image_id)

    def get_images(self):
        return self.api_call(fun_name(), self.apiImpl.get_images)

    def delete_image(self, image_id):
        return self.api_call(fun_name(), self.apiImpl.delete_image, image_id)

    def create_network(self, data):
        return self.api_call(fun_name(), self.apiImpl.create_network, data)

    def delete_network(self, network_id):
        return self.api_call(fun_name(), self.apiImpl.delete_network, network_id)

    def delete_subnet(self, subnet_id):
        return self.api_call(fun_name(), self.apiImpl.delete_subnet, subnet_id)

    def create_port(self, data):
        return self.api_call(fun_name(), self.apiImpl.create_port, data)

    def delete_port(self, port_id):
        return self.api_call(fun_name(), self.apiImpl.delete_port, port_id)
