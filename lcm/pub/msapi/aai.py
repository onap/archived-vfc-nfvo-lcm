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
import logging
import uuid

from lcm.pub.config.config import AAI_BASE_URL, AAI_USER, AAI_PASSWD
from lcm.pub.exceptions import NSLCMException, RequestException
from lcm.pub.utils import restcall


logger = logging.getLogger(__name__)


def call_aai(resource, method, content=''):
    additional_headers = {
        'X-FromAppId': 'VFC-NFVO-LCM',
        'X-TransactionId': str(uuid.uuid1())
    }

    return restcall.call_req(AAI_BASE_URL,
                             AAI_USER,
                             AAI_PASSWD,
                             restcall.rest_no_auth,
                             resource,
                             method,
                             content,
                             additional_headers)


def create_customer_aai(global_customer_id, data):
    resource = "/business/customers/customer/%s" % global_customer_id
    data = json.JSONEncoder().encode(data)
    ret = call_aai(resource, "PUT", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Customer creation exception in AAI")
    return json.JSONDecoder().decode(ret[1]) if ret[1] else ret[1], ret[2]


def query_customer_aai(global_customer_id):
    resource = "/business/customers/customer/%s?depth=all" % global_customer_id
    ret = call_aai(resource, "GET")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Get customer info exception in AAI")
    return json.JSONDecoder().decode(ret[1]) if ret[1] else ret[1]


def delete_customer_aai(global_customer_id, resource_version=""):
    resource = "/business/customers/customer/%s" % global_customer_id
    if resource_version:
        resource = resource + "?resource-version=%s" % resource_version
    ret = call_aai(resource, "DELETE")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Customer delete exception in AAI")
    return json.JSONDecoder().decode(ret[1]) if ret[1] else ret[1], ret[2]


def put_customer_relationship(global_customer_id, data):
    resource = "/business/customers/customer/{global-customer-id}/relationship-list/relationship" % global_customer_id
    data = json.JSONEncoder().encode(data)
    ret = call_aai(resource, "PUT", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Put or update customer relationship exception in AAI")
    return json.JSONDecoder().decode(ret[1]) if ret[1] else ret[1], ret[2]


def delete_customer_relationship(global_customer_id):
    resource = "/business/customers/customer/{global-customer-id}/relationship-list/relationship" % global_customer_id
    ret = call_aai(resource, "DELETE")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Delete customer relationship exception in AAI")
    return json.JSONDecoder().decode(ret[1]) if ret[1] else ret[1], ret[2]


def create_ns_aai(global_customer_id, service_type, service_instance_id, data):
    resource = "/business/customers/customer/%s/service-subscriptions/service-subscription/" \
               "%s/service-instances/service-instance/%s" % \
               (global_customer_id, service_type, service_instance_id)
    data = json.JSONEncoder().encode(data)
    ret = call_aai(resource, "PUT", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Ns instance creation exception in AAI")
    return json.loads(ret[1]) if ret[1] else ret[1], ret[2]


def query_ns_aai(global_customer_id, service_type, service_instance_id):
    resource = "/business/customers/customer/%s/service-subscriptions/service-subscription/" \
               "%s/service-instances/service-instance/%s?depth=all" % \
               (global_customer_id, service_type, service_instance_id)
    ret = call_aai(resource, "GET")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Ns instance query exception in AAI")
    return json.JSONDecoder().decode(ret[1])


def delete_ns_aai(global_customer_id, service_type, service_instance_id, resource_version=""):
    resource = "/business/customers/customer/%s/service-subscriptions/service-subscription/" \
               "%s/service-instances/service-instance/%s" % \
               (global_customer_id, service_type, service_instance_id)
    if resource_version:
        resource = resource + "?resource-version=%s" % resource_version
    ret = call_aai(resource, "DELETE")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Ns instance delete exception in AAI")
    return json.JSONDecoder().decode(ret[1]) if ret[1] else ret[1], ret[2]


def put_ns_relationship(global_customer_id, service_type, service_instance_id, data):
    resource = "/business/customers/customer/%s/service-subscriptions/service-subscription/" \
               "%s/service-instances/service-instance/%s/relationship-list/relationship" % \
               (global_customer_id, service_type, service_instance_id)
    data = json.JSONEncoder().encode(data)
    ret = call_aai(resource, "PUT", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Put or update ns instance relationship exception in AAI")
    return json.JSONDecoder().decode(ret[1]) if ret[1] else ret[1], ret[2]


def delete_ns_relationship(global_customer_id, service_type, service_instance_id):
    resource = "/business/customers/customer/%s/service-subscriptions/service-subscription/" \
               "%s/service-instances/service-instance/%s/relationship-list/relationship" % \
               (global_customer_id, service_type, service_instance_id)
    ret = call_aai(resource, "DELETE")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Delete ns instance relationship exception in AAI")
    return json.JSONDecoder().decode(ret[1]) if ret[1] else ret[1], ret[2]


def create_vnf_aai(vnf_id, data):
    resource = "/network/generic-vnfs/generic-vnf/%s" % vnf_id
    data = json.JSONEncoder().encode(data)
    ret = call_aai(resource, "PUT", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Vnf instance creation exception in AAI")
    return json.JSONDecoder().decode(ret[1]) if ret[1] else ret[1], ret[2]


def query_vnf_aai(vnf_id):
    resource = "/network/generic-vnfs/generic-vnf/%s?depth=all" % vnf_id
    ret = call_aai(resource, "GET")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Vnf instance query exception in AAI")
    return json.JSONDecoder().decode(ret[1])


def delete_vnf_aai(vnf_id, resource_version=""):
    resource = "/network/generic-vnfs/generic-vnf/%s" % vnf_id
    if resource_version:
        resource = resource + "?resource-version=%s" % resource_version
    ret = call_aai(resource, "DELETE")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Vnf instance delete exception in AAI")
    return json.JSONDecoder().decode(ret[1]) if ret[1] else ret[1], ret[2]


def put_vnf_relationship(vnf_id, data):
    resource = "/network/generic-vnfs/generic-vnf/%s/relationship-list/relationship" % vnf_id
    data = json.JSONEncoder().encode(data)
    ret = call_aai(resource, "PUT", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Put or update vnf instance relationship exception in AAI")
    return json.JSONDecoder().decode(ret[1]) if ret[1] else ret[1], ret[2]


def delete_vnf_relationship(vnf_id):
    resource = "/network/generic-vnfs/generic-vnf/%s/relationship-list/relationship" % vnf_id
    ret = call_aai(resource, "DELETE")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Delete vnf instance relationship exception in AAI")
    return json.JSONDecoder().decode(ret[1]) if ret[1] else ret[1], ret[2]


def create_vserver_aai(cloud_owner, cloud_region_id, tenant_id, vserver_id, data):
    resource = "/cloud-infrastructure/cloud-regions/cloud-region/%s/" \
               "%s/tenants/tenant/%s/vservers/vserver/%s" % \
               (cloud_owner, cloud_region_id, tenant_id, vserver_id)
    data = json.JSONEncoder().encode(data)
    ret = call_aai(resource, "PUT", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Vserver creation exception in AAI")
    return json.JSONDecoder().decode(ret[1]) if ret[1] else ret[1], ret[2]


def query_vserver_aai(cloud_owner, cloud_region_id, tenant_id, vserver_id):
    resource = "/cloud-infrastructure/cloud-regions/cloud-region/%s/" \
               "%s/tenants/tenant/%s/vservers/vserver/%s?depth=all" % \
               (cloud_owner, cloud_region_id, tenant_id, vserver_id)
    ret = call_aai(resource, "GET")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Vserver query exception in AAI")
    return json.JSONDecoder().decode(ret[1])


def delete_vserver_aai(cloud_owner, cloud_region_id, tenant_id, vserver_id, resource_version=""):
    resource = "/cloud-infrastructure/cloud-regions/cloud-region/%s/" \
               "%s/tenants/tenant/%s/vservers/vserver/%s" % \
               (cloud_owner, cloud_region_id, tenant_id, vserver_id)
    if resource_version:
        resource = resource + "?resource-version=%s" % resource_version
    ret = call_aai(resource, "DELETE")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Vserver delete exception in AAI")
    if ret[2] == 404:
        logger.error("Vserver has been deleted in aai")
        raise RequestException("Vserver delete exception in AAI")
    return json.JSONDecoder().decode(ret[1]) if ret[1] else ret[1], ret[2]


def put_vserver_relationship(cloud_owner, cloud_region_id, tenant_id, vserver_id, data):
    resource = "/cloud-infrastructure/cloud-regions/cloud-region/%s/" \
               "%s/tenants/tenant/%s/vservers/vserver/%s/relationship-list/relationship" % \
               (cloud_owner, cloud_region_id, tenant_id, vserver_id)
    data = json.JSONEncoder().encode(data)
    ret = call_aai(resource, "PUT", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Put or update vserver relationship exception in AAI")
    return json.JSONDecoder().decode(ret[1]) if ret[1] else ret[1], ret[2]


def delete_vserver_relationship(cloud_owner, cloud_region_id, tenant_id, vserver_id):
    resource = "/cloud-infrastructure/cloud-regions/cloud-region/%s/" \
               "%s/tenants/tenant/%s/vservers/vserver/%s/relationship-list/relationship" % \
               (cloud_owner, cloud_region_id, tenant_id, vserver_id)
    ret = call_aai(resource, "DELETE")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Delete vserver relationship exception in AAI")
    return json.JSONDecoder().decode(ret[1]) if ret[1] else ret[1], ret[2]


def create_l_interface_aai(vnf_id, interface_name):
    resource = "/network/generic-vnfs/generic-vnf/%s/l-interfaces/l-interface/%s" % (vnf_id, interface_name)
    ret = call_aai(resource, "PUT")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("l-interface creation exception in AAI")
    return json.JSONDecoder().decode(ret[1]) if ret[1] else ret[1], ret[2]


def query_l_interface_aai(vnf_id, interface_name):
    resource = "/network/generic-vnfs/generic-vnf/%s/l-interfaces/l-interface/%s" % (vnf_id, interface_name)
    ret = call_aai(resource, "GET")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Get l-interface info exception in AAI")
    return json.JSONDecoder().decode(ret[1]) if ret[1] else ret[1]


def delete_l_interface_aai(vnf_id, interface_name, resource_version=""):
    resource = "/network/generic-vnfs/generic-vnf/%s/l-interfaces/l-interface/%s" % (vnf_id, interface_name)
    if resource_version:
        resource = resource + "?resource-version=%s" % resource_version
    ret = call_aai(resource, "DELETE")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("l_interface delete exception in AAI")
    if ret[2] == 404:
        logger.error("No l_interface %s in AAI" % interface_name)
        raise RequestException("No l_interface %s in AAI" % interface_name)
    return json.JSONDecoder().decode(ret[1]) if ret[1] else ret[1], ret[2]


def create_l3_interface_ipv4_address_list_aai(vnf_id, interface_name, ipv4_addr):
    resource = "/network/generic-vnfs/generic-vnf/%s/l-interfaces/l-interface/%s/" \
               "l3-interface-ipv4-address-list/%s" % (vnf_id, interface_name, ipv4_addr)
    ret = call_aai(resource, "PUT")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Ip address list creation exception in AAI")
    return json.JSONDecoder().decode(ret[1]) if ret[1] else ret[1], ret[2]


def create_network_aai(network_id, data):
    resource = "/network/l3-networks/l3-network/%s" % network_id
    data = json.JSONEncoder().encode(data)
    ret = call_aai(resource, "PUT", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Network creation exception in AAI")
    return json.JSONDecoder().decode(ret[1]) if ret[1] else ret[1], ret[2]


def query_network_aai(network_id):
    resource = "/network/l3-networks/l3-network/%s" % network_id
    ret = call_aai(resource, "GET")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Network query exception in AAI")
    return json.JSONDecoder().decode(ret[1])


def delete_network_aai(network_id, resource_version=""):
    resource = "/network/l3-networks/l3-network/%s" % network_id
    if resource_version:
        resource = resource + "?resource-version=%s" % resource_version
    ret = call_aai(resource, "DELETE")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Network delete exception in AAI")
    if ret[2] == 404:
        logger.error("Network has been deleted in aai")
        raise RequestException("Network delete exception in AAI")
    return json.JSONDecoder().decode(ret[1]) if ret[1] else ret[1], ret[2]


def put_network_relationship(network_id, data):
    resource = "/network/l3-networks/l3-network/%s/relationship-list/relationship" % network_id
    data = json.JSONEncoder().encode(data)
    ret = call_aai(resource, "PUT", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Put or update network relationship exception in AAI")
    return json.JSONDecoder().decode(ret[1]) if ret[1] else ret[1], ret[2]


def delete_network_relationship(network_id):
    resource = "/network/l3-networks/l3-network/%s/relationship-list/relationship" % network_id
    ret = call_aai(resource, "DELETE")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Delete network relationship exception in AAI")
    return json.JSONDecoder().decode(ret[1]) if ret[1] else ret[1], ret[2]


def create_subnet_aai(network_id, subnet_id, data):
    resource = "/network/l3-networks/l3-network/%s/subnets/subnet/%s" % (network_id, subnet_id)
    data = json.JSONEncoder().encode(data)
    ret = call_aai(resource, "PUT", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Subnetwork creation exception in AAI")
    return json.JSONDecoder().decode(ret[1]) if ret[1] else ret[1], ret[2]


def query_subnet_aai(network_id, subnet_id):
    resource = "/network/l3-networks/l3-network/%s/subnets/subnet/%s" % (network_id, subnet_id)
    ret = call_aai(resource, "GET")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Subnetwork query exception in AAI")
    return json.JSONDecoder().decode(ret[1])


def delete_subnet_aai(network_id, subnet_id, resource_version=""):
    resource = "/network/l3-networks/l3-network/%s/subnets/subnet/%s" % (network_id, subnet_id)
    if resource_version:
        resource = resource + "?resource-version=%s" % resource_version
    ret = call_aai(resource, "DELETE")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Subnetwork delete exception in AAI")
    return json.JSONDecoder().decode(ret[1]) if ret[1] else ret[1], ret[2]


def put_subnet_relationship(network_id, subnet_id, data):
    resource = "/network/l3-networks/l3-network/%s/subnets/subnet/%s/relationship-list/relationship"\
               % (network_id, subnet_id)
    data = json.JSONEncoder().encode(data)
    ret = call_aai(resource, "PUT", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Put or update subnetwork relationship exception in AAI")
    return json.JSONDecoder().decode(ret[1]) if ret[1] else ret[1], ret[2]


def delete_subnet_relationship(network_id, subnet_id):
    resource = "/network/l3-networks/l3-network/%s/subnets/subnet/%s/relationship-list/relationship"\
               % (network_id, subnet_id)
    ret = call_aai(resource, "DELETE")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Delete subnetwork relationship exception in AAI")
    return json.JSONDecoder().decode(ret[1]) if ret[1] else ret[1], ret[2]
