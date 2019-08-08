import json

vnfd_model_dict = {
    'local_storages': [
        {
            'local_storage_id': 'local_storage_id_001',
            'properties': {
                'size': '10 MB'
            }
        }
    ],
    'vdus': [
        {
            'volumn_storages': [

            ],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': '2'
            },
            'local_storages': [

            ],
            'vdu_id': 'vdu_omm.001',
            'image_file': 'opencos_sss_omm_img_release_20150723-1-disk1',
            'dependencies': [

            ],
            'vls': [

            ],
            'cps': [

            ],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''
                },
                'inject_data_list': [

                ],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''
                },
                'local_affinity_antiaffinity_rule': {

                },
                'template_id': 'omm.001',
                'manual_scale_select_vim': False
            },
            'description': 'singleommvm'
        },
        {
            'volumn_storages': [

            ],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': '4'
            },
            'local_storages': [

            ],
            'vdu_id': 'vdu_1',
            'image_file': 'sss',
            'dependencies': [

            ],
            'vls': [

            ],
            'cps': [

            ],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''
                },
                'inject_data_list': [

                ],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''
                },
                'local_affinity_antiaffinity_rule': {

                },
                'template_id': '1',
                'manual_scale_select_vim': False
            },
            'description': 'ompvm'
        },
        {
            'volumn_storages': [

            ],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': '14'
            },
            'local_storages': [

            ],
            'vdu_id': 'vdu_2',
            'image_file': 'sss',
            'dependencies': [

            ],
            'vls': [

            ],
            'cps': [

            ],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''
                },
                'inject_data_list': [

                ],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''
                },
                'local_affinity_antiaffinity_rule': {

                },
                'template_id': '2',
                'manual_scale_select_vim': False
            },
            'description': 'ompvm'
        },
        {
            'volumn_storages': [

            ],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': '14'
            },
            'local_storages': [

            ],
            'vdu_id': 'vdu_3',
            'image_file': 'sss',
            'dependencies': [

            ],
            'vls': [

            ],
            'cps': [

            ],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''
                },
                'inject_data_list': [

                ],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''
                },
                'local_affinity_antiaffinity_rule': {

                },
                'template_id': '3',
                'manual_scale_select_vim': False
            },
            'description': 'ompvm'
        },
        {
            'volumn_storages': [

            ],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': '4'
            },
            'local_storages': [

            ],
            'vdu_id': 'vdu_10',
            'image_file': 'sss',
            'dependencies': [

            ],
            'vls': [

            ],
            'cps': [

            ],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''
                },
                'inject_data_list': [

                ],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''
                },
                'local_affinity_antiaffinity_rule': {

                },
                'template_id': '10',
                'manual_scale_select_vim': False
            },
            'description': 'ppvm'
        },
        {
            'volumn_storages': [

            ],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': '14'
            },
            'local_storages': [

            ],
            'vdu_id': 'vdu_11',
            'image_file': 'sss',
            'dependencies': [

            ],
            'vls': [

            ],
            'cps': [

            ],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''
                },
                'inject_data_list': [

                ],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''
                },
                'local_affinity_antiaffinity_rule': {

                },
                'template_id': '11',
                'manual_scale_select_vim': False
            },
            'description': 'ppvm'
        },
        {
            'volumn_storages': [

            ],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': '14'
            },
            'local_storages': [

            ],
            'vdu_id': 'vdu_12',
            'image_file': 'sss',
            'dependencies': [

            ],
            'vls': [

            ],
            'cps': [

            ],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''
                },
                'inject_data_list': [

                ],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''
                },
                'local_affinity_antiaffinity_rule': {

                },
                'template_id': '12',
                'manual_scale_select_vim': False
            },
            'description': 'ppvm'
        },
        {
            'local_storages': ['local_storage_id_001'],
            'vdu_id': 'vdu_grant_vnf_add_resources',
            'properties': {'name': ''},
            'virtual_compute': {
                'virtual_cpu': {'num_virtual_cpu': 5},
                'virtual_memory': {'virtual_mem_size': '10'}
            }
        },
        {
            'local_storages': ['local_storage_id_001'],
            'vdu_id': 'vdu_grant_vnf_remove_resources',
            'properties': {'name': ''},
            'virtual_compute': {
                'virtual_cpu': {'num_virtual_cpu': 5},
                'virtual_memory': {'virtual_mem_size': '10'}
            }
        },
        {
            'local_storages': ['local_storage_id_001'],
            'vdu_id': 'vdu_name_test_grant_vnfs',
            'properties': {'name': ''},
            'virtual_compute': {
                'virtual_cpu': {'num_virtual_cpu': 5},
                'virtual_memory': {'virtual_mem_size': '10'}
            }
        }
    ],
    'volumn_storages': [

    ],
    'policies': {
        'scaling': {
            'targets': {

            },
            'policy_id': 'policy_scale_sss-vnf-template',
            'properties': {
                'policy_file': '*-vnfd.zip/*-vnf-policy.xml'
            },
            'description': ''
        }
    },
    'image_files': [
        {
            'description': '',
            'properties': {
                'name': 'opencos_sss_omm_img_release_20150723-1-disk1.vmdk',
                'checksum': '',
                'disk_format': 'VMDK',
                'file_url': './zte-cn-sss-main-image/OMM/opencos_sss_omm_img_release_20150723-1-disk1.vmdk',
                'container_type': 'vm',
                'version': '',
                'hypervisor_type': 'kvm'
            },
            'image_file_id': 'opencos_sss_omm_img_release_20150723-1-disk1'
        },
        {
            'description': '',
            'properties': {
                'name': 'sss.vmdk',
                'checksum': '',
                'disk_format': 'VMDK',
                'file_url': './zte-cn-sss-main-image/NE/sss.vmdk',
                'container_type': 'vm',
                'version': '',
                'hypervisor_type': 'kvm'
            },
            'image_file_id': 'sss'
        }
    ],
    'vls': [

    ],
    'cps': [

    ],
    'metadata': {
        'vendor': 'zte',
        'is_shared': False,
        'description': '',
        'domain_type': 'CN',
        'version': 'v4.14.10',
        'vmnumber_overquota_alarm': False,
        'cross_dc': False,
        'vnf_type': 'SSS',
        'vnfd_version': 'V00000001',
        'id': 'sss-vnf-template',
        'name': 'sss-vnf-template'
    },
    'vnf_exposed': {
        'external_cps': [
            {
                'key_name': 'vl_id_001_key_name',
                'cpd_id': 'cpd_id_001'
            }
        ]
    }
}

