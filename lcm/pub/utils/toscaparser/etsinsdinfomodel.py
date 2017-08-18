from lcm.pub.utils.toscaparser.baseinfomodel import BaseInfoModel


class EtsiNsdInfoModel(BaseInfoModel):

    def __init__(self, path, params):
        tosca = self.buildToscaTemplate(path, params)
        self.parseModel(tosca)


    def parseModel(self, tosca):
        pass