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
        self.vcenter = self._get_all_vcenter(nodeTemplates)
        self.image_files = self._get_all_image_file(nodeTemplates)
        self.local_storages = self._get_all_local_storage(nodeTemplates)
        self.volume_storages = self._get_all_volume_storage(nodeTemplates)
        self.vdus = self._get_all_vdu(nodeTemplates)
        self.vls = self.get_all_vl(nodeTemplates)
        self.cps = self.get_all_cp(nodeTemplates)
        self.plugins = self.get_all_plugin(nodeTemplates)
        self.routers = self.get_all_router(nodeTemplates)
        self.server_groups = self.get_all_server_group(tosca.topology_template.groups)
        self.element_groups = self._get_all_element_group(tosca.topology_template.groups)


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

    def _get_all_vcenter(self, nodeTemplates):
        rets = []
        for node in nodeTemplates:
            if self._isVcenter(node):
                ret = {}
                if 'compute_clusters' in node['properties']:
                    ret['compute_clusters'] = node['properties']['compute_clusters']
                else:
                    ret['compute_clusters'] = []
                if 'storage_clusters' in node['properties']:
                    ret['storage_clusters'] = node['properties']['storage_clusters']
                else:
                    ret['storage_clusters'] = []
                if 'network_clusters' in node['properties']:
                    ret['network_clusters'] = node['properties']['network_clusters']
                else:
                    ret['network_clusters'] = []

                rets.append(ret)
        return rets

    def _isVcenter(self, node):
        return node['nodeType'].upper().find('.VCENTER.') >= 0 or node['nodeType'].upper().endswith('.VCENTER')

    def _get_all_image_file(self, nodeTemplates):
        rets = []
        for node in nodeTemplates:
            if self._isImageFile(node):
                ret = {}
                ret['image_file_id'] = node['name']
                if 'description' in node:
                    ret['description'] = node['description']
                ret['properties'] = node['properties']

                rets.append(ret)
        return rets

    def _isImageFile(self, node):
        return node['nodeType'].upper().find('.IMAGEFILE.') >= 0 or node['nodeType'].upper().endswith('.IMAGEFILE')

    def _get_all_local_storage(self, nodeTemplates):
        rets = []
        for node in nodeTemplates:
            if self._isLocalStorage(node):
                ret = {}
                ret['local_storage_id'] = node['name']
                if 'description' in node:
                    ret['description'] = node['description']
                ret['properties'] = node['properties']

                rets.append(ret)
        return rets

    def _isLocalStorage(self, node):
        return node['nodeType'].upper().find('.LOCALSTORAGE.') >= 0 or node['nodeType'].upper().endswith(
            '.LOCALSTORAGE')

    def _get_all_volume_storage(self, nodeTemplates):
        rets = []
        for node in nodeTemplates:
            if self._isVolumeStorage(node):
                ret = {}
                ret['volume_storage_id'] = node['name']
                if 'description' in node:
                    ret['description'] = node['description']
                ret['properties'] = node['properties']
                ret['image_file'] = map(lambda x: self.get_requirement_node_name(x),
                                        self.getRequirementByName(node, 'image_file'))

                rets.append(ret)
        return rets

    def _isVolumeStorage(self, node):
        return node['nodeType'].upper().find('.VOLUMESTORAGE.') >= 0 or node['nodeType'].upper().endswith(
            '.VOLUMESTORAGE')

    def _get_all_vdu(self, nodeTemplates):
        rets = []
        for node in nodeTemplates:
            if self.isVdu(node):
                ret = {}
                ret['vdu_id'] = node['name']
                if 'description' in node:
                    ret['description'] = node['description']
                ret['properties'] = node['properties']
                ret['image_file'] = self.get_node_image_file(node)
                local_storages = self.getRequirementByName(node, 'local_storage')
                ret['local_storages'] = map(lambda x: self.get_requirement_node_name(x), local_storages)
                volume_storages = self.getRequirementByName(node, 'volume_storage')
                ret['volume_storages'] = map(functools.partial(self._trans_volume_storage), volume_storages)
                ret['dependencies'] = map(lambda x: self.get_requirement_node_name(x), self.getNodeDependencys(node))

                nfv_compute = self.getCapabilityByName(node, 'nfv_compute')
                if nfv_compute != None and 'properties' in nfv_compute:
                    ret['nfv_compute'] = nfv_compute['properties']

                ret['vls'] = self.get_linked_vl_ids(node, nodeTemplates)

                scalable = self.getCapabilityByName(node, 'scalable')
                if scalable != None and 'properties' in scalable:
                    ret['scalable'] = scalable['properties']

                ret['cps'] = self.getVirtalBindingCpIds(node, nodeTemplates)
                ret['artifacts'] = self._build_artifacts(node)

                rets.append(ret)
        return rets

    def get_node_image_file(self, node):
        rets = map(lambda x: self.get_requirement_node_name(x), self.getRequirementByName(node, 'guest_os'))
        if len(rets) > 0:
            return rets[0]
        return ""

    def _trans_volume_storage(self, volume_storage):
        if isinstance(volume_storage, str):
            return {"volume_storage_id": volume_storage}
        else:
            ret = {}
            ret['volume_storage_id'] = self.get_requirement_node_name(volume_storage)
            if 'relationship' in volume_storage and 'properties' in volume_storage['relationship']:
                if 'location' in volume_storage['relationship']['properties']:
                    ret['location'] = volume_storage['relationship']['properties']['location']
                if 'device' in volume_storage['relationship']['properties']:
                    ret['device'] = volume_storage['relationship']['properties']['device']

            return ret

    def get_linked_vl_ids(self, node, node_templates):
        vl_ids = []
        cps = self.getVirtalBindingCps(node, node_templates)
        for cp in cps:
            vl_reqs = self.getVirtualLinks(cp)
            for vl_req in vl_reqs:
                vl_ids.append(self.get_requirement_node_name(vl_req))
        return vl_ids

    def _build_artifacts(self, node):
        rets = []
        if 'artifacts' in node and len(node['artifacts']) > 0:
            artifacts = node['artifacts']
            for name, value in artifacts.items():
                ret = {}
                if isinstance(value, dict):
                    ret['artifact_name'] = name
                    ret['type'] = value.get('type', '')
                    ret['file'] = value.get('file', '')
                    ret['repository'] = value.get('repository', '')
                    ret['deploy_path'] = value.get('deploy_path', '')
                else:
                    ret['artifact_name'] = name
                    ret['type'] = ''
                    ret['file'] = value
                    ret['repository'] = ''
                    ret['deploy_path'] = ''
                rets.append(ret)
        return rets

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
                cp['vdu_id'] = self.get_node_vdu_id(node)
                vls = self.buil_cp_vls(node)
                if len(vls) > 1:
                    cp['vls'] = vls
                cps.append(cp)
        return cps

    def get_all_plugin(self, node_templates):
        plugins = []
        for node in node_templates:
            if self._isPlugin(node):
                plugin = {}
                plugin['plugin_id'] = node['name']
                plugin['description'] = node['description']
                plugin['properties'] = node['properties']
                if 'interfaces' in node:
                    plugin['interfaces'] = node['interfaces']

                plugins.append(plugin)
        return plugins

    def _isPlugin(self, node):
        return node['nodeType'].lower().find('.plugin.') >= 0 or node['nodeType'].lower().endswith('.plugin')

    def _get_all_element_group(self, groups):
        rets = []
        for group in groups:
            if self._isVnfdElementGroup(group):
                ret = {}
                ret['group_id'] = group.name
                ret['description'] = group.description
                if 'properties' in group.tpl:
                    ret['properties'] = group.tpl['properties']
                ret['members'] = group.members
                rets.append(ret)
        return rets

    def _isVnfdElementGroup(self, group):
        return group.type.upper().find('.VNFDELEMENTGROUP.') >= 0 or group.type.upper().endswith('.VNFDELEMENTGROUP')