nsd_model_dict = {
    "vnffgs": [

    ],
    "inputs": {
        "externalDataNetworkName": {
            "default": "",
            "type": "string",
            "description": ""
        }
    },
    "pnfs": [

    ],
    "fps": [

    ],
    "server_groups": [

    ],
    "ns_flavours": [

    ],
    "vnfs": [
        {
            "dependency": [

            ],
            "properties": {
                "plugin_info": "vbrasplugin_1.0",
                "vendor": "zte",
                "is_shared": "False",
                "request_reclassification": "False",
                "vnfd_version": "1.0.0",
                "version": "1.0",
                "nsh_aware": "True",
                "cross_dc": "False",
                "externalDataNetworkName": {
                    "get_input": "externalDataNetworkName"
                },
                "id": "zte_vbras",
                "name": "vbras"
            },
            "vnf_id": "VBras",
            "networks": [
                {
                    "vl_id": "ext_mnet_network",
                    "key_name": "vl_id_001_key_name"
                }
            ],
            "description": ""
        }
    ],
    "ns_exposed": {
        "external_cps": [

        ],
        "forward_cps": [

        ]
    },
    "vls": [
        {
            "vl_id": "ext_mnet_network",
            "description": "",
            "properties": {
                "network_type": "vlan",
                "name": "externalMNetworkName",
                "dhcp_enabled": False,
                "location_info": {
                    "host": True,
                    "vimid": 2,
                    "region": True,
                    "tenant": "admin",
                    "dc": ""
                },
                "end_ip": "190.168.100.100",
                "gateway_ip": "190.168.100.1",
                "start_ip": "190.168.100.2",
                "cidr": "190.168.100.0/24",
                "mtu": 1500,
                "network_name": "sub_mnet",
                "ip_version": 4,
                "vl_profile": {
                    "networkName": "networkName"
                }
            }
        }
    ],
    "cps": [

    ],
    "policies": [

    ],
    "metadata": {
        "invariant_id": "vbras_ns",
        "description": "vbras_ns",
        "version": 1,
        "vendor": "zte",
        "id": "vbras_ns",
        "name": "vbras_ns"
    }
}

