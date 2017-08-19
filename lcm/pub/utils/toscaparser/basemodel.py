import copy
import os
import shutil
import urllib

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