import functools

from lcm.pub.utils.toscaparser import EtsiNsdInfoModel


class EtsiVnfdInfoModel(EtsiNsdInfoModel):

    def __init__(self, path, params):
        super(EtsiVnfdInfoModel, self).__init__(path, params)

    def parseModel(self, tosca):
        self.buidMetadata(tosca)
        if hasattr(tosca, 'topology_template') and hasattr(tosca.topology_template, 'inputs'):
            self.inputs = self.buildInputs(tosca.topology_template.inputs)

        nodeTemplates = map(functools.partial(self.buildNode, inputs=tosca.inputs, parsed_params=tosca.parsed_params),
                            tosca.nodetemplates)

        self.services = self._get_all_services(nodeTemplates)
        self.vcloud = self._get_all_vcloud(nodeTemplates)


    def _get_all_services(self, nodeTemplates):
        ret = []
        for node in nodeTemplates:
            if self.isService(node):
                service = {}
                service['serviceId'] = node['name']
                if 'description' in node:
                    service['description'] = node['description']
                service['properties'] = node['properties']
                service['dependencies'] = map(lambda x: self.get_requirement_node_name(x),
                                              self.getNodeDependencys(node))
                service['networks'] = map(lambda x: self.get_requirement_node_name(x), self.getVirtualLinks(node))

                ret.append(service)
        return ret

    def _get_all_vcloud(self, nodeTemplates):
        rets = []
        for node in nodeTemplates:
            if self._isVcloud(node):
                ret = {}
                if 'vdc_name' in node['properties']:
                    ret['vdc_name'] = node['properties']['vdc_name']
                else:
                    ret['vdc_name'] = ""
                if 'storage_clusters' in node['properties']:
                    ret['storage_clusters'] = node['properties']['storage_clusters']
                else:
                    ret['storage_clusters'] = []

                rets.append(ret)
        return rets

    def _isVcloud(self, node):
        return node['nodeType'].upper().find('.VCLOUD.') >= 0 or node['nodeType'].upper().endswith('.VCLOUD')