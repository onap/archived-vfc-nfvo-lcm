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

import json

def safe_get(key_val, key):
    return key_val[key] if key in key_val else ""


def find_node_name(node_id, node_list):
    for node in node_list:
        if node['id'] == node_id:
            return node['template_name']
    raise Exception('can not find node(%s).' % node_id)


def find_node_type(node_id, node_list):
    for node in node_list:
        if node['id'] == node_id:
            return node['type_name']
    raise Exception('can not find node(%s).' % node_id)


def find_related_node(node_id, src_json_model, requirement_name):
    related_nodes = []
    for model_tpl in safe_get(src_json_model, "node_templates"):
        for rt in safe_get(model_tpl, 'requirement_templates'):
            if safe_get(rt, 'name') == requirement_name and \
                safe_get(rt, 'target_node_template_name') == node_id:
                related_nodes.append(model_tpl['name'])
    return related_nodes


def convert_props(src_node, dest_node):
    if 'properties' in src_node and src_node['properties']:
        for prop_name, prop_info in src_node['properties'].items():
            if 'value' in prop_info:
                dest_node['properties'][prop_name] = prop_info['value']   


def convert_metadata(src_json):
    return src_json['metadata'] if 'metadata' in src_json else {}

def convert_factor_unit(value):
    if isinstance(value, (str, unicode)):
        return value
    return "%s %s" % (value["factor"], value["unit"])

def convert_inputs(src_json):
    inputs = {}
    if 'inputs' in src_json:
        src_inputs = src_json['inputs']
        for param_name, param_info in src_inputs.items():
            input_param = {}
            if 'type_name' in param_info:
                input_param['type'] = param_info['type_name']
            if 'description' in param_info:
                input_param['description'] = param_info['description']
            if 'value' in param_info:
                input_param['value'] = param_info['value']
            inputs[param_name] = input_param
    return inputs


def convert_vnf_node(src_node, src_json_model):
    vnf_node = {'type': src_node['type_name'], 'vnf_id': src_node['template_name'],
        'description': '', 'properties': {}, 'dependencies': [], 'networks': []}
    convert_props(src_node, vnf_node)
    for model_tpl in safe_get(src_json_model, "node_templates"):
        if model_tpl['name'] != vnf_node['vnf_id']:
            continue
        vnf_node['dependencies'] = [{
            'key_name': requirement['name'],
            'vl_id': requirement['target_node_template_name']} for \
            requirement in safe_get(model_tpl, 'requirement_templates') if \
            safe_get(requirement, 'target_capability_name') == 'virtual_linkable']
        vnf_node['networks'] = [requirement['target_node_template_name'] for \
            requirement in safe_get(model_tpl, 'requirement_templates') if \
            safe_get(requirement, 'name') == 'dependency']
    return vnf_node


def convert_pnf_node(src_node, src_json_model):
    pnf_node = {'pnf_id': src_node['template_name'], 'description': '', 'properties': {}}
    convert_props(src_node, pnf_node)
    pnf_node['cps'] = find_related_node(src_node['id'], src_json_model, 'virtualbinding')
    return pnf_node


def convert_vl_node(src_node, src_node_list):
    vl_node = {'vl_id': src_node['template_name'], 'description': '', 'properties': {}}
    convert_props(src_node, vl_node)
    vl_node['route_id'] = ''
    for relation in safe_get(src_node, 'relationships'):
        if safe_get(relation, 'type_name').endswith('.VirtualLinksTo'):
            vl_node['route_id'] = find_node_name(relation['target_node_id'], src_node_list)
            break
    vl_node['route_external'] = (src_node['type_name'].find('.RouteExternalVL') > 0)
    return vl_node


def convert_cp_node(src_node, src_node_list, model_type='NSD'):
    cp_node = {'cp_id': src_node['template_name'], 'description': '', 'properties': {}}
    convert_props(src_node, cp_node)
    src_relationships = src_node['relationships']
    for relation in src_relationships:
        if safe_get(relation, 'name') in ('virtualLink', 'virtual_link'):
            cp_node['vl_id'] = find_node_name(relation['target_node_id'], src_node_list)
        elif safe_get(relation, 'name') in ('virtualbinding', 'virtual_binding'):
            node_key = 'pnf_id' if model_type == 'NSD' else 'vdu_id'
            cp_node[node_key] = find_node_name(relation['target_node_id'], src_node_list)
    return cp_node


def convert_router_node(src_node, src_node_list):
    router_node = {'router_id': src_node['template_name'], 'description': '', 'properties': {}}
    convert_props(src_node, router_node)
    for relation in src_node['relationships']:
        if safe_get(relation, 'name') != 'external_virtual_link':
            continue
        router_node['external_vl_id'] = find_node_name(relation['target_node_id'], src_node_list)
        router_node['external_ip_addresses'] = []
        if 'properties' not in relation:
            continue
        for prop_name, prop_info in relation['properties'].items():
            if prop_name == 'router_ip_address':
                router_node['external_ip_addresses'].append(prop_info['value'])
        break
    return router_node


def convert_fp_node(src_node, src_node_list, src_json_model):
    fp_node = {'fp_id': src_node['template_name'], 'description': '', 
        'properties': {}, 'forwarder_list': []}
    convert_props(src_node, fp_node)
    for relation in safe_get(src_node, 'relationships'):
        if safe_get(relation, 'name') != 'forwarder':
            continue
        forwarder_point = {'type': 'vnf'}
        target_node_type = find_node_type(relation['target_node_id'], src_node_list).upper()
        if target_node_type.find('.CP.') >= 0 or target_node_type.endswith('.CP'):
            forwarder_point['type'] = 'cp'
        forwarder_point['node_name'] = find_node_name(relation['target_node_id'], src_node_list)
        forwarder_point['capability'] = ''
        if forwarder_point['type'] == 'vnf':
            for node_tpl in src_json_model["node_templates"]:
                if fp_node['fp_id'] != node_tpl["name"]:
                    continue
                for r_tpl in safe_get(node_tpl, "requirement_templates"):
                    if safe_get(r_tpl, "target_node_template_name") != forwarder_point['node_name']:
                        continue
                    forwarder_point['capability'] = safe_get(r_tpl, "target_capability_name")
                    break
                break
        fp_node['forwarder_list'].append(forwarder_point)
    return fp_node