vserver_info = {
    "vserver-id": "example-vserver-id-val-70924",
    "vserver-name": "example-vserver-name-val-61674",
    "vserver-name2": "example-vserver-name2-val-19234",
    "prov-status": "example-prov-status-val-94916",
    "vserver-selflink": "example-vserver-selflink-val-26562",
    "in-maint": True,
    "is-closed-loop-disabled": True,
    "resource-version": "1505465356263",
    "volumes": {
        "volume": [
            {
                "volume-id": "example-volume-id-val-71854",
                "volume-selflink": "example-volume-selflink-val-22433"
            }
        ]
    },
    "l-interfaces": {
        "l-interface": [
            {
                "interface-name": "example-interface-name-val-24351",
                "interface-role": "example-interface-role-val-43242",
                "v6-wan-link-ip": "example-v6-wan-link-ip-val-4196",
                "selflink": "example-selflink-val-61295",
                "interface-id": "example-interface-id-val-95879",
                "macaddr": "example-macaddr-val-37302",
                "network-name": "example-network-name-val-44254",
                "management-option": "example-management-option-val-49009",
                "interface-description": "example-interface-description-val-99923",
                "is-port-mirrored": True,
                "in-maint": True,
                "prov-status": "example-prov-status-val-4698",
                "is-ip-unnumbered": True,
                "allowed-address-pairs": "example-allowed-address-pairs-val-5762",
                "vlans": {
                    "vlan": [
                        {
                            "vlan-interface": "example-vlan-interface-val-58193",
                            "vlan-id-inner": 54452151,
                            "vlan-id-outer": 70239293,
                            "speed-value": "example-speed-value-val-18677",
                            "speed-units": "example-speed-units-val-46185",
                            "vlan-description": "example-vlan-description-val-81675",
                            "backdoor-connection": "example-backdoor-connection-val-44608",
                            "vpn-key": "example-vpn-key-val-7946",
                            "orchestration-status": "example-orchestration-status-val-33611",
                            "in-maint": True,
                            "prov-status": "example-prov-status-val-8288",
                            "is-ip-unnumbered": True,
                            "l3-interface-ipv4-address-list": [
                                {
                                    "l3-interface-ipv4-address": "example-l3-interface-ipv4-address-val-25520",
                                    "l3-interface-ipv4-prefix-length": 69931928,
                                    "vlan-id-inner": 86628520,
                                    "vlan-id-outer": 62729236,
                                    "is-floating": True,
                                    "neutron-network-id": "example-neutron-network-id-val-64021",
                                    "neutron-subnet-id": "example-neutron-subnet-id-val-95049"
                                }
                            ],
                            "l3-interface-ipv6-address-list": [
                                {
                                    "l3-interface-ipv6-address": "example-l3-interface-ipv6-address-val-64310",
                                    "l3-interface-ipv6-prefix-length": 57919834,
                                    "vlan-id-inner": 79150122,
                                    "vlan-id-outer": 59789973,
                                    "is-floating": True,
                                    "neutron-network-id": "example-neutron-network-id-val-31713",
                                    "neutron-subnet-id": "example-neutron-subnet-id-val-89568"
                                }
                            ]
                        }
                    ]
                },
                "sriov-vfs": {
                    "sriov-vf": [
                        {
                            "pci-id": "example-pci-id-val-16747",
                            "vf-vlan-filter": "example-vf-vlan-filter-val-4613",
                            "vf-mac-filter": "example-vf-mac-filter-val-68168",
                            "vf-vlan-strip": True,
                            "vf-vlan-anti-spoof-check": True,
                            "vf-mac-anti-spoof-check": True,
                            "vf-mirrors": "example-vf-mirrors-val-6270",
                            "vf-broadcast-allow": True,
                            "vf-unknown-multicast-allow": True,
                            "vf-unknown-unicast-allow": True,
                            "vf-insert-stag": True,
                            "vf-link-status": "example-vf-link-status-val-49266",
                            "neutron-network-id": "example-neutron-network-id-val-29493"
                        }
                    ]
                },
                "l-interfaces": {
                    "l-interface": [
                        {
                            "interface-name": "example-interface-name-val-98222",
                            "interface-role": "example-interface-role-val-78360",
                            "v6-wan-link-ip": "example-v6-wan-link-ip-val-76921",
                            "selflink": "example-selflink-val-27117",
                            "interface-id": "example-interface-id-val-11260",
                            "macaddr": "example-macaddr-val-60378",
                            "network-name": "example-network-name-val-16258",
                            "management-option": "example-management-option-val-35097",
                            "interface-description": "example-interface-description-val-10475",
                            "is-port-mirrored": True,
                            "in-maint": True,
                            "prov-status": "example-prov-status-val-65203",
                            "is-ip-unnumbered": True,
                            "allowed-address-pairs": "example-allowed-address-pairs-val-65028"
                        }
                    ]
                },
                "l3-interface-ipv4-address-list": [
                    {
                        "l3-interface-ipv4-address": "example-l3-interface-ipv4-address-val-72779",
                        "l3-interface-ipv4-prefix-length": 55956636,
                        "vlan-id-inner": 98174431,
                        "vlan-id-outer": 20372128,
                        "is-floating": True,
                        "neutron-network-id": "example-neutron-network-id-val-39596",
                        "neutron-subnet-id": "example-neutron-subnet-id-val-51109"
                    }
                ],
                "l3-interface-ipv6-address-list": [
                    {
                        "l3-interface-ipv6-address": "example-l3-interface-ipv6-address-val-95203",
                        "l3-interface-ipv6-prefix-length": 57454747,
                        "vlan-id-inner": 53421060,
                        "vlan-id-outer": 16006050,
                        "is-floating": True,
                        "neutron-network-id": "example-neutron-network-id-val-54216",
                        "neutron-subnet-id": "example-neutron-subnet-id-val-1841"
                    }
                ]
            }
        ]
    }
}


