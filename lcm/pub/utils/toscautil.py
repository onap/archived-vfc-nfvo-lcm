# Copyright 2016-2017 ZTE Corporation.
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
        if safe_get(relation, 'name') == 'virtualLink':
            cp_node['vl_id'] = find_node_name(relation['target_node_id'], src_node_list)
        elif safe_get(relation, 'name') == 'virtualbinding':
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


def convert_vdu_node(src_node, src_node_list, src_json_model):
    vdu_node = {'vdu_id': src_node['template_name'], 'description': '', 'properties': {},
        'image_file': '', 'local_storages': [], 'dependencies': [], 'nfv_compute': {},
        'vls': [], 'artifacts': []}
    convert_props(src_node, vdu_node)

    for relation in src_node['relationships']:
        r_id, r_name = safe_get(relation, 'target_node_id'), safe_get(relation, 'name')
        if r_name == 'guest_os':
            vdu_node['image_file'] = find_node_name(r_id, src_node_list)
        elif r_name == 'local_storage':
            vdu_node['local_storages'].append(find_node_name(r_id, src_node_list))
        elif r_name.endswith('.AttachesTo'):
            nt = find_node_type(r_id, src_node_list)
            if nt.endswith('.BlockStorage.Local') or nt.endswith('.LocalStorage'):
                vdu_node['local_storages'].append(find_node_name(r_id, src_node_list))

    for capability in src_node['capabilities']:
        if capability['name'] != 'nfv_compute':
            continue
        for prop_name, prop_info in capability['properties'].items():
            if 'value' in prop_info:
                vdu_node['nfv_compute'][prop_name] = prop_info['value']

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
            'file': item['source_path']}
        vdu_node['artifacts'].append(artifact)

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

def convert_policy_node(src_json):
    target_json = {'name': src_json['template_name'],'file_url': src_json['properties']['drl_file_url']['value']}

    return target_json

def convert_nsd_model(src_json):
    target_json = {'vnfs': [], 'pnfs': [], 'fps': [], 'policies': []}
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
        elif type_name.endswith('tosca.policies.Drools'):
            target_json['policies'].append(convert_policy_node(node))

    target_json['vnffgs'] = convert_vnffgs(src_json_inst, src_nodes)

    target_json['ns_exposed'] = {'external_cps': [], 'forward_cps': []}
    convert_exposed_node(src_json_inst, src_nodes, target_json['ns_exposed'])
    return json.dumps(target_json)


def convert_vnfd_model(src_json):
    target_json = {'image_files': [], 'local_storages': [], 'vdus': []}
    src_json_inst, src_json_model = convert_common(src_json, target_json)
    if "vnfdVersion" in src_json_inst.get("metadata", {}):
        from . import toscautil_new
        return toscautil_new.convert_vnfd_model(src_json)

    src_nodes = src_json_inst['nodes']
    for node in src_nodes:
        type_name = node['type_name']
        if type_name.endswith('.ImageFile'):
            target_json['image_files'].append(convert_imagefile_node(node, src_nodes))
        elif type_name.endswith('.BlockStorage.Local') or type_name.endswith('.LocalStorage'):
            target_json['local_storages'].append(convert_localstorage_node(node, src_nodes))
        elif type_name.find('.VDU.') > 0 or type_name.endswith('.VDU'):
            target_json['vdus'].append(convert_vdu_node(node, src_nodes, src_json_model))
        elif type_name.find('.VL.') > 0 or type_name.endswith('.VL') \
                or node['type_name'].find('.RouteExternalVL') > 0:
            target_json['vls'].append(convert_vl_node(node, src_nodes))
        elif type_name.find('.CP.') > 0 or type_name.endswith('.CP'):
            target_json['cps'].append(convert_cp_node(node, src_nodes, 'VNFD'))
        elif type_name.endswith('.Router'):
            target_json['routers'].append(convert_router_node(node, src_nodes))
    
    target_json['vnf_exposed'] = {'external_cps': [], 'forward_cps': []}
    convert_exposed_node(src_json_inst, src_nodes, target_json['vnf_exposed'])
    return json.dumps(target_json)