def convert_vnffg_group(src_group, src_group_list, src_node_list):
    vnffg = {'vnffg_id': src_group['template_name'], 'description': '', 
        'properties': {}, 'members': []}
    convert_props(src_group, vnffg)
    for member_node_id in src_group['member_node_ids']:
        vnffg['members'].append(find_node_name(member_node_id, src_node_list))
    return vnffg


def convert_imagefile_node(src_node, src_node_list):
    image_node = {'image_file_id': src_node['template_name'], 'description': '', 
        'properties': {}}
    convert_props(src_node, image_node)
    return image_node


def convert_localstorage_node(src_node, src_node_list):
    localstorage_node = {'local_storage_id': src_node['template_name'], 'description': '', 
        'properties': {}}
    convert_props(src_node, localstorage_node)
    return localstorage_node

def convert_volumestorage_node(src_node, src_node_list):
    volumestorage_node = {
        'volume_storage_id': src_node['id'], 
        'description': "", 
        'properties': {}}
    convert_props(src_node, volumestorage_node)
    volumestorage_node["properties"]["size"] = convert_factor_unit(
        volumestorage_node["properties"]["size_of_storage"])
    return volumestorage_node

def convert_vdu_node(src_node, src_node_list, src_json_model):
    vdu_node = {'vdu_id': src_node['template_name'], 'description': '', 'properties': {},
        'image_file': '', 'local_storages': [], 'dependencies': [], 'nfv_compute': {},
        'vls': [], 'artifacts': [], 'volume_storages': []}
    convert_props(src_node, vdu_node)

    for relation in src_node.get('relationships', ''):
        r_id, r_name = safe_get(relation, 'target_node_id'), safe_get(relation, 'name')
        if r_name == 'guest_os':
            vdu_node['image_file'] = find_node_name(r_id, src_node_list)
        elif r_name == 'local_storage':
            vdu_node['local_storages'].append(find_node_name(r_id, src_node_list))
        elif r_name == 'virtual_storage':
            vdu_node['volume_storages'].append(r_id)
        elif r_name.endswith('.AttachesTo'):
            nt = find_node_type(r_id, src_node_list)
            if nt.endswith('.BlockStorage.Local') or nt.endswith('.LocalStorage'):
                vdu_node['local_storages'].append(find_node_name(r_id, src_node_list))

    for capability in src_node['capabilities']:
        if not capability['type_name'].endswith('.VirtualCompute'):
            continue
        vdu_node['nfv_compute']['flavor_extra_specs'] = {}
        for prop_name, prop_info in capability['properties'].items():
            if prop_name == "virtual_cpu":
                vdu_node['nfv_compute']['num_cpus'] = prop_info["value"]["num_virtual_cpu"]
                if "virtual_cpu_clock" in prop_info["value"]:
                    vdu_node['nfv_compute']['cpu_frequency'] = convert_factor_unit(
                        prop_info["value"]["virtual_cpu_clock"])               
            elif prop_name == "virtual_memory":
                vdu_node['nfv_compute']['mem_size'] = convert_factor_unit(
                    prop_info["value"]["virtual_mem_size"])
            elif prop_name == "requested_additional_capabilities":
                if prop_info and "value" in prop_info:
                    for key, val in prop_info["value"].items():
                        vdu_node['nfv_compute']['flavor_extra_specs'].update(
                            val["target_performance_parameters"])

    vdu_node['cps'] = find_related_node(src_node['id'], src_json_model, 'virtualbinding')

    for cp_node in vdu_node['cps']:
        for src_cp_node in src_node_list:
            if src_cp_node['template_name'] != cp_node:
                continue
            for relation in safe_get(src_cp_node, 'relationships'):
                if relation['name'] != 'virtualLink':
                    continue
                vl_node_name = find_node_name(relation['target_node_id'], src_node_list)
                if vl_node_name not in vdu_node['vls']:
                    vdu_node['vls'].append(vl_node_name)

    for item in safe_get(src_node, 'artifacts'):
        artifact = {'artifact_name': item['name'], 'type': item['type_name'], 
            'file': item['source_path'], 'properties': {}}
        convert_props(item, artifact)
        for key in artifact['properties']:
            if 'factor' in artifact['properties'][key] and 'unit' in artifact['properties'][key]:
                artifact['properties'][key] = convert_factor_unit(artifact['properties'][key])
        vdu_node['artifacts'].append(artifact)
        if artifact["type"].endswith(".SwImage"):
            vdu_node['image_file'] = artifact["artifact_name"]
    return vdu_node


def convert_exposed_node(src_json, src_nodes, exposed):
    for item in safe_get(safe_get(src_json, 'substitution'), 'requirements'):
        exposed['external_cps'].append({'key_name': item['mapped_name'],
            "cp_id": find_node_name(item['node_id'], src_nodes)})
    for item in safe_get(safe_get(src_json, 'substitution'), 'capabilities'):
        exposed['forward_cps'].append({'key_name': item['mapped_name'],
            "cp_id": find_node_name(item['node_id'], src_nodes)})


def convert_vnffgs(src_json_inst, src_nodes):
    vnffgs = []
    src_groups = safe_get(src_json_inst, 'groups')
    for group in src_groups:
        type_name = group['type_name'].upper()
        if type_name.find('.VNFFG.') >= 0 or type_name.endswith('.VNFFG'):
            vnffgs.append(convert_vnffg_group(group, src_groups, src_nodes))
    return vnffgs

def merge_imagefile_node(img_nodes, vdu_nodes):
    for vdu_node in vdu_nodes:
        for artifact in vdu_node.get("artifacts", []):
            if not artifact["type"].endswith(".SwImage"):
                continue
            imgids = [img["image_file_id"] for img in img_nodes]
            if artifact["artifact_name"] in imgids:
                continue
            img_nodes.append({
                "image_file_id": artifact["artifact_name"],
                "description": "",
                "properties": artifact["properties"]
            })

