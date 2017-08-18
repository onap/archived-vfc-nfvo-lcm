from lcm.pub.utils.toscaparser import EtsiNsdInfoModel


class EtsiVnfdInfoModel(EtsiNsdInfoModel):

    def __init__(self, path, params):
        super(EtsiVnfdInfoModel, self).__init__(path, params)
