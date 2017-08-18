import os
import urllib

from toscaparser.tosca_template import ToscaTemplate

from lcm.pub.utils.toscaparser.dataentityext import DataEntityExt


class BaseInfoModel(object):
    def __init__(self, path, params):
        pass

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
            pass
            # if tosca_tpl != None and hasattr(tosca_tpl, "temp_dir") and os.path.exists(tosca_tpl.temp_dir):
            #     try:
            #         shutil.rmtree(tosca_tpl.temp_dir)
            #     except Exception, e:
            #         pass
            #         # if tosca_tpl != None and tosca_tpl.temp_dir != None and os.path.exists(tosca_tpl.temp_dir):
            #         #     try:
            #         #         shutil.rmtree(tosca_tpl.temp_dir)
            #         #     except Exception, e:
            #         #         pass

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