def convert_common(src_json, target_json):
    if isinstance(src_json, (unicode, str)):
        src_json_dict = json.loads(src_json)
    else:
        src_json_dict = src_json
    src_json_inst = src_json_dict["instance"]
    src_json_model = src_json_dict["model"] if "model" in src_json_dict else {}

    target_json['metadata'] = convert_metadata(src_json_inst)
    target_json['inputs'] = convert_inputs(src_json_inst)
    target_json['vls'] = []
    target_json['cps'] = []
    target_json['routers'] = []

    return src_json_inst, src_json_model


def convert_nsd_model(src_json):
    target_json = {'vnfs': [], 'pnfs': [], 'fps': []}
    src_json_inst, src_json_model = convert_common(src_json, target_json)
   
    src_nodes = src_json_inst['nodes']
    for node in src_nodes:
        type_name = node['type_name']
        if type_name.find('.VNF.') > 0 or type_name.endswith('.VNF'):
            target_json['vnfs'].append(convert_vnf_node(node, src_json_model))
        elif type_name.find('.PNF.') > 0 or type_name.endswith('.PNF'):
            target_json['pnfs'].append(convert_pnf_node(node, src_json_model))
        elif type_name.find('.VL.') > 0 or type_name.endswith('.VL') \
                or node['type_name'].find('.RouteExternalVL') > 0:
            target_json['vls'].append(convert_vl_node(node, src_nodes))
        elif type_name.find('.CP.') > 0 or type_name.endswith('.CP'):
            target_json['cps'].append(convert_cp_node(node, src_nodes))
        elif type_name.find('.FP.') > 0 or type_name.endswith('.FP'):
            target_json['fps'].append(convert_fp_node(node, src_nodes, src_json_model))
        elif type_name.endswith('.Router'):
            target_json['routers'].append(convert_router_node(node, src_nodes))

    target_json['vnffgs'] = convert_vnffgs(src_json_inst, src_nodes)

    target_json['ns_exposed'] = {'external_cps': [], 'forward_cps': []}
    convert_exposed_node(src_json_inst, src_nodes, target_json['ns_exposed'])
    return json.dumps(target_json)


def convert_vnfd_model(src_json):
    target_json = {'image_files': [], 'local_storages': [], 'vdus': [], 'volume_storages': []}
    src_json_inst, src_json_model = convert_common(src_json, target_json)

    src_nodes = src_json_inst['nodes']
    for node in src_nodes:
        type_name = node['type_name']
        if type_name.endswith('.ImageFile'):
            target_json['image_files'].append(convert_imagefile_node(node, src_nodes))
        elif type_name.endswith('.BlockStorage.Local') or type_name.endswith('.LocalStorage'):
            target_json['local_storages'].append(convert_localstorage_node(node, src_nodes))
        elif type_name.endswith('VDU.VirtualStorage'):
            target_json['volume_storages'].append(convert_volumestorage_node(node, src_nodes))
        elif type_name.endswith('VDU.Compute'):
            target_json['vdus'].append(convert_vdu_node(node, src_nodes, src_json_model))
        elif type_name.find('.VL.') > 0 or type_name.endswith('.VL') \
                or type_name.endswith('.VnfVirtualLinkDesc') \
                or type_name.endswith('.RouteExternalVL'):
            target_json['vls'].append(convert_vl_node(node, src_nodes))
        elif type_name.find('.CP.') > 0 or type_name.endswith('.CP') or type_name.endswith(".VduCpd"):
            target_json['cps'].append(convert_cp_node(node, src_nodes, 'VNFD'))
        elif type_name.endswith('.Router'):
            target_json['routers'].append(convert_router_node(node, src_nodes))
    
    target_json['vnf_exposed'] = {'external_cps': [], 'forward_cps': []}
    convert_exposed_node(src_json_inst, src_nodes, target_json['vnf_exposed'])
    merge_imagefile_node(target_json['image_files'], target_json['vdus'])
    return json.dumps(target_json)