if __name__ == '__main__':
    src_json = json.dumps(
        {
            "instance":{
                "metadata":{
                    "vendor":"ZTE",
                    "name":"VCPE_NS",
                    "csarVersion":"v1.0",
                    "csarType":"NSAR",
                    "csarProvider":"ZTE",
                    "version":1,
                    "invariant_id":"vcpe_ns_sff_1",
                    "id":"VCPE_NS",
                    "description":"vcpe_ns"
                },
                "policies:":[
                    {
                        "aaa:" : {
                            "type": "tosca.policies.Drools",
                            "properties": {
                                "drl_file_url":"policies/abc.drl"
                            }
                        }
                    }
                ],
                "nodes":[
                    {
                        "id":"policies",
                        "type_name":"tosca.policies.Drools",
                        "template_name":"aaa",
                        "properties":{
                            "drl_file_url":{
                                "type_name":"string",
                                "value":"policies/abc.drl"
                            }
                        }
                    },
                    {
                        "id":"path2_kgmfqr5ldqs9lj3oscrgxqefc",
                        "type_name":"tosca.nodes.nfv.ext.FP",
                        "template_name":"path2",
                        "properties":{
                            "symmetric":{
                                "type_name":"boolean",
                                "value":False
                            },
                            "policy":{
                                "type_name":"tosca.datatypes.nfv.ext.FPPolicy",
                                "value":{
                                    "type":"ACL",
                                    "criteria":{
                                        "dest_port_range":"1-100",
                                        "ip_protocol":"tcp",
                                        "source_ip_range":[
                                            "119.1.1.1-119.1.1.10"
                                        ],
                                        "dest_ip_range":[
                                            {"get_input":"NatIpRange"}
                                        ],
                                        "dscp":0,
                                        "source_port_range":"1-100"
                                    }
                                }
                            }
                        },
                        "interfaces":[
                            {
                                "name":"Standard",
                                "description":"This lifecycle interface defines the essential, normative operations that TOSCA nodes may support.",
                                "type_name":"tosca.interfaces.node.lifecycle.Standard",
                                "operations":[
                                    {
                                        "name":"create",
                                        "description":"Standard lifecycle create operation."
                                    },
                                    {
                                        "name":"stop",
                                        "description":"Standard lifecycle stop operation."
                                    },
                                    {
                                        "name":"start",
                                        "description":"Standard lifecycle start operation."
                                    },
                                    {
                                        "name":"delete",
                                        "description":"Standard lifecycle delete operation."
                                    },
                                    {
                                        "name":"configure",
                                        "description":"Standard lifecycle configure operation."
                                    }
                                ]
                            }
                        ],
                        "capabilities":[
                            {
                                "name":"feature",
                                "type_name":"tosca.capabilities.Node"
                            }
                        ],
                        "relationships":[
                            {
                                "name":"forwarder",
                                "source_requirement_index":0,
                                "target_node_id":"m6000_data_out_qeukdtf6g87cnparxi51fa8s6"
                            },
                            {
                                "name":"forwarder",
                                "source_requirement_index":1,
                                "target_node_id":"m600_tunnel_cp_imwfk5l48ljz0g9knc6d68hv5"
                            },
                            {
                                "name":"forwarder",
                                "source_requirement_index":2,
                                "target_node_id":"VNAT_cfdljtspvkp234irka59wgab0",
                                "target_capability_name":"feature"
                            }
                        ]
                    },
                    {
                        "id":"path1_bv53fblv26hawr8dj4fxe2rsd",
                        "type_name":"tosca.nodes.nfv.ext.FP",
                        "template_name":"path1",
                        "properties":{
                            "symmetric":{
                                "type_name":"boolean",
                                "value":True
                            },
                            "policy":{
                                "type_name":"tosca.datatypes.nfv.ext.FPPolicy",
                                "value":{
                                    "type":"ACL",
                                    "criteria":{
                                        "dest_port_range":"1-100",
                                        "ip_protocol":"tcp",
                                        "source_ip_range":[
                                            "1-100"
                                        ],
                                        "dest_ip_range":[
                                            "1-100"
                                        ],
                                        "dscp":4,
                                        "source_port_range":"1-100"
                                    }
                                }
                            }
                        },
                        "interfaces":[
                            {
                                "name":"Standard",
                                "description":"This lifecycle interface defines the essential, normative operations that TOSCA nodes may support.",
                                "type_name":"tosca.interfaces.node.lifecycle.Standard",
                                "operations":[
                                    {
                                        "name":"create",
                                        "description":"Standard lifecycle create operation."
                                    },
                                    {
                                        "name":"stop",
                                        "description":"Standard lifecycle stop operation."
                                    },
                                    {
                                        "name":"start",
                                        "description":"Standard lifecycle start operation."
                                    },
                                    {
                                        "name":"delete",
                                        "description":"Standard lifecycle delete operation."
                                    },
                                    {
                                        "name":"configure",
                                        "description":"Standard lifecycle configure operation."
                                    }
                                ]
                            }
                        ],
                        "capabilities":[
                            {
                                "name":"feature",
                                "type_name":"tosca.capabilities.Node"
                            }
                        ],
                        "relationships":[
                            {
                                "name":"forwarder",
                                "source_requirement_index":0,
                                "target_node_id":"m6000_data_in_eldly5txw4frny3cc349uz3nc"
                            },
                            {
                                "name":"forwarder",
                                "source_requirement_index":1,
                                "target_node_id":"m600_tunnel_cp_imwfk5l48ljz0g9knc6d68hv5"
                            },
                            {
                                "name":"forwarder",
                                "source_requirement_index":2,
                                "target_node_id":"VFW_57z0ua89aiyl8ncvw7h7mjf34",
                                "target_capability_name":"feature"
                            },
                            {
                                "name":"forwarder",
                                "source_requirement_index":3,
                                "target_node_id":"VNAT_cfdljtspvkp234irka59wgab0",
                                "target_capability_name":"feature"
                            },
                            {
                                "name":"forwarder",
                                "source_requirement_index":4,
                                "target_node_id":"m600_tunnel_cp_imwfk5l48ljz0g9knc6d68hv5"
                            },
                            {
                                "name":"forwarder",
                                "source_requirement_index":5,
                                "target_node_id":"m6000_data_out_qeukdtf6g87cnparxi51fa8s6"
                            }
                        ]
                    },
                    {
                        "id":"m6000_data_out_qeukdtf6g87cnparxi51fa8s6",
                        "type_name":"tosca.nodes.nfv.ext.zte.CP",
                        "template_name":"m6000_data_out",
                        "properties":{
                            "direction":{
                                "type_name":"string",
                                "value":"bidirectional"
                            },
                            "vnic_type":{
                                "type_name":"string",
                                "value":"normal"
                            },
                            "bandwidth":{
                                "type_name":"integer",
                                "value":0
                            },
                            "mac_address":{
                                "type_name":"string",
                                "value":"11-22-33-22-11-44"
                            },
                            "interface_name":{
                                "type_name":"string",
                                "value":"xgei-0/4/1/5"
                            },
                            "ip_address":{
                                "type_name":"string",
                                "value":"176.1.1.2"
                            },
                            "order":{
                                "type_name":"integer",
                                "value":0
                            },
                            "sfc_encapsulation":{
                                "type_name":"string",
                                "value":"mac"
                            }
                        },
                        "interfaces":[
                            {
                                "name":"Standard",
                                "description":"This lifecycle interface defines the essential, normative operations that TOSCA nodes may support.",
                                "type_name":"tosca.interfaces.node.lifecycle.Standard",
                                "operations":[
                                    {
                                        "name":"create",
                                        "description":"Standard lifecycle create operation."
                                    },
                                    {
                                        "name":"stop",
                                        "description":"Standard lifecycle stop operation."
                                    },
                                    {
                                        "name":"start",
                                        "description":"Standard lifecycle start operation."
                                    },
                                    {
                                        "name":"delete",
                                        "description":"Standard lifecycle delete operation."
                                    },
                                    {
                                        "name":"configure",
                                        "description":"Standard lifecycle configure operation."
                                    }
                                ]
                            }
                        ],
                        "capabilities":[
                            {
                                "name":"feature",
                                "type_name":"tosca.capabilities.Node"
                            },
                            {
                                "name":"forwarder",
                                "type_name":"tosca.capabilities.nfv.Forwarder"
                            }
                        ],
                        "relationships":[
                            {
                                "name":"virtualbinding",
                                "source_requirement_index":0,
                                "target_node_id":"m6000_s_7qtzo5nuocyfmebc6kp9raq18",
                                "target_capability_name":"feature"
                            },
                            {
                                "name":"virtualLink",
                                "source_requirement_index":1,
                                "target_node_id":"path2_kgmfqr5ldqs9lj3oscrgxqefc",
                                "target_capability_name":"feature"
                            },
                            {
                                "name":"forwarder",
                                "source_requirement_index":2,
                                "target_node_id":"path2_kgmfqr5ldqs9lj3oscrgxqefc",
                                "target_capability_name":"feature"
                            }
                        ]
                    },
                    {
                        "id":"VFW_57z0ua89aiyl8ncvw7h7mjf34",
                        "type_name":"tosca.nodes.nfv.ext.zte.VNF.VFW",
                        "template_name":"VFW",
                        "properties":{
                            "is_shared":{
                                "type_name":"boolean",
                                "value":False
                            },
                            "plugin_info":{
                                "type_name":"string",
                                "value":"vbrasplugin_1.0"
                            },
                            "vendor":{
                                "type_name":"string",
                                "value":"zte"
                            },
                            "request_reclassification":{
                                "type_name":"boolean",
                                "value":False
                            },
                            "vnf_extend_type":{
                                "type_name":"string",
                                "value":"driver"
                            },
                            "name":{
                                "type_name":"string",
                                "value":"VFW"
                            },
                            "version":{
                                "type_name":"string",
                                "value":"1.0"
                            },
                            "cross_dc":{
                                "type_name":"boolean",
                                "value":False
                            },
                            "vnf_type":{
                                "type_name":"string",
                                "value":"VFW"
                            },
                            "vnfd_version":{
                                "type_name":"string",
                                "value":"1.0.0"
                            },
                            "id":{
                                "type_name":"string",
                                "value":"vcpe_vfw_zte_1_0"
                            },
                            "nsh_aware":{
                                "type_name":"boolean",
                                "value":True
                            },
                            "adjust_vnf_capacity":{
                                "type_name":"boolean",
                                "value":True
                            },
                            "vmnumber_overquota_alarm":{
                                "type_name":"boolean",
                                "value":True
                            },
                            "csarProvider":{
                                "type_name":"string",
                                "value":"ZTE"
                            },
                            "csarVersion":{
                                "type_name":"string",
                                "value":"v1.0"
                            },
                            "externalPluginManageNetworkName":{
                                "type_name":"string",
                                "value":"vlan_4007_plugin_net"
                            },
                            "csarType":{
                                "type_name":"string",
                                "value":"NFAR"
                            }
                        },
                        "interfaces":[
                            {
                                "name":"Standard",
                                "description":"This lifecycle interface defines the essential, normative operations that TOSCA nodes may support.",
                                "type_name":"tosca.interfaces.node.lifecycle.Standard",
                                "operations":[
                                    {
                                        "name":"create",
                                        "description":"Standard lifecycle create operation."
                                    },
                                    {
                                        "name":"stop",
                                        "description":"Standard lifecycle stop operation."
                                    },
                                    {
                                        "name":"start",
                                        "description":"Standard lifecycle start operation."
                                    },
                                    {
                                        "name":"delete",
                                        "description":"Standard lifecycle delete operation."
                                    },
                                    {
                                        "name":"configure",
                                        "description":"Standard lifecycle configure operation."
                                    }
                                ]
                            }
                        ],
                        "capabilities":[
                            {
                                "name":"feature",
                                "type_name":"tosca.capabilities.Node"
                            },
                            {
                                "name":"forwarder",
                                "type_name":"tosca.capabilities.nfv.Forwarder"
                            },
                            {
                                "name":"vfw_fw_inout",
                                "type_name":"tosca.capabilities.nfv.Forwarder"
                            }
                        ],
                        "relationships":[
                            {
                                "name":"vfw_ctrl_by_manager_cp",
                                "source_requirement_index":0,
                                "target_node_id":"ext_mnet_net_au2otee5mcy0dnpqykj487zr3",
                                "target_capability_name":"feature"
                            },
                            {
                                "name":"vfw_data_cp",
                                "source_requirement_index":1,
                                "target_node_id":"sfc_data_network_vx3pc1oahn0k0pa5q722yafee",
                                "target_capability_name":"feature"
                            },
                            {
                                "name":"virtualLink",
                                "source_requirement_index":2,
                                "target_node_id":"path2_kgmfqr5ldqs9lj3oscrgxqefc",
                                "target_capability_name":"feature"
                            },
                            {
                                "name":"forwarder",
                                "source_requirement_index":3,
                                "target_node_id":"path2_kgmfqr5ldqs9lj3oscrgxqefc",
                                "target_capability_name":"feature"
                            }
                        ]
                    },
                    {
                        "id":"m600_tunnel_cp_imwfk5l48ljz0g9knc6d68hv5",
                        "type_name":"tosca.nodes.nfv.ext.zte.CP",
                        "template_name":"m600_tunnel_cp",
                        "properties":{
                            "direction":{
                                "type_name":"string",
                                "value":"bidirectional"
                            },
                            "vnic_type":{
                                "type_name":"string",
                                "value":"normal"
                            },
                            "bandwidth":{
                                "type_name":"integer",
                                "value":0
                            },
                            "mac_address":{
                                "type_name":"string",
                                "value":"00-11-00-22-33-00"
                            },
                            "interface_name":{
                                "type_name":"string",
                                "value":"gei-0/4/0/13"
                            },
                            "ip_address":{
                                "type_name":"string",
                                "value":"191.167.100.5"
                            },
                            "order":{
                                "type_name":"integer",
                                "value":0
                            },
                            "sfc_encapsulation":{
                                "type_name":"string",
                                "value":"mac"
                            }
                        },
                        "interfaces":[
                            {
                                "name":"Standard",
                                "description":"This lifecycle interface defines the essential, normative operations that TOSCA nodes may support.",
                                "type_name":"tosca.interfaces.node.lifecycle.Standard",
                                "operations":[
                                    {
                                        "name":"create",
                                        "description":"Standard lifecycle create operation."
                                    },
                                    {
                                        "name":"stop",
                                        "description":"Standard lifecycle stop operation."
                                    },
                                    {
                                        "name":"start",
                                        "description":"Standard lifecycle start operation."
                                    },
                                    {
                                        "name":"delete",
                                        "description":"Standard lifecycle delete operation."
                                    },
                                    {
                                        "name":"configure",
                                        "description":"Standard lifecycle configure operation."
                                    }
                                ]
                            }
                        ],
                        "capabilities":[
                            {
                                "name":"feature",
                                "type_name":"tosca.capabilities.Node"
                            },
                            {
                                "name":"forwarder",
                                "type_name":"tosca.capabilities.nfv.Forwarder"
                            }
                        ],
                        "relationships":[
                            {
                                "name":"virtualLink",
                                "source_requirement_index":0,
                                "target_node_id":"ext_datanet_net_qtqzlx5dsthzs883hxjn6hyhd",
                                "target_capability_name":"feature"
                            },
                            {
                                "name":"virtualbinding",
                                "source_requirement_index":1,
                                "target_node_id":"m6000_s_7qtzo5nuocyfmebc6kp9raq18",
                                "target_capability_name":"feature"
                            },
                            {
                                "name":"forwarder",
                                "source_requirement_index":2,
                                "target_node_id":"path2_kgmfqr5ldqs9lj3oscrgxqefc",
                                "target_capability_name":"feature"
                            }
                        ]
                    },
                    {
                        "id":"ext_mnet_net_au2otee5mcy0dnpqykj487zr3",
                        "type_name":"tosca.nodes.nfv.ext.VL.Vmware",
                        "template_name":"ext_mnet_net",
                        "properties":{
                            "name":{
                                "type_name":"string",
                                "value":"vlan_4008_mng_net"
                            },
                            "dhcp_enabled":{
                                "type_name":"boolean",
                                "value":True
                            },
                            "location_info":{
                                "type_name":"tosca.datatypes.nfv.ext.LocationInfo",
                                "value":{
                                    "tenant":"admin",
                                    "vimid":2,
                                    "availability_zone":"nova"
                                }
                            },
                            "ip_version":{
                                "type_name":"integer",
                                "value":4
                            },
                            "mtu":{
                                "type_name":"integer",
                                "value":1500
                            },
                            "network_name":{
                                "type_name":"string",
                                "value":"vlan_4008_mng_net"
                            },
                            "network_type":{
                                "type_name":"string",
                                "value":"vlan"
                            }
                        },
                        "interfaces":[
                            {
                                "name":"Standard",
                                "description":"This lifecycle interface defines the essential, normative operations that TOSCA nodes may support.",
                                "type_name":"tosca.interfaces.node.lifecycle.Standard",
                                "operations":[
                                    {
                                        "name":"create",
                                        "description":"Standard lifecycle create operation."
                                    },
                                    {
                                        "name":"stop",
                                        "description":"Standard lifecycle stop operation."
                                    },
                                    {
                                        "name":"start",
                                        "description":"Standard lifecycle start operation."
                                    },
                                    {
                                        "name":"delete",
                                        "description":"Standard lifecycle delete operation."
                                    },
                                    {
                                        "name":"configure",
                                        "description":"Standard lifecycle configure operation."
                                    }
                                ]
                            }
                        ],
                        "capabilities":[
                            {
                                "name":"feature",
                                "type_name":"tosca.capabilities.Node"
                            },
                            {
                                "name":"virtual_linkable",
                                "type_name":"tosca.capabilities.nfv.VirtualLinkable"
                            }
                        ]
                    },
                    {
                        "id":"m6000_data_in_eldly5txw4frny3cc349uz3nc",
                        "type_name":"tosca.nodes.nfv.ext.zte.CP",
                        "template_name":"m6000_data_in",
                        "properties":{
                            "direction":{
                                "type_name":"string",
                                "value":"bidirectional"
                            },
                            "vnic_type":{
                                "type_name":"string",
                                "value":"normal"
                            },
                            "bandwidth":{
                                "type_name":"integer",
                                "value":0
                            },
                            "mac_address":{
                                "type_name":"string",
                                "value":"11-22-33-22-11-41"
                            },
                            "interface_name":{
                                "type_name":"string",
                                "value":"gei-0/4/0/7"
                            },
                            "ip_address":{
                                "type_name":"string",
                                "value":"1.1.1.1"
                            },
                            "order":{
                                "type_name":"integer",
                                "value":0
                            },
                            "sfc_encapsulation":{
                                "type_name":"string",
                                "value":"mac"
                            },
                            "bond":{
                                "type_name":"string",
                                "value":"none"
                            }
                        },
                        "interfaces":[
                            {
                                "name":"Standard",
                                "description":"This lifecycle interface defines the essential, normative operations that TOSCA nodes may support.",
                                "type_name":"tosca.interfaces.node.lifecycle.Standard",
                                "operations":[
                                    {
                                        "name":"create",
                                        "description":"Standard lifecycle create operation."
                                    },
                                    {
                                        "name":"stop",
                                        "description":"Standard lifecycle stop operation."
                                    },
                                    {
                                        "name":"start",
                                        "description":"Standard lifecycle start operation."
                                    },
                                    {
                                        "name":"delete",
                                        "description":"Standard lifecycle delete operation."
                                    },
                                    {
                                        "name":"configure",
                                        "description":"Standard lifecycle configure operation."
                                    }
                                ]
                            }
                        ],
                        "capabilities":[
                            {
                                "name":"feature",
                                "type_name":"tosca.capabilities.Node"
                            },
                            {
                                "name":"forwarder",
                                "type_name":"tosca.capabilities.nfv.Forwarder"
                            }
                        ],
                        "relationships":[
                            {
                                "name":"virtualbinding",
                                "source_requirement_index":0,
                                "target_node_id":"m6000_s_7qtzo5nuocyfmebc6kp9raq18",
                                "target_capability_name":"feature"
                            },
                            {
                                "name":"virtualLink",
                                "source_requirement_index":1,
                                "target_node_id":"path2_kgmfqr5ldqs9lj3oscrgxqefc",
                                "target_capability_name":"feature"
                            },
                            {
                                "name":"forwarder",
                                "source_requirement_index":2,
                                "target_node_id":"path2_kgmfqr5ldqs9lj3oscrgxqefc",
                                "target_capability_name":"feature"
                            }
                        ]
                    },
                    {
                        "id":"ext_datanet_net_qtqzlx5dsthzs883hxjn6hyhd",
                        "type_name":"tosca.nodes.nfv.ext.VL.Vmware",
                        "template_name":"ext_datanet_net",
                        "properties":{
                            "name":{
                                "type_name":"string",
                                "value":"vlan_4004_tunnel_net"
                            },
                            "dhcp_enabled":{
                                "type_name":"boolean",
                                "value":True
                            },
                            "location_info":{
                                "type_name":"tosca.datatypes.nfv.ext.LocationInfo",
                                "value":{
                                    "tenant":"admin",
                                    "vimid":2,
                                    "availability_zone":"nova"
                                }
                            },
                            "ip_version":{
                                "type_name":"integer",
                                "value":4
                            },
                            "mtu":{
                                "type_name":"integer",
                                "value":1500
                            },
                            "network_name":{
                                "type_name":"string",
                                "value":"vlan_4004_tunnel_net"
                            },
                            "network_type":{
                                "type_name":"string",
                                "value":"vlan"
                            }
                        },
                        "interfaces":[
                            {
                                "name":"Standard",
                                "description":"This lifecycle interface defines the essential, normative operations that TOSCA nodes may support.",
                                "type_name":"tosca.interfaces.node.lifecycle.Standard",
                                "operations":[
                                    {
                                        "name":"create",
                                        "description":"Standard lifecycle create operation."
                                    },
                                    {
                                        "name":"stop",
                                        "description":"Standard lifecycle stop operation."
                                    },
                                    {
                                        "name":"start",
                                        "description":"Standard lifecycle start operation."
                                    },
                                    {
                                        "name":"delete",
                                        "description":"Standard lifecycle delete operation."
                                    },
                                    {
                                        "name":"configure",
                                        "description":"Standard lifecycle configure operation."
                                    }
                                ]
                            }
                        ],
                        "capabilities":[
                            {
                                "name":"feature",
                                "type_name":"tosca.capabilities.Node"
                            },
                            {
                                "name":"virtual_linkable",
                                "type_name":"tosca.capabilities.nfv.VirtualLinkable"
                            }
                        ]
                    },
                    {
                        "id":"m600_mnt_cp_l3488y2a8ilyfdn0l89ni4os7",
                        "type_name":"tosca.nodes.nfv.ext.zte.CP",
                        "template_name":"m600_mnt_cp",
                        "properties":{
                            "direction":{
                                "type_name":"string",
                                "value":"bidirectional"
                            },
                            "vnic_type":{
                                "type_name":"string",
                                "value":"normal"
                            },
                            "bandwidth":{
                                "type_name":"integer",
                                "value":0
                            },
                            "mac_address":{
                                "type_name":"string",
                                "value":"00-11-00-22-33-11"
                            },
                            "interface_name":{
                                "type_name":"string",
                                "value":"gei-0/4/0/1"
                            },
                            "ip_address":{
                                "type_name":"string",
                                "value":"10.46.244.51"
                            },
                            "order":{
                                "type_name":"integer",
                                "value":0
                            },
                            "sfc_encapsulation":{
                                "type_name":"string",
                                "value":"mac"
                            },
                            "bond":{
                                "type_name":"string",
                                "value":"none"
                            }
                        },
                        "interfaces":[
                            {
                                "name":"Standard",
                                "description":"This lifecycle interface defines the essential, normative operations that TOSCA nodes may support.",
                                "type_name":"tosca.interfaces.node.lifecycle.Standard",
                                "operations":[
                                    {
                                        "name":"create",
                                        "description":"Standard lifecycle create operation."
                                    },
                                    {
                                        "name":"stop",
                                        "description":"Standard lifecycle stop operation."
                                    },
                                    {
                                        "name":"start",
                                        "description":"Standard lifecycle start operation."
                                    },
                                    {
                                        "name":"delete",
                                        "description":"Standard lifecycle delete operation."
                                    },
                                    {
                                        "name":"configure",
                                        "description":"Standard lifecycle configure operation."
                                    }
                                ]
                            }
                        ],
                        "capabilities":[
                            {
                                "name":"feature",
                                "type_name":"tosca.capabilities.Node"
                            },
                            {
                                "name":"forwarder",
                                "type_name":"tosca.capabilities.nfv.Forwarder"
                            }
                        ],
                        "relationships":[
                            {
                                "name":"virtualLink",
                                "source_requirement_index":0,
                                "target_node_id":"ext_mnet_net_au2otee5mcy0dnpqykj487zr3",
                                "target_capability_name":"feature"
                            },
                            {
                                "name":"virtualbinding",
                                "source_requirement_index":1,
                                "target_node_id":"m6000_s_7qtzo5nuocyfmebc6kp9raq18",
                                "target_capability_name":"feature"
                            },
                            {
                                "name":"forwarder",
                                "source_requirement_index":2,
                                "target_node_id":"path2_kgmfqr5ldqs9lj3oscrgxqefc",
                                "target_capability_name":"feature"
                            }
                        ]
                    },
                    {
                        "id":"sfc_data_network_vx3pc1oahn0k0pa5q722yafee",
                        "type_name":"tosca.nodes.nfv.ext.zte.VL",
                        "template_name":"sfc_data_network",
                        "properties":{
                            "name":{
                                "type_name":"string",
                                "value":"sfc_data_network"
                            },
                            "dhcp_enabled":{
                                "type_name":"boolean",
                                "value":True
                            },
                            "is_predefined":{
                                "type_name":"boolean",
                                "value":False
                            },
                            "location_info":{
                                "type_name":"tosca.datatypes.nfv.ext.LocationInfo",
                                "value":{
                                    "tenant":"admin",
                                    "vimid":2,
                                    "availability_zone":"nova"
                                }
                            },
                            "ip_version":{
                                "type_name":"integer",
                                "value":4
                            },
                            "mtu":{
                                "type_name":"integer",
                                "value":1500
                            },
                            "network_name":{
                                "type_name":"string",
                                "value":"sfc_data_network"
                            },
                            "network_type":{
                                "type_name":"string",
                                "value":"vlan"
                            }
                        },
                        "interfaces":[
                            {
                                "name":"Standard",
                                "description":"This lifecycle interface defines the essential, normative operations that TOSCA nodes may support.",
                                "type_name":"tosca.interfaces.node.lifecycle.Standard",
                                "operations":[
                                    {
                                        "name":"create",
                                        "description":"Standard lifecycle create operation."
                                    },
                                    {
                                        "name":"stop",
                                        "description":"Standard lifecycle stop operation."
                                    },
                                    {
                                        "name":"start",
                                        "description":"Standard lifecycle start operation."
                                    },
                                    {
                                        "name":"delete",
                                        "description":"Standard lifecycle delete operation."
                                    },
                                    {
                                        "name":"configure",
                                        "description":"Standard lifecycle configure operation."
                                    }
                                ]
                            }
                        ],
                        "capabilities":[
                            {
                                "name":"feature",
                                "type_name":"tosca.capabilities.Node"
                            },
                            {
                                "name":"virtual_linkable",
                                "type_name":"tosca.capabilities.nfv.VirtualLinkable"
                            }
                        ]
                    },
                    {
                        "id":"m6000_s_7qtzo5nuocyfmebc6kp9raq18",
                        "type_name":"tosca.nodes.nfv.ext.PNF",
                        "template_name":"m6000_s",
                        "properties":{
                            "vendor":{
                                "type_name":"string",
                                "value":"zte"
                            },
                            "request_reclassification":{
                                "type_name":"boolean",
                                "value":False
                            },
                            "pnf_type":{
                                "type_name":"string",
                                "value":"m6000s"
                            },
                            "version":{
                                "type_name":"string",
                                "value":"1.0"
                            },
                            "management_address":{
                                "type_name":"string",
                                "value":"111111"
                            },
                            "id":{
                                "type_name":"string",
                                "value":"m6000_s"
                            },
                            "nsh_aware":{
                                "type_name":"boolean",
                                "value":False
                            }
                        },
                        "interfaces":[
                            {
                                "name":"Standard",
                                "description":"This lifecycle interface defines the essential, normative operations that TOSCA nodes may support.",
                                "type_name":"tosca.interfaces.node.lifecycle.Standard",
                                "operations":[
                                    {
                                        "name":"create",
                                        "description":"Standard lifecycle create operation."
                                    },
                                    {
                                        "name":"stop",
                                        "description":"Standard lifecycle stop operation."
                                    },
                                    {
                                        "name":"start",
                                        "description":"Standard lifecycle start operation."
                                    },
                                    {
                                        "name":"delete",
                                        "description":"Standard lifecycle delete operation."
                                    },
                                    {
                                        "name":"configure",
                                        "description":"Standard lifecycle configure operation."
                                    }
                                ]
                            }
                        ],
                        "capabilities":[
                            {
                                "name":"feature",
                                "type_name":"tosca.capabilities.Node"
                            },
                            {
                                "name":"virtualBinding",
                                "type_name":"tosca.capabilities.nfv.VirtualBindable"
                            },
                            {
                                "name":"forwarder",
                                "type_name":"tosca.capabilities.nfv.Forwarder"
                            }
                        ],
                        "relationships":[
                            {
                                "name":"forwarder",
                                "source_requirement_index":0,
                                "target_node_id":"path2_kgmfqr5ldqs9lj3oscrgxqefc",
                                "target_capability_name":"feature"
                            }
                        ]
                    },
                    {
                        "id":"VNAT_cfdljtspvkp234irka59wgab0",
                        "type_name":"tosca.nodes.nfv.ext.zte.VNF.VNAT",
                        "template_name":"VNAT",
                        "properties":{
                            "is_shared":{
                                "type_name":"boolean",
                                "value":False
                            },
                            "plugin_info":{
                                "type_name":"string",
                                "value":"vbrasplugin_1.0"
                            },
                            "vendor":{
                                "type_name":"string",
                                "value":"zte"
                            },
                            "request_reclassification":{
                                "type_name":"boolean",
                                "value":False
                            },
                            "name":{
                                "type_name":"string",
                                "value":"VNAT"
                            },
                            "vnf_extend_type":{
                                "type_name":"string",
                                "value":"driver"
                            },
                            "externalPluginManageNetworkName":{
                                "type_name":"string",
                                "value":"vlan_4007_plugin_net"
                            },
                            "version":{
                                "type_name":"string",
                                "value":"1.0"
                            },
                            "cross_dc":{
                                "type_name":"boolean",
                                "value":False
                            },
                            "vnf_type":{
                                "type_name":"string",
                                "value":"VNAT"
                            },
                            "vnfd_version":{
                                "type_name":"string",
                                "value":"1.0.0"
                            },
                            "id":{
                                "type_name":"string",
                                "value":"vcpe_vnat_zte_1"
                            },
                            "nsh_aware":{
                                "type_name":"boolean",
                                "value":True
                            },
                            "adjust_vnf_capacity":{
                                "type_name":"boolean",
                                "value":True
                            },
                            "vmnumber_overquota_alarm":{
                                "type_name":"boolean",
                                "value":True
                            },
                            "csarProvider":{
                                "type_name":"string",
                                "value":"ZTE"
                            },
                            "NatIpRange":{
                                "type_name":"string",
                                "value":"192.167.0.10-192.168.0.20"
                            },
                            "csarVersion":{
                                "type_name":"string",
                                "value":"v1.0"
                            },
                            "csarType":{
                                "type_name":"string",
                                "value":"NFAR"
                            }
                        },
                        "interfaces":[
                            {
                                "name":"Standard",
                                "description":"This lifecycle interface defines the essential, normative operations that TOSCA nodes may support.",
                                "type_name":"tosca.interfaces.node.lifecycle.Standard",
                                "operations":[
                                    {
                                        "name":"create",
                                        "description":"Standard lifecycle create operation."
                                    },
                                    {
                                        "name":"stop",
                                        "description":"Standard lifecycle stop operation."
                                    },
                                    {
                                        "name":"start",
                                        "description":"Standard lifecycle start operation."
                                    },
                                    {
                                        "name":"delete",
                                        "description":"Standard lifecycle delete operation."
                                    },
                                    {
                                        "name":"configure",
                                        "description":"Standard lifecycle configure operation."
                                    }
                                ]
                            }
                        ],
                        "capabilities":[
                            {
                                "name":"feature",
                                "type_name":"tosca.capabilities.Node"
                            },
                            {
                                "name":"forwarder",
                                "type_name":"tosca.capabilities.nfv.Forwarder"
                            },
                            {
                                "name":"vnat_fw_inout",
                                "type_name":"tosca.capabilities.nfv.Forwarder"
                            }
                        ],
                        "relationships":[
                            {
                                "name":"vnat_ctrl_by_manager_cp",
                                "source_requirement_index":0,
                                "target_node_id":"ext_mnet_net_au2otee5mcy0dnpqykj487zr3",
                                "target_capability_name":"feature"
                            },
                            {
                                "name":"vnat_data_cp",
                                "source_requirement_index":1,
                                "target_node_id":"sfc_data_network_vx3pc1oahn0k0pa5q722yafee",
                                "target_capability_name":"feature"
                            },
                            {
                                "name":"virtualLink",
                                "source_requirement_index":2,
                                "target_node_id":"path2_kgmfqr5ldqs9lj3oscrgxqefc",
                                "target_capability_name":"feature"
                            },
                            {
                                "name":"forwarder",
                                "source_requirement_index":3,
                                "target_node_id":"path2_kgmfqr5ldqs9lj3oscrgxqefc",
                                "target_capability_name":"feature"
                            }
                        ]
                    }
                ],
                "groups":[
                    {
                        "id":"vnffg1_wk1aqhk6exoh5fmds2unu0uyc",
                        "type_name":"tosca.groups.nfv.VNFFG",
                        "template_name":"vnffg1",
                        "properties":{
                            "vendor":{
                                "type_name":"string",
                                "value":"zte"
                            },
                            "connection_point":{
                                "type_name":"list",
                                "value":[
                                    "m6000_data_in",
                                    "m600_tunnel_cp",
                                    "m6000_data_out"
                                ]
                            },
                            "version":{
                                "type_name":"string",
                                "value":"1.0"
                            },
                            "constituent_vnfs":{
                                "type_name":"list",
                                "value":[
                                    "VFW",
                                    "VNAT"
                                ]
                            },
                            "number_of_endpoints":{
                                "type_name":"integer",
                                "value":3
                            },
                            "dependent_virtual_link":{
                                "type_name":"list",
                                "value":[
                                    "sfc_data_network",
                                    "ext_datanet_net",
                                    "ext_mnet_net"
                                ]
                            }
                        },
                        "interfaces":[
                            {
                                "name":"standard",
                                "description":"This lifecycle interface defines the essential, normative operations that TOSCA nodes may support.",
                                "type_name":"tosca.interfaces.node.lifecycle.Standard",
                                "operations":[
                                    {
                                        "name":"create",
                                        "description":"Standard lifecycle create operation."
                                    },
                                    {
                                        "name":"stop",
                                        "description":"Standard lifecycle stop operation."
                                    },
                                    {
                                        "name":"start",
                                        "description":"Standard lifecycle start operation."
                                    },
                                    {
                                        "name":"delete",
                                        "description":"Standard lifecycle delete operation."
                                    },
                                    {
                                        "name":"configure",
                                        "description":"Standard lifecycle configure operation."
                                    }
                                ]
                            }
                        ],
                        "member_node_ids":[
                            "path1_bv53fblv26hawr8dj4fxe2rsd",
                            "path2_kgmfqr5ldqs9lj3oscrgxqefc"
                        ]
                    }
                ],
                "substitution":{
                    "node_type_name":"tosca.nodes.nfv.NS.VCPE_NS"
                },
                "inputs":{
                    "externalDataNetworkName":{
                        "type_name":"string",
                        "value":"vlan_4004_tunnel_net"
                    },
                    "sfc_data_network":{
                        "type_name":"string",
                        "value":"sfc_data_network"
                    },
                    "NatIpRange":{
                        "type_name":"string",
                        "value":"192.167.0.10-192.168.0.20"
                    },
                    "externalManageNetworkName":{
                        "type_name":"string",
                        "value":"vlan_4008_mng_net"
                    },
                    "externalPluginManageNetworkName":{
                        "type_name":"string",
                        "value":"vlan_4007_plugin_net"
                    }
                }
            },
            "model":{
                "metadata":{
                    "vendor":"ZTE",
                    "name":"VCPE_NS",
                    "csarVersion":"v1.0",
                    "csarType":"NSAR",
                    "csarProvider":"ZTE",
                    "version":1,
                    "invariant_id":"vcpe_ns_sff_1",
                    "id":"VCPE_NS",
                    "description":"vcpe_ns"
                },
                "node_templates":[
                    {
                        "name":"path2",
                        "type_name":"tosca.nodes.nfv.ext.FP",
                        "default_instances":1,
                        "min_instances":0,
                        "properties":{
                            "symmetric":{
                                "type_name":"boolean",
                                "value":False
                            },
                            "policy":{
                                "type_name":"tosca.datatypes.nfv.ext.FPPolicy",
                                "value":{
                                    "type":"ACL",
                                    "criteria":{
                                        "dest_port_range":"1-100",
                                        "ip_protocol":"tcp",
                                        "source_ip_range":[
                                            "119.1.1.1-119.1.1.10"
                                        ],
                                        "dest_ip_range":[
                                            {"get_input":"NatIpRange"}
                                        ],
                                        "dscp":0,
                                        "source_port_range":"1-100"
                                    }
                                }
                            }
                        },
                        "interface_templates":[
                            "<aria.modeling.model_elements.InterfaceTemplate object at 0x7f8ed0288a10>"
                        ],
                        "capability_templates":[
                            {
                                "name":"feature",
                                "type_name":"tosca.capabilities.Node"
                            }
                        ],
                        "requirement_templates":[
                            {
                                "name":"forwarder",
                                "target_node_template_name":"m6000_data_out"
                            },
                            {
                                "name":"forwarder",
                                "target_node_template_name":"m600_tunnel_cp"
                            },
                            {
                                "name":"forwarder",
                                "target_node_template_name":"VNAT",
                                "target_capability_name":"vnat_fw_inout"
                            }
                        ]
                    },
                    {
                        "name":"path1",
                        "type_name":"tosca.nodes.nfv.ext.FP",
                        "default_instances":1,
                        "min_instances":0,
                        "properties":{
                            "symmetric":{
                                "type_name":"boolean",
                                "value":True
                            },
                            "policy":{
                                "type_name":"tosca.datatypes.nfv.ext.FPPolicy",
                                "value":{
                                    "type":"ACL",
                                    "criteria":{
                                        "dest_port_range":"1-100",
                                        "ip_protocol":"tcp",
                                        "source_ip_range":[
                                            "1-100"
                                        ],
                                        "dest_ip_range":[
                                            "1-100"
                                        ],
                                        "dscp":4,
                                        "source_port_range":"1-100"
                                    }
                                }
                            }
                        },
                        "interface_templates":[
                            "<aria.modeling.model_elements.InterfaceTemplate object at 0x7f8ec81df090>"
                        ],
                        "capability_templates":[
                            {
                                "name":"feature",
                                "type_name":"tosca.capabilities.Node"
                            }
                        ],
                        "requirement_templates":[
                            {
                                "name":"forwarder",
                                "target_node_template_name":"m6000_data_in"
                            },
                            {
                                "name":"forwarder",
                                "target_node_template_name":"m600_tunnel_cp"
                            },
                            {
                                "name":"forwarder",
                                "target_node_template_name":"VFW",
                                "target_capability_name":"vfw_fw_inout"
                            },
                            {
                                "name":"forwarder",
                                "target_node_template_name":"VNAT",
                                "target_capability_name":"vnat_fw_inout"
                            },
                            {
                                "name":"forwarder",
                                "target_node_template_name":"m600_tunnel_cp"
                            },
                            {
                                "name":"forwarder",
                                "target_node_template_name":"m6000_data_out"
                            }
                        ]
                    },
                    {
                        "name":"m6000_data_out",
                        "type_name":"tosca.nodes.nfv.ext.zte.CP",
                        "default_instances":1,
                        "min_instances":0,
                        "properties":{
                            "direction":{
                                "type_name":"string",
                                "value":"bidirectional"
                            },
                            "vnic_type":{
                                "type_name":"string",
                                "value":"normal"
                            },
                            "bandwidth":{
                                "type_name":"integer",
                                "value":0
                            },
                            "mac_address":{
                                "type_name":"string",
                                "value":"11-22-33-22-11-44"
                            },
                            "interface_name":{
                                "type_name":"string",
                                "value":"xgei-0/4/1/5"
                            },
                            "ip_address":{
                                "type_name":"string",
                                "value":"176.1.1.2"
                            },
                            "order":{
                                "type_name":"integer",
                                "value":0
                            },
                            "sfc_encapsulation":{
                                "type_name":"string",
                                "value":"mac"
                            }
                        },
                        "interface_templates":[
                            "<aria.modeling.model_elements.InterfaceTemplate object at 0x7f8ec82c6610>"
                        ],
                        "capability_templates":[
                            {
                                "name":"feature",
                                "type_name":"tosca.capabilities.Node"
                            },
                            {
                                "name":"forwarder",
                                "type_name":"tosca.capabilities.nfv.Forwarder"
                            }
                        ],
                        "requirement_templates":[
                            {
                                "name":"virtualbinding",
                                "target_node_template_name":"m6000_s",
                                "target_capability_name":"virtualBinding"
                            },
                            {
                                "name":"virtualLink",
                                "target_node_type_name":"tosca.nodes.Root"
                            },
                            {
                                "name":"forwarder",
                                "target_node_type_name":"tosca.nodes.Root"
                            }
                        ]
                    },
                    {
                        "name":"VFW",
                        "type_name":"tosca.nodes.nfv.ext.zte.VNF.VFW",
                        "default_instances":1,
                        "min_instances":0,
                        "properties":{
                            "is_shared":{
                                "type_name":"boolean",
                                "value":False
                            },
                            "plugin_info":{
                                "type_name":"string",
                                "value":"vbrasplugin_1.0"
                            },
                            "vendor":{
                                "type_name":"string",
                                "value":"zte"
                            },
                            "request_reclassification":{
                                "type_name":"boolean",
                                "value":False
                            },
                            "vnf_extend_type":{
                                "type_name":"string",
                                "value":"driver"
                            },
                            "name":{
                                "type_name":"string",
                                "value":"VFW"
                            },
                            "version":{
                                "type_name":"string",
                                "value":"1.0"
                            },
                            "cross_dc":{
                                "type_name":"boolean",
                                "value":False
                            },
                            "vnf_type":{
                                "type_name":"string",
                                "value":"VFW"
                            },
                            "vnfd_version":{
                                "type_name":"string",
                                "value":"1.0.0"
                            },
                            "id":{
                                "type_name":"string",
                                "value":"vcpe_vfw_zte_1_0"
                            },
                            "nsh_aware":{
                                "type_name":"boolean",
                                "value":True
                            },
                            "adjust_vnf_capacity":{
                                "type_name":"boolean",
                                "value":True
                            },
                            "vmnumber_overquota_alarm":{
                                "type_name":"boolean",
                                "value":True
                            },
                            "csarProvider":{
                                "type_name":"string",
                                "value":"ZTE"
                            },
                            "csarVersion":{
                                "type_name":"string",
                                "value":"v1.0"
                            },
                            "externalPluginManageNetworkName":{
                                "type_name":"string",
                                "value":"vlan_4007_plugin_net"
                            },
                            "csarType":{
                                "type_name":"string",
                                "value":"NFAR"
                            }
                        },
                        "interface_templates":[
                            "<aria.modeling.model_elements.InterfaceTemplate object at 0x7f8ec8281950>"
                        ],
                        "capability_templates":[
                            {
                                "name":"feature",
                                "type_name":"tosca.capabilities.Node"
                            },
                            {
                                "name":"forwarder",
                                "type_name":"tosca.capabilities.nfv.Forwarder"
                            },
                            {
                                "name":"vfw_fw_inout",
                                "type_name":"tosca.capabilities.nfv.Forwarder"
                            }
                        ],
                        "requirement_templates":[
                            {
                                "name":"vfw_ctrl_by_manager_cp",
                                "target_node_template_name":"ext_mnet_net",
                                "target_capability_name":"virtual_linkable"
                            },
                            {
                                "name":"vfw_data_cp",
                                "target_node_template_name":"sfc_data_network",
                                "target_capability_name":"virtual_linkable"
                            },
                            {
                                "name":"virtualLink",
                                "target_node_type_name":"tosca.nodes.Root"
                            },
                            {
                                "name":"forwarder",
                                "target_node_type_name":"tosca.nodes.Root"
                            }
                        ]
                    },
                    {
                        "name":"m600_tunnel_cp",
                        "type_name":"tosca.nodes.nfv.ext.zte.CP",
                        "default_instances":1,
                        "min_instances":0,
                        "properties":{
                            "direction":{
                                "type_name":"string",
                                "value":"bidirectional"
                            },
                            "vnic_type":{
                                "type_name":"string",
                                "value":"normal"
                            },
                            "bandwidth":{
                                "type_name":"integer",
                                "value":0
                            },
                            "mac_address":{
                                "type_name":"string",
                                "value":"00-11-00-22-33-00"
                            },
                            "interface_name":{
                                "type_name":"string",
                                "value":"gei-0/4/0/13"
                            },
                            "ip_address":{
                                "type_name":"string",
                                "value":"191.167.100.5"
                            },
                            "order":{
                                "type_name":"integer",
                                "value":0
                            },
                            "sfc_encapsulation":{
                                "type_name":"string",
                                "value":"mac"
                            }
                        },
                        "interface_templates":[
                            "<aria.modeling.model_elements.InterfaceTemplate object at 0x1ae39d0>"
                        ],
                        "capability_templates":[
                            {
                                "name":"feature",
                                "type_name":"tosca.capabilities.Node"
                            },
                            {
                                "name":"forwarder",
                                "type_name":"tosca.capabilities.nfv.Forwarder"
                            }
                        ],
                        "requirement_templates":[
                            {
                                "name":"virtualLink",
                                "target_node_template_name":"ext_datanet_net",
                                "target_capability_name":"virtual_linkable"
                            },
                            {
                                "name":"virtualbinding",
                                "target_node_template_name":"m6000_s",
                                "target_capability_name":"virtualBinding"
                            },
                            {
                                "name":"forwarder",
                                "target_node_type_name":"tosca.nodes.Root"
                            }
                        ]
                    },
                    {
                        "name":"ext_mnet_net",
                        "type_name":"tosca.nodes.nfv.ext.VL.Vmware",
                        "default_instances":1,
                        "min_instances":0,
                        "properties":{
                            "name":{
                                "type_name":"string",
                                "value":"vlan_4008_mng_net"
                            },
                            "dhcp_enabled":{
                                "type_name":"boolean",
                                "value":True
                            },
                            "location_info":{
                                "type_name":"tosca.datatypes.nfv.ext.LocationInfo",
                                "value":{
                                    "tenant":"admin",
                                    "vimid":2,
                                    "availability_zone":"nova"
                                }
                            },
                            "ip_version":{
                                "type_name":"integer",
                                "value":4
                            },
                            "mtu":{
                                "type_name":"integer",
                                "value":1500
                            },
                            "network_name":{
                                "type_name":"string",
                                "value":"vlan_4008_mng_net"
                            },
                            "network_type":{
                                "type_name":"string",
                                "value":"vlan"
                            }
                        },
                        "interface_templates":[
                            "<aria.modeling.model_elements.InterfaceTemplate object at 0x7f8ed00f89d0>"
                        ],
                        "capability_templates":[
                            {
                                "name":"feature",
                                "type_name":"tosca.capabilities.Node"
                            },
                            {
                                "name":"virtual_linkable",
                                "type_name":"tosca.capabilities.nfv.VirtualLinkable"
                            }
                        ]
                    },
                    {
                        "name":"m6000_data_in",
                        "type_name":"tosca.nodes.nfv.ext.zte.CP",
                        "default_instances":1,
                        "min_instances":0,
                        "properties":{
                            "direction":{
                                "type_name":"string",
                                "value":"bidirectional"
                            },
                            "vnic_type":{
                                "type_name":"string",
                                "value":"normal"
                            },
                            "bandwidth":{
                                "type_name":"integer",
                                "value":0
                            },
                            "mac_address":{
                                "type_name":"string",
                                "value":"11-22-33-22-11-41"
                            },
                            "interface_name":{
                                "type_name":"string",
                                "value":"gei-0/4/0/7"
                            },
                            "ip_address":{
                                "type_name":"string",
                                "value":"1.1.1.1"
                            },
                            "order":{
                                "type_name":"integer",
                                "value":0
                            },
                            "sfc_encapsulation":{
                                "type_name":"string",
                                "value":"mac"
                            },
                            "bond":{
                                "type_name":"string",
                                "value":"none"
                            }
                        },
                        "interface_templates":[
                            "<aria.modeling.model_elements.InterfaceTemplate object at 0x1745710>"
                        ],
                        "capability_templates":[
                            {
                                "name":"feature",
                                "type_name":"tosca.capabilities.Node"
                            },
                            {
                                "name":"forwarder",
                                "type_name":"tosca.capabilities.nfv.Forwarder"
                            }
                        ],
                        "requirement_templates":[
                            {
                                "name":"virtualbinding",
                                "target_node_template_name":"m6000_s",
                                "target_capability_name":"virtualBinding"
                            },
                            {
                                "name":"virtualLink",
                                "target_node_type_name":"tosca.nodes.Root"
                            },
                            {
                                "name":"forwarder",
                                "target_node_type_name":"tosca.nodes.Root"
                            }
                        ]
                    },
                    {
                        "name":"ext_datanet_net",
                        "type_name":"tosca.nodes.nfv.ext.VL.Vmware",
                        "default_instances":1,
                        "min_instances":0,
                        "properties":{
                            "name":{
                                "type_name":"string",
                                "value":"vlan_4004_tunnel_net"
                            },
                            "dhcp_enabled":{
                                "type_name":"boolean",
                                "value":True
                            },
                            "location_info":{
                                "type_name":"tosca.datatypes.nfv.ext.LocationInfo",
                                "value":{
                                    "tenant":"admin",
                                    "vimid":2,
                                    "availability_zone":"nova"
                                }
                            },
                            "ip_version":{
                                "type_name":"integer",
                                "value":4
                            },
                            "mtu":{
                                "type_name":"integer",
                                "value":1500
                            },
                            "network_name":{
                                "type_name":"string",
                                "value":"vlan_4004_tunnel_net"
                            },
                            "network_type":{
                                "type_name":"string",
                                "value":"vlan"
                            }
                        },
                        "interface_templates":[
                            "<aria.modeling.model_elements.InterfaceTemplate object at 0x7f8eac063990>"
                        ],
                        "capability_templates":[
                            {
                                "name":"feature",
                                "type_name":"tosca.capabilities.Node"
                            },
                            {
                                "name":"virtual_linkable",
                                "type_name":"tosca.capabilities.nfv.VirtualLinkable"
                            }
                        ]
                    },
                    {
                        "name":"m600_mnt_cp",
                        "type_name":"tosca.nodes.nfv.ext.zte.CP",
                        "default_instances":1,
                        "min_instances":0,
                        "properties":{
                            "direction":{
                                "type_name":"string",
                                "value":"bidirectional"
                            },
                            "vnic_type":{
                                "type_name":"string",
                                "value":"normal"
                            },
                            "bandwidth":{
                                "type_name":"integer",
                                "value":0
                            },
                            "mac_address":{
                                "type_name":"string",
                                "value":"00-11-00-22-33-11"
                            },
                            "interface_name":{
                                "type_name":"string",
                                "value":"gei-0/4/0/1"
                            },
                            "ip_address":{
                                "type_name":"string",
                                "value":"10.46.244.51"
                            },
                            "order":{
                                "type_name":"integer",
                                "value":0
                            },
                            "sfc_encapsulation":{
                                "type_name":"string",
                                "value":"mac"
                            },
                            "bond":{
                                "type_name":"string",
                                "value":"none"
                            }
                        },
                        "interface_templates":[
                            "<aria.modeling.model_elements.InterfaceTemplate object at 0x7f8ec81264d0>"
                        ],
                        "capability_templates":[
                            {
                                "name":"feature",
                                "type_name":"tosca.capabilities.Node"
                            },
                            {
                                "name":"forwarder",
                                "type_name":"tosca.capabilities.nfv.Forwarder"
                            }
                        ],
                        "requirement_templates":[
                            {
                                "name":"virtualLink",
                                "target_node_template_name":"ext_mnet_net",
                                "target_capability_name":"virtual_linkable"
                            },
                            {
                                "name":"virtualbinding",
                                "target_node_template_name":"m6000_s",
                                "target_capability_name":"virtualBinding"
                            },
                            {
                                "name":"forwarder",
                                "target_node_type_name":"tosca.nodes.Root"
                            }
                        ]
                    },
                    {
                        "name":"sfc_data_network",
                        "type_name":"tosca.nodes.nfv.ext.zte.VL",
                        "default_instances":1,
                        "min_instances":0,
                        "properties":{
                            "name":{
                                "type_name":"string",
                                "value":"sfc_data_network"
                            },
                            "dhcp_enabled":{
                                "type_name":"boolean",
                                "value":True
                            },
                            "is_predefined":{
                                "type_name":"boolean",
                                "value":False
                            },
                            "location_info":{
                                "type_name":"tosca.datatypes.nfv.ext.LocationInfo",
                                "value":{
                                    "tenant":"admin",
                                    "vimid":2,
                                    "availability_zone":"nova"
                                }
                            },
                            "ip_version":{
                                "type_name":"integer",
                                "value":4
                            },
                            "mtu":{
                                "type_name":"integer",
                                "value":1500
                            },
                            "network_name":{
                                "type_name":"string",
                                "value":"sfc_data_network"
                            },
                            "network_type":{
                                "type_name":"string",
                                "value":"vlan"
                            }
                        },
                        "interface_templates":[
                            "<aria.modeling.model_elements.InterfaceTemplate object at 0x7f8ec813c6d0>"
                        ],
                        "capability_templates":[
                            {
                                "name":"feature",
                                "type_name":"tosca.capabilities.Node"
                            },
                            {
                                "name":"virtual_linkable",
                                "type_name":"tosca.capabilities.nfv.VirtualLinkable"
                            }
                        ]
                    },
                    {
                        "name":"m6000_s",
                        "type_name":"tosca.nodes.nfv.ext.PNF",
                        "default_instances":1,
                        "min_instances":0,
                        "properties":{
                            "vendor":{
                                "type_name":"string",
                                "value":"zte"
                            },
                            "request_reclassification":{
                                "type_name":"boolean",
                                "value":False
                            },
                            "pnf_type":{
                                "type_name":"string",
                                "value":"m6000s"
                            },
                            "version":{
                                "type_name":"string",
                                "value":"1.0"
                            },
                            "management_address":{
                                "type_name":"string",
                                "value":"111111"
                            },
                            "id":{
                                "type_name":"string",
                                "value":"m6000_s"
                            },
                            "nsh_aware":{
                                "type_name":"boolean",
                                "value":False
                            }
                        },
                        "interface_templates":[
                            "<aria.modeling.model_elements.InterfaceTemplate object at 0x7f8ec8132490>"
                        ],
                        "capability_templates":[
                            {
                                "name":"feature",
                                "type_name":"tosca.capabilities.Node"
                            },
                            {
                                "name":"virtualBinding",
                                "type_name":"tosca.capabilities.nfv.VirtualBindable"
                            },
                            {
                                "name":"forwarder",
                                "type_name":"tosca.capabilities.nfv.Forwarder"
                            }
                        ],
                        "requirement_templates":[
                            {
                                "name":"forwarder",
                                "target_node_type_name":"tosca.nodes.Root"
                            }
                        ]
                    },
                    {
                        "name":"VNAT",
                        "type_name":"tosca.nodes.nfv.ext.zte.VNF.VNAT",
                        "default_instances":1,
                        "min_instances":0,
                        "properties":{
                            "is_shared":{
                                "type_name":"boolean",
                                "value":False
                            },
                            "plugin_info":{
                                "type_name":"string",
                                "value":"vbrasplugin_1.0"
                            },
                            "vendor":{
                                "type_name":"string",
                                "value":"zte"
                            },
                            "request_reclassification":{
                                "type_name":"boolean",
                                "value":False
                            },
                            "name":{
                                "type_name":"string",
                                "value":"VNAT"
                            },
                            "vnf_extend_type":{
                                "type_name":"string",
                                "value":"driver"
                            },
                            "externalPluginManageNetworkName":{
                                "type_name":"string",
                                "value":"vlan_4007_plugin_net"
                            },
                            "version":{
                                "type_name":"string",
                                "value":"1.0"
                            },
                            "cross_dc":{
                                "type_name":"boolean",
                                "value":False
                            },
                            "vnf_type":{
                                "type_name":"string",
                                "value":"VNAT"
                            },
                            "vnfd_version":{
                                "type_name":"string",
                                "value":"1.0.0"
                            },
                            "id":{
                                "type_name":"string",
                                "value":"vcpe_vnat_zte_1"
                            },
                            "nsh_aware":{
                                "type_name":"boolean",
                                "value":True
                            },
                            "adjust_vnf_capacity":{
                                "type_name":"boolean",
                                "value":True
                            },
                            "vmnumber_overquota_alarm":{
                                "type_name":"boolean",
                                "value":True
                            },
                            "csarProvider":{
                                "type_name":"string",
                                "value":"ZTE"
                            },
                            "NatIpRange":{
                                "type_name":"string",
                                "value":"192.167.0.10-192.168.0.20"
                            },
                            "csarVersion":{
                                "type_name":"string",
                                "value":"v1.0"
                            },
                            "csarType":{
                                "type_name":"string",
                                "value":"NFAR"
                            }
                        },
                        "interface_templates":[
                            "<aria.modeling.model_elements.InterfaceTemplate object at 0x1bba810>"
                        ],
                        "capability_templates":[
                            {
                                "name":"feature",
                                "type_name":"tosca.capabilities.Node"
                            },
                            {
                                "name":"forwarder",
                                "type_name":"tosca.capabilities.nfv.Forwarder"
                            },
                            {
                                "name":"vnat_fw_inout",
                                "type_name":"tosca.capabilities.nfv.Forwarder"
                            }
                        ],
                        "requirement_templates":[
                            {
                                "name":"vnat_ctrl_by_manager_cp",
                                "target_node_template_name":"ext_mnet_net",
                                "target_capability_name":"virtual_linkable"
                            },
                            {
                                "name":"vnat_data_cp",
                                "target_node_template_name":"sfc_data_network",
                                "target_capability_name":"virtual_linkable"
                            },
                            {
                                "name":"virtualLink",
                                "target_node_type_name":"tosca.nodes.Root"
                            },
                            {
                                "name":"forwarder",
                                "target_node_type_name":"tosca.nodes.Root"
                            }
                        ]
                    }
                ],
                "group_templates":[
                    {
                        "name":"vnffg1",
                        "type_name":"tosca.groups.nfv.VNFFG",
                        "properties":{
                            "vendor":{
                                "type_name":"string",
                                "value":"zte"
                            },
                            "connection_point":{
                                "type_name":"list",
                                "value":[
                                    "m6000_data_in",
                                    "m600_tunnel_cp",
                                    "m6000_data_out"
                                ]
                            },
                            "version":{
                                "type_name":"string",
                                "value":"1.0"
                            },
                            "constituent_vnfs":{
                                "type_name":"list",
                                "value":[
                                    "VFW",
                                    "VNAT"
                                ]
                            },
                            "number_of_endpoints":{
                                "type_name":"integer",
                                "value":3
                            },
                            "dependent_virtual_link":{
                                "type_name":"list",
                                "value":[
                                    "sfc_data_network",
                                    "ext_datanet_net",
                                    "ext_mnet_net"
                                ]
                            }
                        },
                        "interface_templates":[
                            "<aria.modeling.model_elements.InterfaceTemplate object at 0x7f8ec811cd10>"
                        ],
                        "member_node_template_names":[
                            "path1",
                            "path2"
                        ]
                    }
                ],
                "substitution_template":{
                    "node_type_name":"tosca.nodes.nfv.NS.VCPE_NS"
                },
                "inputs":{
                    "externalDataNetworkName":{
                        "type_name":"string",
                        "value":"vlan_4004_tunnel_net"
                    },
                    "sfc_data_network":{
                        "type_name":"string",
                        "value":"sfc_data_network"
                    },
                    "NatIpRange":{
                        "type_name":"string",
                        "value":"192.167.0.10-192.168.0.20"
                    },
                    "externalManageNetworkName":{
                        "type_name":"string",
                        "value":"vlan_4008_mng_net"
                    },
                    "externalPluginManageNetworkName":{
                        "type_name":"string",
                        "value":"vlan_4007_plugin_net"
                    }
                }
            }
        }
    )
    print convert_nsd_model(src_json)