vnfm_info = {
    "vnfm-id": "example-vnfm-id-val-97336",
    "vim-id": "zte_test",
    "certificate-url": "example-certificate-url-val-18046",
    "resource-version": "example-resource-version-val-42094",
    "esr-system-info-list": {
        "esr-system-info": [
            {
                "esr-system-info-id": "example-esr-system-info-id-val-7713",
                "system-name": "example-system-name-val-19801",
                "type": "ztevnfmdriver",
                "vendor": "example-vendor-val-50079",
                "version": "example-version-val-93146",
                "service-url": "example-service-url-val-68090",
                "user-name": "example-user-name-val-14470",
                "password": "example-password-val-84190",
                "system-type": "example-system-type-val-42773",
                "protocal": "example-protocal-val-85736",
                "ssl-cacert": "example-ssl-cacert-val-33989",
                "ssl-insecure": True,
                "ip-address": "example-ip-address-val-99038",
                "port": "example-port-val-27323",
                "cloud-domain": "example-cloud-domain-val-55163",
                "default-tenant": "example-default-tenant-val-99383",
                "resource-version": "example-resource-version-val-15424"
            }
        ]
    }
}

vim_info = {
    "cloud-owner": "example-cloud-owner-val-97336",
    "cloud-region-id": "example-cloud-region-id-val-35532",
    "cloud-type": "example-cloud-type-val-18046",
    "owner-defined-type": "example-owner-defined-type-val-9413",
    "cloud-region-version": "example-cloud-region-version-val-85706",
    "identity-url": "example-identity-url-val-71252",
    "cloud-zone": "example-cloud-zone-val-27112",
    "complex-name": "example-complex-name-val-85283",
    "sriov-automation": True,
    "cloud-extra-info": "example-cloud-extra-info-val-90854",
    "cloud-epa-caps": "example-cloud-epa-caps-val-2409",
    "resource-version": "example-resource-version-val-42094",
    "esr-system-info-list": {
        "esr-system-info": [
            {
                "esr-system-info-id": "example-esr-system-info-id-val-7713",
                "system-name": "example-system-name-val-19801",
                "type": "example-type-val-24477",
                "vendor": "example-vendor-val-50079",
                "version": "example-version-val-93146",
                "service-url": "example-service-url-val-68090",
                "user-name": "example-user-name-val-14470",
                "password": "example-password-val-84190",
                "system-type": "example-system-type-val-42773",
                "protocal": "example-protocal-val-85736",
                "ssl-cacert": "example-ssl-cacert-val-33989",
                "ssl-insecure": True,
                "ip-address": "example-ip-address-val-99038",
                "port": "example-port-val-27323",
                "cloud-domain": "example-cloud-domain-val-55163",
                "default-tenant": "admin",
                "resource-version": "example-resource-version-val-15424"
            }
        ]
    }
}

