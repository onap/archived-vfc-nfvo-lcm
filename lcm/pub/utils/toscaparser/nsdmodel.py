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
        self.vls = self.get_all_vl(nodeTemplates)
        self.cps = self.get_all_cp(nodeTemplates)
        self.routers = self.get_all_router(nodeTemplates)
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

    def get_all_vl(self, nodeTemplates):
        vls = []
        for node in nodeTemplates:
            if self.isVl(node):
                vl = {}
                vl['vl_id'] = node['name']
                vl['description'] = node['description']
                vl['properties'] = node['properties']
                vl['route_external'] = False
                vl['route_id'] = self._get_vl_route_id(node)
                vls.append(vl)
            if self._isExternalVL(node):
                vl = {}
                vl['vl_id'] = node['name']
                vl['description'] = node['description']
                vl['properties'] = node['properties']
                vl['route_external'] = True
                vls.append(vl)
        return vls

    def _get_vl_route_id(self, node):
        route_ids = map(lambda x: self.get_requirement_node_name(x),
                        self.getRequirementByName(node, 'virtual_route'))
        if len(route_ids) > 0:
            return route_ids[0]
        return ""

    def _isExternalVL(self, node):
        return node['nodeType'].upper().find('.ROUTEEXTERNALVL') >= 0

    def get_all_cp(self, nodeTemplates):
        cps = []
        for node in nodeTemplates:
            if self.isCp(node):
                cp = {}
                cp['cp_id'] = node['name']
                cp['cpd_id'] = node['name']
                cp['description'] = node['description']
                cp['properties'] = node['properties']
                cp['vl_id'] = self.get_node_vl_id(node)
                binding_node_ids = map(lambda x: self.get_requirement_node_name(x), self.getVirtualbindings(node))
                #                 cp['vnf_id'] = self._filter_vnf_id(binding_node_ids, nodeTemplates)
                cp['pnf_id'] = self._filter_pnf_id(binding_node_ids, nodeTemplates)
                vls = self.buil_cp_vls(node)
                if len(vls) > 1:
                    cp['vls'] = vls
                cps.append(cp)
        return cps

    def buil_cp_vls(self, node):
        return map(lambda x: self._build_cp_vl(x), self.getVirtualLinks(node))

    def _build_cp_vl(self, req):
        cp_vl = {}
        cp_vl['vl_id'] = self.get_prop_from_obj(req, 'node')
        relationship = self.get_prop_from_obj(req, 'relationship')
        if relationship != None:
            properties = self.get_prop_from_obj(relationship, 'properties')
            if properties != None and isinstance(properties, dict):
                for key, value in properties.items():
                    cp_vl[key] = value
        return cp_vl

    def _filter_pnf_id(self, node_ids, node_templates):
        for node_id in node_ids:
            node = self.get_node_by_name(node_templates, node_id)
            if self.isPnf(node):
                return node_id
        return ""

    def get_all_router(self, nodeTemplates):
        rets = []
        for node in nodeTemplates:
            if self._isRouter(node):
                ret = {}
                ret['router_id'] = node['name']
                ret['description'] = node['description']
                ret['properties'] = node['properties']
                ret['external_vl_id'] = self._get_router_external_vl_id(node)
                ret['external_ip_addresses'] = self._get_external_ip_addresses(node)

                rets.append(ret)
        return rets

    def _isRouter(self, node):
        return node['nodeType'].upper().find('.ROUTER.') >= 0 or node['nodeType'].upper().endswith('.ROUTER')

    def _get_router_external_vl(self, node):
        return self.getRequirementByName(node, 'external_virtual_link')

    def _get_router_external_vl_id(self, node):
        ids = map(lambda x: self.get_requirement_node_name(x), self._get_router_external_vl(node))
        if len(ids) > 0:
            return ids[0]
        return ""

    def _get_external_ip_addresses(self, node):
        external_vls = self._get_router_external_vl(node)
        if len(external_vls) > 0:
            if 'relationship' in external_vls[0] and 'properties' in external_vls[0]['relationship'] and 'router_ip_address' in external_vls[0]['relationship']['properties']:
                return external_vls[0]['relationship']['properties']['router_ip_address']
        return []