import functools

from lcm.pub.utils.toscaparser.basemodel import BaseInfoModel


class EtsiNsdInfoModel(BaseInfoModel):

    def __init__(self, path, params):
        tosca = self.buildToscaTemplate(path, params)
        self.parseModel(tosca)

    def parseModel(self, tosca):
        self.buidMetadata(tosca)
        if hasattr(tosca, 'topology_template') and hasattr(tosca.topology_template, 'inputs'):
            self.inputs = self.buildInputs(tosca.topology_template.inputs)

        nodeTemplates = map(functools.partial(self.buildNode, inputs=tosca.inputs, parsed_params=tosca.parsed_params),
                            tosca.nodetemplates)

        self.vnfs = self._get_all_vnf(nodeTemplates)
        self.pnfs = self._get_all_pnf(nodeTemplates)
        # self.vls = self.get_all_vl(nodeTemplates)
        # self.cps = self.get_all_cp(nodeTemplates)
        # self.routers = self.get_all_router(nodeTemplates)
        # self.fps = self._get_all_fp(nodeTemplates)
        # self.vnffgs = self._get_all_vnffg(tosca.topology_template.groups)
        # self.server_groups = self.get_all_server_group(tosca.topology_template.groups)
        # self.ns_exposed = self.get_all_endpoint_exposed(tosca.topology_template)
        # self.policies = self._get_policies_scaling(tosca.topology_template.policies)
        # self.ns_flavours = self.get_all_flavour(tosca.topology_template.groups)
        # self.nested_ns = self.get_all_nested_ns(nodeTemplates)

    def buildInputs(self, top_inputs):
        ret = {}
        for tmpinput in top_inputs:
            tmp = {}
            tmp['type'] = tmpinput.type
            tmp['description'] = tmpinput.description
            tmp['default'] = tmpinput.default

            ret[tmpinput.name] = tmp
        return ret

    def buildNode(self, nodeTemplate, inputs, parsed_params):
        ret ={}
        ret['name'] = nodeTemplate.name
        ret['nodeType'] = nodeTemplate.type
        if 'description' in nodeTemplate.entity_tpl:
            ret['description'] = nodeTemplate.entity_tpl['description']
        else:
            ret['description'] = ''
        props = self.buildProperties(nodeTemplate, parsed_params)
        ret['properties'] = self.verify_properties(props, inputs, parsed_params)
        ret['requirements'] = self.build_requirements(nodeTemplate)
        self.buildCapabilities(nodeTemplate, inputs, ret)
        self.buildArtifacts(nodeTemplate, inputs, ret)
        interfaces = self.build_interfaces(nodeTemplate)
        if interfaces: ret['interfaces'] = interfaces
        return ret

    def _get_all_vnf(self, nodeTemplates):
        vnfs = []
        for node in nodeTemplates:
            if self.isVnf(node):
                vnf = {}
                vnf['vnf_id'] = node['name']
                vnf['description'] = node['description']
                vnf['properties'] = node['properties']
                vnf['dependencies'] = map(lambda x: self.get_requirement_node_name(x), self.getNodeDependencys(node))
                vnf['networks'] = self.get_networks(node)

                vnfs.append(vnf)
        return vnfs

    def _get_all_pnf(self, nodeTemplates):
        pnfs = []
        for node in nodeTemplates:
            if self.isPnf(node):
                pnf = {}
                pnf['pnf_id'] = node['name']
                pnf['description'] = node['description']
                pnf['properties'] = node['properties']
                pnf['cps'] = self.getVirtalBindingCpIds(node, nodeTemplates)

                pnfs.append(pnf)
        return pnfs

    def getVirtalBindingCpIds(self, node, nodeTemplates):
        return map(lambda x: x['name'], self.getVirtalBindingCps(node, nodeTemplates))

    def getVirtalBindingCps(self, node, nodeTemplates):
        cps = []
        for tmpnode in nodeTemplates:
            if 'requirements' in tmpnode:
                for item in tmpnode['requirements']:
                    for key, value in item.items():
                        if key.upper().startswith('VIRTUALBINDING'):
                            req_node_name = self.get_requirement_node_name(value)
                            if req_node_name != None and req_node_name == node['name']:
                                cps.append(tmpnode)
        return cps