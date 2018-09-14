# Copyright 2018 ZTE Corporation.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

GRANT_DATA = {
    'vnfInstanceId': '1',
    'vnfLcmOpOccId': '2',
    'vnfdId': '3',
    'flavourId': '4',
    'operation': 'INSTANTIATE',
    'isAutomaticInvocation': True,
    'instantiationLevelId': '5',
    'addResources': [
        {
            'id': '1',
            'type': 'COMPUTE',
            'vduId': '2',
            'resourceTemplateId': '3',
            'resourceTemplate': {
                'vimConnectionId': '4',
                'resourceProviderId': '5',
                'resourceId': '6',
                'vimLevelResourceType': '7'
            }
        }
    ],
    'placementConstraints': [
        {
            'affinityOrAntiAffinity': 'AFFINITY',
            'scope': 'NFVI_POP',
            'resource': [
                {
                    'idType': 'RES_MGMT',
                    'resourceId': '1',
                    'vimConnectionId': '2',
                    'resourceProviderId': '3'
                }
            ]
        }
    ],
    'vimConstraints': [
        {
            'sameResourceGroup': True,
            'resource': [
                {
                    'idType': 'RES_MGMT',
                    'resourceId': '1',
                    'vimConnectionId': '2',
                    'resourceProviderId': '3'
                }
            ]
        }
    ],
    'additionalParams': {},
    '_links': {
        'vnfLcmOpOcc': {
            'href': '1'
        },
        'vnfInstance': {
            'href': '2'
        }
    }
}

VNF_LCM_OP_OCC_NOTIFICATION_DATA = {
    'id': 'string',
    'notificationType': 'VnfLcmOperationOccurrenceNotification',
    'subscriptionId': 'string',
    'timeStamp': 'string',
    'notificationStatus': 'START',
    'operationState': 'STARTING',
    'vnfInstanceId': 'string',
    'operation': 'INSTANTIATE',
    'isAutomaticInvocation': True,
    'vnfLcmOpOccId': 'string',
    'affectedVnfcs': [{
        'id': 'string',
        'vduId': 'string',
        'changeType': 'ADDED',
        'computeResource': {
            'vimConnectionId': 'string',
            'resourceProviderId': 'string',
            'resourceId': 'string',
            'vimLevelResourceType': 'string'
        },
        'metadata': {},
        'affectedVnfcCpIds': [],
        'addedStorageResourceIds': [],
        'removedStorageResourceIds': [],
    }],
    'affectedVirtualLinks': [{
        'id': 'string',
        'virtualLinkDescId': 'string',
        'changeType': 'ADDED',
        'networkResource': {
            'vimConnectionId': 'string',
            'resourceProviderId': 'string',
            'resourceId': 'string',
            'vimLevelResourceType': 'network',
        }
    }],
    'affectedVirtualStorages': [{
        'id': 'string',
        'virtualStorageDescId': 'string',
        'changeType': 'ADDED',
        'storageResource': {
            'vimConnectionId': 'string',
            'resourceProviderId': 'string',
            'resourceId': 'string',
            'vimLevelResourceType': 'network',
        },
        'metadata': {}
    }],
    'changedInfo': {
        'vnfInstanceName': 'string',
        'vnfInstanceDescription': 'string',
        'vnfConfigurableProperties': {
            'additionalProp1': 'string',
            'additionalProp2': 'string',
            'additionalProp3': 'string'
        },
        'metadata': {
            'additionalProp1': 'string',
            'additionalProp2': 'string',
            'additionalProp3': 'string'
        },
        'extensions': {
            'additionalProp1': 'string',
            'additionalProp2': 'string',
            'additionalProp3': 'string'
        },
        'vimConnectionInfo': [{
            'id': 'string',
            'vimId': 'string',
            'vimType': 'string',
            'interfaceInfo': {
                'additionalProp1': 'string',
                'additionalProp2': 'string',
                'additionalProp3': 'string'
            },
            'accessInfo': {
                'additionalProp1': 'string',
                'additionalProp2': 'string',
                'additionalProp3': 'string'
            },
            'extra': {
                'additionalProp1': 'string',
                'additionalProp2': 'string',
                'additionalProp3': 'string'
            }
        }],
        'vnfPkgId': 'string',
        'vnfdId': 'string',
        'vnfProvider': 'string',
        'vnfProductName': 'string',
        'vnfSoftwareVersion': 'string',
        'vnfdVersion': 'string'
    },
    'changedExtConnectivity': [{
        'id': 'string',
        'resourceHandle': {
            'vimConnectionId': 'string',
            'resourceProviderId': 'string',
            'resourceId': 'string',
            'vimLevelResourceType': 'string'
        },
        'extLinkPorts': [{
            'id': 'string',
            'resourceHandle': {
                'vimConnectionId': 'string',
                'resourceProviderId': 'string',
                'resourceId': 'string',
                'vimLevelResourceType': 'string'
            },
            'cpInstanceId': 'string'
        }]
    }],
    'error': {
        'type': 'string',
        'title': 'string',
        'status': 0,
        'detail': 'string',
        'instance': 'string'
    },
    '_links': {
        'vnfInstance': {'href': 'string'},
        'subscription': {'href': 'string'},
        'vnfLcmOpOcc': {'href': 'string'}
    }
}

VNF_IDENTIFIER_CREATION_NOTIFICATION_DATA = {
    'id': 'Identifier of this notification',
    'notificationType': 'VnfIdentifierCreationNotification',
    'subscriptionId': 'Identifier of the subscription',
    'timeStamp': '2018-9-12T00:00:00',
    'vnfInstanceId': '2',
    '_links': {
        'vnfInstance': {'href': 'URI of the referenced resource'},
        'subscription': {'href': 'URI of the referenced resource'},
        'vnfLcmOpOcc': {'href': 'URI of the referenced resource'}
    }
}

VNF_IDENTIFIER_DELETION_NOTIFICATION_DATA = {
    'id': 'Identifier of this notification',
    'notificationType': 'VnfIdentifierDeletionNotification',
    'subscriptionId': 'Identifier of the subscription',
    'timeStamp': '2018-9-12T00:00:00',
    'vnfInstanceId': '2',
    '_links': {
        'vnfInstance': {'href': 'URI of the referenced resource'},
        'subscription': {'href': 'URI of the referenced resource'},
        'vnfLcmOpOcc': {'href': 'URI of the referenced resource'}
    }
}