nf_package_info = {
    "csarId": "zte_vbras",
    "packageInfo": {
        "vnfdId": "1",
        "vnfPackageId": "zte_vbras",
        "vnfdProvider": "1",
        "vnfdVersion": "1",
        "vnfVersion": "1",
        "csarName": "1",
        "vnfdModel": json.dumps(vnfd_model_dict),
        "downloadUrl": "1"
    },
    "imageInfo": []
}

vnf_place_request = {
    "requestId": "1234",
    "transactionId": "1234",
    "statusMessage": "xx",
    "requestStatus": "completed",
    "solutions": {
        "placementSolutions": [
            [
                {
                    "resourceModuleName": "vG",
                    "serviceResourceId": "1234",
                    "solution": {
                        "identifierType": "serviceInstanceId",
                        "identifiers": [
                            "xx"
                        ],
                        "cloudOwner": "CloudOwner1"
                    },
                    "assignmentInfo": [
                        {"key": "isRehome",
                         "value": "false"
                         },
                        {"key": "locationId",
                         "value": "DLLSTX1A"
                         },
                        {"key": "locationType",
                         "value": "openstack-cloud"
                         },
                        {"key": "vimId",
                         "value": "CloudOwner1_DLLSTX1A"
                         },
                        {"key": "physicalLocationId",
                         "value": "DLLSTX1223"
                         },
                        {"key": "oof_directives",
                         "value": {
                             "directives": [
                                 {
                                     "id": "vG_0",
                                     "type": "tosca.nodes.nfv.Vdu.Compute",
                                     "directives": [
                                         {
                                             "type": "flavor_directives",
                                             "attributes": [
                                                 {
                                                     "attribute_name": "flavorName",
                                                     "attribute_value": "HPA.flavor.1"
                                                 },
                                                 {
                                                     "attribute_name": "flavorId",
                                                     "attribute_value": "12345"
                                                 },
                                             ]
                                         }
                                     ]
                                 },
                                 {
                                     "id": "",
                                     "type": "vnf",
                                     "directives": [
                                         {"type": " ",
                                          "attributes": [
                                              {
                                                  "attribute_name": " ",
                                                  "attribute_value": " "
                                              }
                                          ]
                                          }
                                     ]
                                 }
                             ]
                         }
                         }
                    ]
                }
            ]
        ],
        "licenseSolutions": [
            {
                "resourceModuleName": "string",
                "serviceResourceId": "string",
                "entitlementPoolUUID": [
                    "string"
                ],
                "licenseKeyGroupUUID": [
                    "string"
                ],
                "entitlementPoolInvariantUUID": [
                    "string"
                ],
                "licenseKeyGroupInvariantUUID": [
                    "string"
                ]
            }
        ]
    }
}

subscription_response_data = {
    "id": "subscription_id_1",
    "filter": {
        "notificationTypes": "notificationTypes",
        "operationTypes": "operationTypes",
        "operationStates": "operationStates",
        "vnfInstanceSubscriptionFilter": "vnfInstanceSubscriptionFilter"
    },
    "callbackUri": "callback_uri",
    "_links": "_links"
}
