# Copyright 2017 ZTE Corporation.
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

import copy
import ftplib
import json
import os
import re
import shutil
import urllib

import paramiko
from toscaparser.functions import GetInput
from toscaparser.tosca_template import ToscaTemplate

from lcm.pub.utils.toscaparser.dataentityext import DataEntityExt


class BaseInfoModel(object):

    def buildToscaTemplate(self, path, params):
        file_name = None
        try:
            file_name = self._check_download_file(path)
            valid_params = self._validate_input_params(file_name, params)
            return self._create_tosca_template(file_name, valid_params)
        finally:
            if file_name != None and file_name != path and os.path.exists(file_name):
                try:
                    os.remove(file_name)
                except Exception, e:
                    pass

    def _validate_input_params(self, path, params):
        valid_params = {}
        if params and len(params) > 0:
            tmp = self._create_tosca_template(path, None)
            for key,value in params.items():
                if hasattr(tmp, 'inputs') and len(tmp.inputs) > 0:
                    for input_def in tmp.inputs:
                        if (input_def.name == key):
                            valid_params[key] = DataEntityExt.validate_datatype(input_def.type, value)

        return valid_params

    def _create_tosca_template(self, file_name, valid_params):
        tosca_tpl = None
        try:
            tosca_tpl = ToscaTemplate(file_name, valid_params)
            print "-----------------------------"
            print '\n'.join(['%s:%s' % item for item in tosca_tpl.__dict__.items()])
            print "-----------------------------"
            return tosca_tpl
        finally:
            if tosca_tpl != None and hasattr(tosca_tpl, "temp_dir") and os.path.exists(tosca_tpl.temp_dir):
                try:
                    shutil.rmtree(tosca_tpl.temp_dir)
                except Exception, e:
                    pass

    def _check_download_file(self, path):
        if (path.startswith("ftp") or path.startswith("sftp")):
            return self.downloadFileFromFtpServer(path)
        elif (path.startswith("http")):
            return self.download_file_from_httpserver(path)
        return path

    def download_file_from_httpserver(self, path):
        path = path.encode("utf-8")
        tmps = str.split(path, '/')
        localFileName = tmps[len(tmps) - 1]
        urllib.urlretrieve(path, localFileName)
        return localFileName

    def downloadFileFromFtpServer(self, path):
        path = path.encode("utf-8")
        tmp = str.split(path, '://')
        protocol = tmp[0]
        tmp = str.split(tmp[1], ':')
        if len(tmp) == 2:
            userName = tmp[0]
            tmp = str.split(tmp[1], '@')
            userPwd = tmp[0]
            index = tmp[1].index('/')
            hostIp = tmp[1][0:index]
            remoteFileName = tmp[1][index:len(tmp[1])]
            if protocol.lower() == 'ftp':
                hostPort = 21
            else:
                hostPort = 22

        if len(tmp) == 3:
            userName = tmp[0]
            userPwd = str.split(tmp[1], '@')[0]
            hostIp = str.split(tmp[1], '@')[1]
            index = tmp[2].index('/')
            hostPort = tmp[2][0:index]
            remoteFileName = tmp[2][index:len(tmp[2])]

        localFileName = str.split(remoteFileName, '/')
        localFileName = localFileName[len(localFileName) - 1]

        if protocol.lower() == 'sftp':
            self.sftp_get(userName, userPwd, hostIp, hostPort, remoteFileName, localFileName)
        else:
            self.ftp_get(userName, userPwd, hostIp, hostPort, remoteFileName, localFileName)
        return localFileName

    def sftp_get(self, userName, userPwd, hostIp, hostPort, remoteFileName, localFileName):
        # return
        t = None
        try:
            t = paramiko.Transport(hostIp, int(hostPort))
            t.connect(username=userName, password=userPwd)
            sftp = paramiko.SFTPClient.from_transport(t)
            sftp.get(remoteFileName, localFileName)
        finally:
            if t != None:
                t.close()


    def ftp_get(self, userName, userPwd, hostIp, hostPort, remoteFileName, localFileName):
        f = None
        try:
            ftp = ftplib.FTP()
            ftp.connect(hostIp, hostPort)
            ftp.login(userName, userPwd)
            f = open(localFileName, 'wb')
            ftp.retrbinary('RETR ' + remoteFileName, f.write, 1024)
            f.close()
        finally:
            if f != None:
                f.close()

    def buidMetadata(self, tosca):
        if 'metadata' in tosca.tpl:
            self.metadata = copy.deepcopy(tosca.tpl['metadata'])

    def buildProperties(self, nodeTemplate, parsed_params):
        properties = {}
        isMappingParams = parsed_params and len(parsed_params) > 0
        for k, item in nodeTemplate.get_properties().items():
            properties[k] = item.value
            if isinstance(item.value, GetInput):
                if item.value.result() and isMappingParams:
                    properties[k] = DataEntityExt.validate_datatype(item.type, item.value.result())
                else:
                    tmp = {}
                    tmp[item.value.name] = item.value.input_name
                    properties[k] = tmp
        if 'attributes' in nodeTemplate.entity_tpl:
            for k, item in nodeTemplate.entity_tpl['attributes'].items():
                properties[k] = str(item)
        return properties


    def verify_properties(self, props, inputs, parsed_params):
        ret_props = {}
        if (props and len(props) > 0):
            for key, value in props.items():
                ret_props[key] = self._verify_value(value, inputs, parsed_params)
                #                 if isinstance(value, str):
                #                     ret_props[key] = self._verify_string(inputs, parsed_params, value);
                #                     continue
                #                 if isinstance(value, list):
                #                     ret_props[key] = map(lambda x: self._verify_dict(inputs, parsed_params, x), value)
                #                     continue
                #                 if isinstance(value, dict):
                #                     ret_props[key] = self._verify_map(inputs, parsed_params, value)
                #                     continue
                #                 ret_props[key] = value
        return ret_props

    def build_requirements(self, node_template):
        rets = []
        for req in node_template.requirements:
            for req_name, req_value in req.items():
                if (isinstance(req_value, dict)):
                    if ('node' in req_value and req_value['node'] not in node_template.templates):
                        continue  # No target requirement for aria parser, not add to result.
                rets.append({req_name : req_value})
        return rets

    def buildCapabilities(self, nodeTemplate, inputs, ret):
        capabilities = json.dumps(nodeTemplate.entity_tpl.get('capabilities', None))
        match = re.findall(r'\{"get_input":\s*"([\w|\-]+)"\}',capabilities)
        for m in match:
            aa= [input_def for input_def in inputs
                 if m == input_def.name][0]
            capabilities = re.sub(r'\{"get_input":\s*"([\w|\-]+)"\}', json.dumps(aa.default), capabilities,1)
        if capabilities != 'null':
            ret['capabilities'] = json.loads(capabilities)

    def buildArtifacts(self, nodeTemplate, inputs, ret):
        artifacts = json.dumps(nodeTemplate.entity_tpl.get('artifacts', None))
        match = re.findall(r'\{"get_input":\s*"([\w|\-]+)"\}',artifacts)
        for m in match:
            aa= [input_def for input_def in inputs
                 if m == input_def.name][0]
            artifacts = re.sub(r'\{"get_input":\s*"([\w|\-]+)"\}', json.dumps(aa.default), artifacts,1)
        if artifacts != 'null':
            ret['artifacts'] = json.loads(artifacts)

    def build_interfaces(self, node_template):
        if 'interfaces' in node_template.entity_tpl:
            return node_template.entity_tpl['interfaces']
        return None

    def isVnf(self, node):
        return node['nodeType'].upper().find('.VNF.') >= 0 or node['nodeType'].upper().endswith('.VNF')

    def isPnf(self, node):
        return node['nodeType'].upper().find('.PNF.') >= 0 or node['nodeType'].upper().endswith('.PNF')

    def isCp(self, node):
        return node['nodeType'].upper().find('.CP.') >= 0 or node['nodeType'].upper().endswith('.CP')

    def isVl(self, node):
        return node['nodeType'].upper().find('.VIRTUALLINK.') >= 0 or node['nodeType'].upper().find('.VL.') >= 0 or \
               node['nodeType'].upper().endswith('.VIRTUALLINK') or node['nodeType'].upper().endswith('.VL')

    def isService(self, node):
        return node['nodeType'].upper().find('.SERVICE.') >= 0 or node['nodeType'].upper().endswith('.SERVICE')

    def get_requirement_node_name(self, req_value):
        return self.get_prop_from_obj(req_value, 'node')

    def get_prop_from_obj(self, obj, prop):
        if isinstance(obj, str):
            return obj
        if (isinstance(obj, dict) and prop in obj):
            return obj[prop]
        return None

    def getNodeDependencys(self, node):
        return self.getRequirementByName(node, 'dependency')

    def getVirtualLinks(self, node):
        return self.getRequirementByName(node, 'virtualLink')

    def getVirtualbindings(self, node):
        return self.getRequirementByName(node, 'virtualbinding')


    def getRequirementByName(self, node, requirementName):
        requirements = []
        if 'requirements' in node:
            for item in node['requirements']:
                for key, value in item.items():
                    if key == requirementName:
                        requirements.append(value)
        return requirements

    def get_networks(self, node):
        rets = []
        if 'requirements' in node:
            for item in node['requirements']:
                for key, value in item.items():
                    if key.upper().find('VIRTUALLINK') >=0:
                        rets.append({"key_name":key, "vl_id":self.get_requirement_node_name(value)})
        return rets

    def _verify_value(self, value, inputs, parsed_params):
        if isinstance(value, str):
            return self._verify_string(inputs, parsed_params, value)
        if isinstance(value, list) or isinstance(value, dict):
            return self._verify_object(value, inputs, parsed_params)
        return value

    def _verify_object(self, value, inputs, parsed_params):
        s = self._verify_string(inputs, parsed_params, json.dumps(value))
        return json.loads(s)

    def _get_input_name(self, getInput):
        input_name = getInput.split(':')[1]
        input_name = input_name.strip()
        return input_name.replace('"', '').replace('}', '')

    def _verify_string(self, inputs, parsed_params, value):
        getInputs = re.findall(r'{"get_input": "[a-zA-Z_0-9]+"}', value)
        for getInput in getInputs:
            input_name = self._get_input_name(getInput)
            if parsed_params and input_name in parsed_params:
                value = value.replace(getInput, json.dumps(parsed_params[input_name]))
            else:
                for input_def in inputs:
                    if input_def.default and input_name == input_def.name:
                        value = value.replace(getInput, json.dumps(input_def.default))
        return value

    def get_node_vl_id(self, node):
        vl_ids = map(lambda x: self.get_requirement_node_name(x), self.getVirtualLinks(node))
        if len(vl_ids) > 0:
            return vl_ids[0]
        return ""

    def get_node_by_name(self, node_templates, name):
        for node in node_templates:
            if node['name'] == name:
                return node
        return None

    def get_all_nested_ns(self, nodes):
        nss = []
        for node in nodes:
            if self.is_nested_ns(node):
                ns = {}
                ns['ns_id'] = node['name']
                ns['description'] = node['description']
                ns['properties'] = node['properties']
                ns['networks'] = self.get_networks(node)

                nss.append(ns)
        return nss

    def is_nested_ns(self, node):
        return node['nodeType'].upper().find('.NS.') >= 0 or node['nodeType'].upper().endswith('.NS')