if __name__ == '__main__':
    src_json = json.dumps({
        "instance": {
            "metadata": {
                "vnfSoftwareVersion": "1.0.0",
                "vnfProductName": "zte",
                "localizationLanguage": [
                    "english",
                    "chinese"
                ],
                "vnfProvider": "zte",
                "vnfmInfo": "zte",
                "defaultLocalizationLanguage": "english",
                "vnfdId": "zte-hss-1.0",
                "vnfProductInfoDescription": "hss",
                "vnfdVersion": "1.0.0",
                "vnfProductInfoName": "hss"
            },
            "nodes": [
                {
                    "id": "vNAT_Storage_6wdgwzedlb6sq18uzrr41sof7",
                    "type_name": "tosca.nodes.nfv.VDU.VirtualStorage",
                    "template_name": "vNAT_Storage",
                    "properties": {
                        "size_of_storage": {
                            "type_name": "scalar-unit.size",
                            "value": {
                                "value": 10000000000,
                                "factor": 10,
                                "unit": "GB",
                                "unit_size": 1000000000
                            }
                        },
                        "type_of_storage": {
                            "type_name": "string",
                            "value": "volume"
                        },
                        "rdma_enabled": {
                            "type_name": "boolean",
                            "value": False
                        }
                    },
                    "interfaces": [
                        {
                            "name": "Standard",
                            "description": "This lifecycle interface defines the essential, normative operations that TOSCA nodes may support.",
                            "type_name": "tosca.interfaces.node.lifecycle.Standard",
                            "operations": [
                                {
                                    "name": "create",
                                    "description": "Standard lifecycle create operation."
                                },
                                {
                                    "name": "stop",
                                    "description": "Standard lifecycle stop operation."
                                },
                                {
                                    "name": "start",
                                    "description": "Standard lifecycle start operation."
                                },
                                {
                                    "name": "delete",
                                    "description": "Standard lifecycle delete operation."
                                },
                                {
                                    "name": "configure",
                                    "description": "Standard lifecycle configure operation."
                                }
                            ]
                        }
                    ],
                    "capabilities": [
                        {
                            "name": "feature",
                            "type_name": "tosca.capabilities.Node"
                        },
                        {
                            "name": "virtual_storage",
                            "type_name": "tosca.capabilities.nfv.VirtualStorage"
                        }
                    ]
                },
                {
                    "id": "sriov_link_2610d7gund4e645wo39dvp238",
                    "type_name": "tosca.nodes.nfv.VnfVirtualLinkDesc",
                    "template_name": "sriov_link",
                    "properties": {
                        "vl_flavours": {
                            "type_name": "map",
                            "value": {
                                "vl_id": "aaaa"
                            }
                        },
                        "connectivity_type": {
                            "type_name": "tosca.datatypes.nfv.ConnectivityType",
                            "value": {
                                "layer_protocol": "ipv4",
                                "flow_pattern": "flat"
                            }
                        },
                        "description": {
                            "type_name": "string",
                            "value": "sriov_link"
                        },
                        "test_access": {
                            "type_name": "list",
                            "value": [
                                "test"
                            ]
                        }
                    },
                    "interfaces": [
                        {
                            "name": "Standard",
                            "description": "This lifecycle interface defines the essential, normative operations that TOSCA nodes may support.",
                            "type_name": "tosca.interfaces.node.lifecycle.Standard",
                            "operations": [
                                {
                                    "name": "create",
                                    "description": "Standard lifecycle create operation."
                                },
                                {
                                    "name": "stop",
                                    "description": "Standard lifecycle stop operation."
                                },
                                {
                                    "name": "start",
                                    "description": "Standard lifecycle start operation."
                                },
                                {
                                    "name": "delete",
                                    "description": "Standard lifecycle delete operation."
                                },
                                {
                                    "name": "configure",
                                    "description": "Standard lifecycle configure operation."
                                }
                            ]
                        }
                    ],
                    "capabilities": [
                        {
                            "name": "feature",
                            "type_name": "tosca.capabilities.Node"
                        },
                        {
                            "name": "virtual_linkable",
                            "type_name": "tosca.capabilities.nfv.VirtualLinkable"
                        }
                    ]
                },
                {
                    "id": "vdu_vNat_7ozwkcr86sa87fmd2nue2ww07",
                    "type_name": "tosca.nodes.nfv.VDU.Compute",
                    "template_name": "vdu_vNat",
                    "properties": {
                        "configurable_properties": {
                            "type_name": "map",
                            "value": {
                                "test": {
                                    "additional_vnfc_configurable_properties": {
                                        "aaa": "1",
                                        "bbb": "2",
                                        "ccc": "3"
                                    }
                                }
                            }
                        },
                        "boot_order": {
                            "type_name": "list",
                            "value": [
                                "vNAT_Storage"
                            ]
                        },
                        "name": {
                            "type_name": "string",
                            "value": "vNat"
                        },
                        "nfvi_constraints": {
                            "type_name": "list",
                            "value": [
                                "test"
                            ]
                        },
                        "description": {
                            "type_name": "string",
                            "value": "the virtual machine of vNat"
                        }
                    },
                    "interfaces": [
                        {
                            "name": "Standard",
                            "description": "This lifecycle interface defines the essential, normative operations that TOSCA nodes may support.",
                            "type_name": "tosca.interfaces.node.lifecycle.Standard",
                            "operations": [
                                {
                                    "name": "create",
                                    "description": "Standard lifecycle create operation."
                                },
                                {
                                    "name": "stop",
                                    "description": "Standard lifecycle stop operation."
                                },
                                {
                                    "name": "start",
                                    "description": "Standard lifecycle start operation."
                                },
                                {
                                    "name": "delete",
                                    "description": "Standard lifecycle delete operation."
                                },
                                {
                                    "name": "configure",
                                    "description": "Standard lifecycle configure operation."
                                }
                            ]
                        }
                    ],
                    "artifacts": [
                        {
                            "name": "vNatVNFImage",
                            "type_name": "tosca.artifacts.nfv.SwImage",
                            "source_path": "/swimages/vRouterVNF_ControlPlane.qcow2",
                            "properties": {
                                "operating_system": {
                                    "type_name": "string",
                                    "value": "linux"
                                },
                                "sw_image": {
                                    "type_name": "string",
                                    "value": "/swimages/vRouterVNF_ControlPlane.qcow2"
                                },
                                "name": {
                                    "type_name": "string",
                                    "value": "vNatVNFImage"
                                },
                                "checksum": {
                                    "type_name": "string",
                                    "value": "5000"
                                },
                                "min_ram": {
                                    "type_name": "scalar-unit.size",
                                    "value": {
                                        "value": 1000000000,
                                        "factor": 1,
                                        "unit": "GB",
                                        "unit_size": 1000000000
                                    }
                                },
                                "disk_format": {
                                    "type_name": "string",
                                    "value": "qcow2"
                                },
                                "version": {
                                    "type_name": "string",
                                    "value": "1.0"
                                },
                                "container_format": {
                                    "type_name": "string",
                                    "value": "bare"
                                },
                                "min_disk": {
                                    "type_name": "scalar-unit.size",
                                    "value": {
                                        "value": 10000000000,
                                        "factor": 10,
                                        "unit": "GB",
                                        "unit_size": 1000000000
                                    }
                                },
                                "supported_virtualisation_environments": {
                                    "type_name": "list",
                                    "value": [
                                        "test_0"
                                    ]
                                },
                                "size": {
                                    "type_name": "scalar-unit.size",
                                    "value": {
                                        "value": 10000000000,
                                        "factor": 10,
                                        "unit": "GB",
                                        "unit_size": 1000000000
                                    }
                                }
                            }
                        }
                    ],
                    "capabilities": [
                        {
                            "name": "feature",
                            "type_name": "tosca.capabilities.Node"
                        },
                        {
                            "name": "os",
                            "type_name": "tosca.capabilities.OperatingSystem",
                            "properties": {
                                "distribution": {
                                    "type_name": "string",
                                    "description": "The Operating System (OS) distribution. Examples of valid values for a \"type\" of \"Linux\" would include: debian, fedora, rhel and ubuntu."
                                },
                                "version": {
                                    "type_name": "version",
                                    "description": "The Operating System version."
                                },
                                "type": {
                                    "type_name": "string",
                                    "description": "The Operating System (OS) type. Examples of valid values include: linux, aix, mac, windows, etc."
                                },
                                "architecture": {
                                    "type_name": "string",
                                    "description": "The Operating System (OS) architecture. Examples of valid values include: x86_32, x86_64, etc."
                                }
                            }
                        },
                        {
                            "name": "host",
                            "type_name": "tosca.capabilities.Container",
                            "properties": {
                                "cpu_frequency": {
                                    "type_name": "scalar-unit.frequency",
                                    "description": "Specifies the operating frequency of CPU's core. This property expresses the expected frequency of one (1) CPU as provided by the property \"num_cpus\"."
                                },
                                "mem_size": {
                                    "type_name": "scalar-unit.size",
                                    "description": "Size of memory available to applications running on the Compute node (default unit is MB)."
                                },
                                "num_cpus": {
                                    "type_name": "integer",
                                    "description": "Number of (actual or virtual) CPUs associated with the Compute node."
                                },
                                "disk_size": {
                                    "type_name": "scalar-unit.size",
                                    "description": "Size of the local disk available to applications running on the Compute node (default unit is MB)."
                                }
                            }
                        },
                        {
                            "name": "binding",
                            "type_name": "tosca.capabilities.network.Bindable"
                        },
                        {
                            "name": "scalable",
                            "type_name": "tosca.capabilities.Scalable",
                            "properties": {
                                "min_instances": {
                                    "type_name": "integer",
                                    "value": 1,
                                    "description": "This property is used to indicate the minimum number of instances that should be created for the associated TOSCA Node Template by a TOSCA orchestrator."
                                },
                                "default_instances": {
                                    "type_name": "integer",
                                    "description": "An optional property that indicates the requested default number of instances that should be the starting number of instances a TOSCA orchestrator should attempt to allocate. Note: The value for this property MUST be in the range between the values set for \"min_instances\" and \"max_instances\" properties."
                                },
                                "max_instances": {
                                    "type_name": "integer",
                                    "value": 1,
                                    "description": "This property is used to indicate the maximum number of instances that should be created for the associated TOSCA Node Template by a TOSCA orchestrator."
                                }
                            }
                        },
                        {
                            "name": "virtual_compute",
                            "type_name": "tosca.capabilities.nfv.VirtualCompute",
                            "properties": {
                                "requested_additional_capabilities": {
                                    "type_name": "map",
                                    "value": {
                                        "ovs_dpdk": {
                                            "requested_additional_capability_name": "ovs_dpdk",
                                            "min_requested_additional_capability_version": "1.0",
                                            "support_mandatory": True,
                                            "target_performance_parameters": {
                                                "sw:ovs_dpdk": "true"
                                            },
                                            "preferred_requested_additional_capability_version": "1.0"
                                        },
                                        "hyper_threading": {
                                            "requested_additional_capability_name": "hyper_threading",
                                            "min_requested_additional_capability_version": "1.0",
                                            "support_mandatory": True,
                                            "target_performance_parameters": {
                                                "hw:cpu_cores": "2",
                                                "hw:cpu_threads": "2",
                                                "hw:cpu_threads_policy": "isolate",
                                                "hw:cpu_sockets": "2"
                                            },
                                            "preferred_requested_additional_capability_version": "1.0"
                                        },
                                        "numa": {
                                            "requested_additional_capability_name": "numa",
                                            "min_requested_additional_capability_version": "1.0",
                                            "support_mandatory": True,
                                            "target_performance_parameters": {
                                                "hw:numa_cpus.0": "0,1",
                                                "hw:numa_cpus.1": "2,3,4,5",
                                                "hw:numa_nodes": "2",
                                                "hw:numa_mem.1": "3072",
                                                "hw:numa_mem.0": "1024"
                                            },
                                            "preferred_requested_additional_capability_version": "1.0"
                                        }
                                    }
                                },
                                "virtual_cpu": {
                                    "type_name": "tosca.datatypes.nfv.VirtualCpu",
                                    "value": {
                                        "num_virtual_cpu": 2,
                                        "virtual_cpu_clock": {
                                            "value": 2400000000,
                                            "factor": 2.4,
                                            "unit": "GHz",
                                            "unit_size": 1000000000
                                        },
                                        "cpu_architecture": "X86",
                                        "virtual_cpu_oversubscription_policy": "test",
                                        "virtual_cpu_pinning": {
                                            "cpu_pinning_map": {
                                                "cpu_pinning_0": "1"
                                            },
                                            "cpu_pinning_policy": "static"
                                        }
                                    }
                                },
                                "virtual_memory": {
                                    "type_name": "tosca.datatypes.nfv.VirtualMemory",
                                    "value": {
                                        "virtual_mem_oversubscription_policy": "mem_policy_test",
                                        "numa_enabled": True,
                                        "virtual_mem_size": {
                                            "value": 10000000000,
                                            "factor": 10,
                                            "unit": "GB",
                                            "unit_size": 1000000000
                                        }
                                    }
                                }
                            }
                        },
                        {
                            "name": "virtual_binding",
                            "type_name": "tosca.capabilities.nfv.VirtualBindable"
                        }
                    ],
                    "relationships": [
                        {
                            "name": "virtual_storage",
                            "source_requirement_index": 0,
                            "target_node_id": "vNAT_Storage_6wdgwzedlb6sq18uzrr41sof7",
                            "properties": {
                                "location": {
                                    "type_name": "string",
                                    "value": "/mnt/volume_0",
                                    "description": "The relative location (e.g., path on the file system), which provides the root location to address an attached node. e.g., a mount point / path such as '/usr/data'. Note: The user must provide it and it cannot be \"root\"."
                                }
                            },
                            "source_interfaces": [
                                {
                                    "name": "Configure",
                                    "description": "The lifecycle interfaces define the essential, normative operations that each TOSCA Relationship Types may support.",
                                    "type_name": "tosca.interfaces.relationship.Configure",
                                    "operations": [
                                        {
                                            "name": "add_source",
                                            "description": "Operation to notify the target node of a source node which is now available via a relationship."
                                        },
                                        {
                                            "name": "pre_configure_target",
                                            "description": "Operation to pre-configure the target endpoint."
                                        },
                                        {
                                            "name": "post_configure_source",
                                            "description": "Operation to post-configure the source endpoint."
                                        },
                                        {
                                            "name": "target_changed",
                                            "description": "Operation to notify source some property or attribute of the target changed"
                                        },
                                        {
                                            "name": "pre_configure_source",
                                            "description": "Operation to pre-configure the source endpoint."
                                        },
                                        {
                                            "name": "post_configure_target",
                                            "description": "Operation to post-configure the target endpoint."
                                        },
                                        {
                                            "name": "remove_target",
                                            "description": "Operation to remove a target node."
                                        },
                                        {
                                            "name": "add_target",
                                            "description": "Operation to notify the source node of a target node being added via a relationship."
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    "id": "SRIOV_Port_leu1j6rfdt4c8vta6aec1xe39",
                    "type_name": "tosca.nodes.nfv.VduCpd",
                    "template_name": "SRIOV_Port",
                    "properties": {
                        "address_data": {
                            "type_name": "list",
                            "value": [
                                {
                                    "address_type": "ip_address",
                                    "l3_address_data": {
                                        "ip_address_type": "ipv4",
                                        "floating_ip_activated": False,
                                        "number_of_ip_address": 1,
                                        "ip_address_assignment": True
                                    }
                                }
                            ]
                        },
                        "description": {
                            "type_name": "string",
                            "value": "sriov port"
                        },
                        "layer_protocol": {
                            "type_name": "string",
                            "value": "ipv4"
                        },
                        "virtual_network_interface_requirements": {
                            "type_name": "list",
                            "value": [
                                {
                                    "requirement": {
                                        "SRIOV": "true"
                                    },
                                    "support_mandatory": False,
                                    "name": "sriov",
                                    "description": "sriov"
                                },
                                {
                                    "requirement": {
                                        "SRIOV": "false"
                                    },
                                    "support_mandatory": False,
                                    "name": "normal",
                                    "description": "normal"
                                }
                            ]
                        },
                        "role": {
                            "type_name": "string",
                            "value": "root"
                        },
                        "bitrate_requirement": {
                            "type_name": "integer",
                            "value": 10
                        }
                    },
                    "interfaces": [
                        {
                            "name": "Standard",
                            "description": "This lifecycle interface defines the essential, normative operations that TOSCA nodes may support.",
                            "type_name": "tosca.interfaces.node.lifecycle.Standard",
                            "operations": [
                                {
                                    "name": "create",
                                    "description": "Standard lifecycle create operation."
                                },
                                {
                                    "name": "stop",
                                    "description": "Standard lifecycle stop operation."
                                },
                                {
                                    "name": "start",
                                    "description": "Standard lifecycle start operation."
                                },
                                {
                                    "name": "delete",
                                    "description": "Standard lifecycle delete operation."
                                },
                                {
                                    "name": "configure",
                                    "description": "Standard lifecycle configure operation."
                                }
                            ]
                        }
                    ],
                    "capabilities": [
                        {
                            "name": "feature",
                            "type_name": "tosca.capabilities.Node"
                        }
                    ],
                    "relationships": [
                        {
                            "name": "virtual_binding",
                            "source_requirement_index": 0,
                            "target_node_id": "vdu_vNat_7ozwkcr86sa87fmd2nue2ww07",
                            "source_interfaces": [
                                {
                                    "name": "Configure",
                                    "description": "The lifecycle interfaces define the essential, normative operations that each TOSCA Relationship Types may support.",
                                    "type_name": "tosca.interfaces.relationship.Configure",
                                    "operations": [
                                        {
                                            "name": "add_source",
                                            "description": "Operation to notify the target node of a source node which is now available via a relationship."
                                        },
                                        {
                                            "name": "pre_configure_target",
                                            "description": "Operation to pre-configure the target endpoint."
                                        },
                                        {
                                            "name": "post_configure_source",
                                            "description": "Operation to post-configure the source endpoint."
                                        },
                                        {
                                            "name": "target_changed",
                                            "description": "Operation to notify source some property or attribute of the target changed"
                                        },
                                        {
                                            "name": "pre_configure_source",
                                            "description": "Operation to pre-configure the source endpoint."
                                        },
                                        {
                                            "name": "post_configure_target",
                                            "description": "Operation to post-configure the target endpoint."
                                        },
                                        {
                                            "name": "remove_target",
                                            "description": "Operation to remove a target node."
                                        },
                                        {
                                            "name": "add_target",
                                            "description": "Operation to notify the source node of a target node being added via a relationship."
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "name": "virtual_link",
                            "source_requirement_index": 1,
                            "target_node_id": "sriov_link_2610d7gund4e645wo39dvp238",
                            "target_capability_name": "feature",
                            "source_interfaces": [
                                {
                                    "name": "Configure",
                                    "description": "The lifecycle interfaces define the essential, normative operations that each TOSCA Relationship Types may support.",
                                    "type_name": "tosca.interfaces.relationship.Configure",
                                    "operations": [
                                        {
                                            "name": "add_source",
                                            "description": "Operation to notify the target node of a source node which is now available via a relationship."
                                        },
                                        {
                                            "name": "pre_configure_target",
                                            "description": "Operation to pre-configure the target endpoint."
                                        },
                                        {
                                            "name": "post_configure_source",
                                            "description": "Operation to post-configure the source endpoint."
                                        },
                                        {
                                            "name": "target_changed",
                                            "description": "Operation to notify source some property or attribute of the target changed"
                                        },
                                        {
                                            "name": "pre_configure_source",
                                            "description": "Operation to pre-configure the source endpoint."
                                        },
                                        {
                                            "name": "post_configure_target",
                                            "description": "Operation to post-configure the target endpoint."
                                        },
                                        {
                                            "name": "remove_target",
                                            "description": "Operation to remove a target node."
                                        },
                                        {
                                            "name": "add_target",
                                            "description": "Operation to notify the source node of a target node being added via a relationship."
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ],
            "substitution": {
                "node_type_name": "tosca.nodes.nfv.VNF.vOpenNAT",
                "requirements": [
                    {
                        "mapped_name": "sriov_plane",
                        "node_id": "SRIOV_Port_leu1j6rfdt4c8vta6aec1xe39",
                        "name": "virtual_link"
                    }
                ]
            }
        },
        "model": {
            "metadata": {
                "vnfSoftwareVersion": "1.0.0",
                "vnfProductName": "openNAT",
                "localizationLanguage": [
                    "english",
                    "chinese"
                ],
                "vnfProvider": "intel",
                "vnfmInfo": "GVNFM",
                "defaultLocalizationLanguage": "english",
                "vnfdId": "openNAT-1.0",
                "vnfProductInfoDescription": "openNAT",
                "vnfdVersion": "1.0.0",
                "vnfProductInfoName": "openNAT"
            },
            "node_templates": [
                {
                    "name": "vNAT_Storage",
                    "type_name": "tosca.nodes.nfv.VDU.VirtualStorage",
                    "default_instances": 1,
                    "min_instances": 0,
                    "properties": {
                        "size_of_storage": {
                            "type_name": "scalar-unit.size",
                            "value": {
                                "value": 10000000000,
                                "factor": 10,
                                "unit": "GB",
                                "unit_size": 1000000000
                            }
                        },
                        "type_of_storage": {
                            "type_name": "string",
                            "value": "volume"
                        },
                        "rdma_enabled": {
                            "type_name": "boolean",
                            "value": False
                        }
                    },
                    "interface_templates": [
                        ""
                    ],
                    "capability_templates": [
                        {
                            "name": "feature",
                            "type_name": "tosca.capabilities.Node"
                        },
                        {
                            "name": "virtual_storage",
                            "type_name": "tosca.capabilities.nfv.VirtualStorage"
                        }
                    ]
                },
                {
                    "name": "vdu_vNat",
                    "type_name": "tosca.nodes.nfv.VDU.Compute",
                    "default_instances": 1,
                    "min_instances": 0,
                    "properties": {
                        "configurable_properties": {
                            "type_name": "map",
                            "value": {
                                "test": {
                                    "additional_vnfc_configurable_properties": {
                                        "aaa": "1",
                                        "bbb": "2",
                                        "ccc": "3"
                                    }
                                }
                            }
                        },
                        "boot_order": {
                            "type_name": "list",
                            "value": [
                                "vNAT_Storage"
                            ]
                        },
                        "name": {
                            "type_name": "string",
                            "value": "vNat"
                        },
                        "nfvi_constraints": {
                            "type_name": "list",
                            "value": [
                                "test"
                            ]
                        },
                        "description": {
                            "type_name": "string",
                            "value": "the virtual machine of vNat"
                        }
                    },
                    "interface_templates": [
                        ""
                    ],
                    "artifact_templates": [
                        ""
                    ],
                    "capability_templates": [
                        {
                            "name": "feature",
                            "type_name": "tosca.capabilities.Node"
                        },
                        {
                            "name": "os",
                            "type_name": "tosca.capabilities.OperatingSystem",
                            "properties": {
                                "distribution": {
                                    "type_name": "string",
                                    "description": "The Operating System (OS) distribution. Examples of valid values for a \"type\" of \"Linux\" would include: debian, fedora, rhel and ubuntu."
                                },
                                "version": {
                                    "type_name": "version",
                                    "description": "The Operating System version."
                                },
                                "type": {
                                    "type_name": "string",
                                    "description": "The Operating System (OS) type. Examples of valid values include: linux, aix, mac, windows, etc."
                                },
                                "architecture": {
                                    "type_name": "string",
                                    "description": "The Operating System (OS) architecture. Examples of valid values include: x86_32, x86_64, etc."
                                }
                            }
                        },
                        {
                            "name": "host",
                            "type_name": "tosca.capabilities.Container",
                            "valid_source_node_type_names": [
                                "tosca.nodes.SoftwareComponent"
                            ],
                            "properties": {
                                "cpu_frequency": {
                                    "type_name": "scalar-unit.frequency",
                                    "description": "Specifies the operating frequency of CPU's core. This property expresses the expected frequency of one (1) CPU as provided by the property \"num_cpus\"."
                                },
                                "mem_size": {
                                    "type_name": "scalar-unit.size",
                                    "description": "Size of memory available to applications running on the Compute node (default unit is MB)."
                                },
                                "num_cpus": {
                                    "type_name": "integer",
                                    "description": "Number of (actual or virtual) CPUs associated with the Compute node."
                                },
                                "disk_size": {
                                    "type_name": "scalar-unit.size",
                                    "description": "Size of the local disk available to applications running on the Compute node (default unit is MB)."
                                }
                            }
                        },
                        {
                            "name": "binding",
                            "type_name": "tosca.capabilities.network.Bindable"
                        },
                        {
                            "name": "scalable",
                            "type_name": "tosca.capabilities.Scalable",
                            "properties": {
                                "min_instances": {
                                    "type_name": "integer",
                                    "value": 1,
                                    "description": "This property is used to indicate the minimum number of instances that should be created for the associated TOSCA Node Template by a TOSCA orchestrator."
                                },
                                "default_instances": {
                                    "type_name": "integer",
                                    "description": "An optional property that indicates the requested default number of instances that should be the starting number of instances a TOSCA orchestrator should attempt to allocate. Note: The value for this property MUST be in the range between the values set for \"min_instances\" and \"max_instances\" properties."
                                },
                                "max_instances": {
                                    "type_name": "integer",
                                    "value": 1,
                                    "description": "This property is used to indicate the maximum number of instances that should be created for the associated TOSCA Node Template by a TOSCA orchestrator."
                                }
                            }
                        },
                        {
                            "name": "virtual_compute",
                            "type_name": "tosca.capabilities.nfv.VirtualCompute",
                            "properties": {
                                "requested_additional_capabilities": {
                                    "type_name": "map",
                                    "value": {
                                        "ovs_dpdk": {
                                            "requested_additional_capability_name": "ovs_dpdk",
                                            "min_requested_additional_capability_version": "1.0",
                                            "support_mandatory": True,
                                            "target_performance_parameters": {
                                                "sw:ovs_dpdk": "true"
                                            },
                                            "preferred_requested_additional_capability_version": "1.0"
                                        },
                                        "hyper_threading": {
                                            "requested_additional_capability_name": "hyper_threading",
                                            "min_requested_additional_capability_version": "1.0",
                                            "support_mandatory": True,
                                            "target_performance_parameters": {
                                                "hw:cpu_cores": "2",
                                                "hw:cpu_threads": "2",
                                                "hw:cpu_threads_policy": "isolate",
                                                "hw:cpu_sockets": "2"
                                            },
                                            "preferred_requested_additional_capability_version": "1.0"
                                        },
                                        "numa": {
                                            "requested_additional_capability_name": "numa",
                                            "min_requested_additional_capability_version": "1.0",
                                            "support_mandatory": True,
                                            "target_performance_parameters": {
                                                "hw:numa_cpus.0": "0,1",
                                                "hw:numa_cpus.1": "2,3,4,5",
                                                "hw:numa_nodes": "2",
                                                "hw:numa_mem.1": "3072",
                                                "hw:numa_mem.0": "1024"
                                            },
                                            "preferred_requested_additional_capability_version": "1.0"
                                        }
                                    }
                                },
                                "virtual_cpu": {
                                    "type_name": "tosca.datatypes.nfv.VirtualCpu",
                                    "value": {
                                        "num_virtual_cpu": 2,
                                        "virtual_cpu_clock": {
                                            "value": 2400000000,
                                            "factor": 2.4,
                                            "unit": "GHz",
                                            "unit_size": 1000000000
                                        },
                                        "cpu_architecture": "X86",
                                        "virtual_cpu_oversubscription_policy": "test",
                                        "virtual_cpu_pinning": {
                                            "cpu_pinning_map": {
                                                "cpu_pinning_0": "1"
                                            },
                                            "cpu_pinning_policy": "static"
                                        }
                                    }
                                },
                                "virtual_memory": {
                                    "type_name": "tosca.datatypes.nfv.VirtualMemory",
                                    "value": {
                                        "virtual_mem_oversubscription_policy": "mem_policy_test",
                                        "numa_enabled": True,
                                        "virtual_mem_size": {
                                            "value": 10000000000,
                                            "factor": 10,
                                            "unit": "GB",
                                            "unit_size": 1000000000
                                        }
                                    }
                                }
                            }
                        },
                        {
                            "name": "virtual_binding",
                            "type_name": "tosca.capabilities.nfv.VirtualBindable"
                        }
                    ],
                    "requirement_templates": [
                        {
                            "name": "virtual_storage",
                            "target_node_template_name": "vNAT_Storage",
                            "relationship_template": {
                                "type_name": "tosca.relationships.nfv.VDU.AttachedTo",
                                "properties": {
                                    "location": {
                                        "type_name": "string",
                                        "value": "/mnt/volume_0",
                                        "description": "The relative location (e.g., path on the file system), which provides the root location to address an attached node. e.g., a mount point / path such as '/usr/data'. Note: The user must provide it and it cannot be \"root\"."
                                    }
                                },
                                "source_interface_templates": [
                                    ""
                                ]
                            }
                        }
                    ]
                },
                {
                    "name": "SRIOV_Port",
                    "type_name": "tosca.nodes.nfv.VduCpd",
                    "default_instances": 1,
                    "min_instances": 0,
                    "properties": {
                        "address_data": {
                            "type_name": "list",
                            "value": [
                                {
                                    "address_type": "ip_address",
                                    "l3_address_data": {
                                        "ip_address_type": "ipv4",
                                        "floating_ip_activated": False,
                                        "number_of_ip_address": 1,
                                        "ip_address_assignment": True
                                    }
                                }
                            ]
                        },
                        "description": {
                            "type_name": "string",
                            "value": "sriov port"
                        },
                        "layer_protocol": {
                            "type_name": "string",
                            "value": "ipv4"
                        },
                        "virtual_network_interface_requirements": {
                            "type_name": "list",
                            "value": [
                                {
                                    "requirement": {
                                        "SRIOV": "true"
                                    },
                                    "support_mandatory": False,
                                    "name": "sriov",
                                    "description": "sriov"
                                },
                                {
                                    "requirement": {
                                        "SRIOV": "false"
                                    },
                                    "support_mandatory": False,
                                    "name": "normal",
                                    "description": "normal"
                                }
                            ]
                        },
                        "role": {
                            "type_name": "string",
                            "value": "root"
                        },
                        "bitrate_requirement": {
                            "type_name": "integer",
                            "value": 10
                        }
                    },
                    "interface_templates": [
                        ""
                    ],
                    "capability_templates": [
                        {
                            "name": "feature",
                            "type_name": "tosca.capabilities.Node"
                        }
                    ],
                    "requirement_templates": [
                        {
                            "name": "virtual_binding",
                            "target_node_template_name": "vdu_vNat",
                            "relationship_template": {
                                "type_name": "tosca.relationships.nfv.VirtualBindsTo",
                                "source_interface_templates": [
                                    ""
                                ]
                            }
                        },
                        {
                            "name": "virtual_link",
                            "target_node_type_name": "tosca.nodes.nfv.VnfVirtualLinkDesc",
                            "relationship_template": {
                                "type_name": "tosca.relationships.nfv.VirtualLinksTo",
                                "source_interface_templates": [
                                    ""
                                ]
                            }
                        }
                    ]
                }
            ],
            "substitution_template": {
                "node_type_name": "tosca.nodes.nfv.VNF.vOpenNAT",
                "requirement_templates": [
                    {
                        "mapped_name": "sriov_plane",
                        "node_template_name": "SRIOV_Port",
                        "name": "virtual_link"
                    }
                ]
            }
        }
    })
    print convert_vnfd_model(src_json)




