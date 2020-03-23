#!/usr/bin/python

# Prerequisites for machine to run this
# Put in required parameters in vcpe_vgw_config.json
# Install python-pip (apt install python-pip)
# Install ONAP CLI
# Must have connectivity to the ONAP, a k8s vm already running is recommended
# Create Preload File, the script will modify the parameters required from serivce model, service instance
# and vnf instance
# Put in CSAR file

import json
import os
import uuid
import requests
import unittest
import time
import logging

logger = logging.getLogger(__name__)


class VcpeToscaTest(unittest.TestCase):

    def setUp(self):
        file_path = os.path.dirname(os.path.abspath(__file__))
        requests.packages.urllib3.disable_warnings()
        with open(file_path + "//vcpe_config_ip.json", encoding='utf-8') as self.config_file:
            self.config_params = self.get_parameters()
        self.aai_header = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            'X-TransactionId': "9999",
            'Real-Time': "true",
            'X-FromAppId': "jimmy-postman",
            "Authorization": "Basic QUFJOkFBSQ=="
        }
        self.base_url = self.config_params["msb_url"]
        logger.debug("Set cli command environment--beginning")
        os.environ["OPEN_CLI_PRODUCT_IN_USE"] = self.config_params["open_cli_product"]
        os.environ["OPEN_CLI_HOME"] = self.config_params["open_cli_home"]
        logger.debug("Set cli command environment--successful")
        logger.debug("Create cloud complex--beginning")
        self.create_complex()
        logger.debug("Create cloud complex--successful")
        logger.debug("Register all clouds--beginning")
        self.register_all_clouds()
        logger.debug("Register all clouds--successful")
        time.sleep(30)
        logger.debug("create vCPE service")
        self.create_service_type()
        logger.debug("create customer")
        self.create_customer()
        logger.debug("Get tenant id")
        self.get_tenant_id()
        logger.debug("add customer and subscription")
        self.add_customer_subscription()
        logger.debug("Register vnfm")
        self.register_vnfm()

    def tearDown(self):
        if self.ns_instance_id:
            self.terminateNs()
            self.deleteNs()

        if self.esr_vnfm_id and self.esr_vnfm_version:
            self.unregister_vnfm()

        if self.ns_package_id:
            self.delete_ns_package()

        if self.vnf_package_list:
            self.delete_vnf_package()

        if self.subscription_version:
            logger.debug("Remove service subscription")
            self.remove_customer_subscription()

        if self.customer_version:
            logger.debug("Remove customer %s" % self.config_params["customer_name"])
            self.delete_customer()

        if self.service_type_version:
            logger.debug("Remove service type %s" % self.config_params["service_name"])
            self.delete_service_type()

        if self.cloud_version:
            logger.debug("Remove cloud %s" % self.config_params["cloud-owner"])
            self.delete_cloud_helper()

        time.sleep(30)

        if self.complex_version:
            logger.debug("Remove complex %s" % self.config_params["complex_name"])
            self.delete_complex()

    def get_parameters(self):
        parameters = json.load(self.config_file)
        return parameters

    def create_complex(self):
        self.complex_version = None
        complex_create_string = "oclip complex-create -j {} -r {} -x {} -y {} -lt {} -l {} -i {} -lo {} \
                             -S {} -la {} -g {} -w {} -z {} -k {} -o {} -q {} -m {} -u {} -p {}".format(
            self.config_params["street2"],
            self.config_params["physical_location"], self.config_params["complex_name"],
            self.config_params["data_center_code"], self.config_params["latitude"], self.config_params["region"],
            self.config_params["street1"], self.config_params["longitude"], self.config_params["state"],
            self.config_params["lata"], self.config_params["city"], self.config_params["postal-code"],
            self.config_params["complex_name"], self.config_params["country"], self.config_params["elevation"],
            self.config_params["identity_url"], self.config_params["aai_url"], self.config_params["aai_username"],
            self.config_params["aai_password"])
        os.system(complex_create_string)

        complex_url = self.base_url + "/aai/v11/cloud-infrastructure/complexes"
        
        complex_list_response = requests.get(url=complex_url, headers=self.aai_header, verify=False)
        if complex_list_response.status_code == 200:
            for complex in (complex_list_response.json())["complex"]:
                if complex['physical-location-id'] == self.config_params["complex_name"]:
                    self.complex_version = complex['resource-version']
                    logger.debug("Complex %s resource-version is %s."
                                 % (self.config_params["complex_name"], self.complex_version))

    def delete_complex(self):
        complex_delete_string = 'oclip complex-delete -x {} -y {} -m {} -u {} -p {}'.format(
            self.config_params["complex_name"], self.complex_version, self.config_params["aai_url"],
            self.config_params["aai_username"], self.config_params["aai_password"])
        os.system(complex_delete_string)
        logger.debug("Delete complex--successful")
        self.complex_version = None

    def register_cloud_helper(self, cloud_region, values):
        logger.debug("Create Cloud--beginning")
        self.cloud_version = None
        cloud_create_string = 'oclip cloud-create -e {} -b {} ' \
                              '-x {} -y {} -j {} -w {} -l {} -url {} -n {} -q {} -r {} -Q {} -i {} -g {} \
                              -z {} -k {} -c {} -m {} -u {} -p {}' \
            .format(values.get("esr-system-info-id"), values.get("user-name"),
                    self.config_params["cloud-owner"],
                    cloud_region, values.get("password"),
                    values.get("cloud-region-version"), values.get("default-tenant"),
                    values.get("service-url"), self.config_params["complex_name"],
                    values.get("cloud-type"), self.config_params["owner-defined-type"],
                    values.get("system-type"), values.get("identity-url"),
                    self.config_params["cloud-zone"], values.get("ssl-insecure"),
                    values.get("system-status"), values.get("cloud-domain"),
                    self.config_params["aai_url"],
                    self.config_params["aai_username"],
                    self.config_params["aai_password"])
        os.system(cloud_create_string)
        logger.debug("Create Cloud--successful")
        logger.debug("Associate Cloud with complex--beginning")
        complex_associate_string = "oclip complex-associate -x {} -y {} -z {} -m {} -u {} -p {}".format(
            self.config_params["complex_name"],
            cloud_region, self.config_params["cloud-owner"], self.config_params["aai_url"],
            self.config_params["aai_username"],
            self.config_params["aai_password"])
        os.system(complex_associate_string)
        logger.debug("Associate Cloud with complex--successful")
        logger.debug("Register Cloud with Multicloud--beginning")
        multicloud_register_string = "oclip multicloud-register-cloud -y {} -x {} -m {}".format(
            self.config_params["cloud-owner"], cloud_region, self.config_params["multicloud_url"])
        os.system(multicloud_register_string)
        logger.debug("Register Cloud with Multicloud--successful")
        cloud_url = self.base_url + "/aai/v11/cloud-infrastructure/cloud-regions"
        cloud_list_response = requests.get(url=cloud_url, headers=self.aai_header, verify=False)
        if cloud_list_response.status_code == 200:
            for cloud in (cloud_list_response.json())["cloud-region"]:
                if cloud['cloud-owner'] == self.config_params["cloud-owner"]:
                    self.cloud_version = cloud['resource-version']
                    logger.debug("Cloud %s resource-version is %s."
                                 % (self.config_params["cloud-owner"], self.cloud_version))

    def register_all_clouds(self):
        cloud_dictionary = self.config_params["cloud_region_data"]
        for cloud_region, cloud_region_values in cloud_dictionary.items():
            self.register_cloud_helper(cloud_region, cloud_region_values)

    def delete_cloud_helper(self):
        logger.debug("Multicloud-cloud-delete--beginning")
        cloud_region = list(self.config_params["cloud_region_data"].keys())[0]
        header = {'content-type': 'application/json', 'accept': 'application/json'}
        multicloud_url = self.base_url + "/api/multicloud-titaniumcloud/v1/{}/{}" \
            .format(self.config_params["cloud-owner"], cloud_region)
        requests.delete(url=multicloud_url, headers=header, verify=False)
        logger.debug("Multicloud-cloud-delete----successful")
        self.customer_version = None

    def create_service_type(self):
        self.service_type_version = None
        create_string = "oclip service-type-create -x {} -y {} -m {} -u {} -p {}".format(
            self.config_params["service_name"], self.config_params["service_name"], self.config_params["aai_url"],
            self.config_params["aai_username"], self.config_params["aai_password"])
        os.system(create_string)
        service_tpe_list_url = self.base_url + "/aai/v11/service-design-and-creation/services"
        service_type_list_response = requests.get(url=service_tpe_list_url, headers=self.aai_header, verify=False)
        if service_type_list_response.status_code == 200:
            for service in (service_type_list_response.json())["service"]:
                if service["service-id"] == self.config_params["service_name"]:
                    self.service_type_version = service['resource-version']
                    logger.debug("Service type %s resource-version is %s."
                                 % (self.config_params["service_name"], self.service_type_version))

    def delete_service_type(self):
        logger.debug("delete service type--beginning")
        service_delete_string = 'oclip service-type-delete -x {} -y {} -m {} -u {} -p {}'.format(
            self.config_params["service_name"], self.service_type_version, self.config_params["aai_url"],
            self.config_params["aai_username"], self.config_params["aai_password"])
        os.system(service_delete_string)
        logger.debug("delete service type--successful")
        self.service_type_version = None

    def create_customer(self):
        self.customer_version = None
        create_string = "oclip customer-create -x {} -y {} -m {} -u {} -p {}".format(
            self.config_params["customer_name"],
            self.config_params["subscriber_name"],
            self.config_params["aai_url"],
            self.config_params["aai_username"],
            self.config_params["aai_password"])
        os.system(create_string)
        customer_list_url = self.base_url + "/aai/v11/business/customers"
        customer_list_response = requests.get(url=customer_list_url, headers=self.aai_header, verify=False)
        if customer_list_response.status_code == 200:
            for cutsomer in (customer_list_response.json())["customer"]:
                if cutsomer['global-customer-id'] == self.config_params["customer_name"]:
                    self.customer_version = cutsomer['resource-version']
                    logger.debug("Customer %s resource-version is %s."
                                 % (self.config_params["customer_name"], self.customer_version))

    def delete_customer(self):
        logger.debug("delete customer--beginning")
        customer_delete_string = 'oclip customer-delete -x {} -y {} -m {} -u {} -p {}'.format(
            self.config_params["customer_name"], self.customer_version, self.config_params["aai_url"],
            self.config_params["aai_username"], self.config_params["aai_password"])
        os.system(customer_delete_string)
        logger.debug("delete customer--successful")
        self.customer_version = None

    def get_tenant_id(self):
        logger.debug("Get tenant id--beginning")
        self.tenant_id = None
        cloud_dictionary = self.config_params["cloud_region_data"]
        cloud_region = list(self.config_params["cloud_region_data"].keys())[0]
        tenant_list_url = self.base_url + "/aai/v11/cloud-infrastructure/cloud-regions/cloud-region/{}/{}/tenants" \
            .format(self.config_params["cloud-owner"], cloud_region)

        for cloud_region, cloud_region_values in cloud_dictionary.items():
            tenant_name = cloud_region_values.get("default-tenant")
        tenant_list_response = requests.get(url=tenant_list_url, headers=self.aai_header, verify=False)
        if tenant_list_response.status_code == 200:
            for tenant in (tenant_list_response.json())["tenant"]:
                if tenant['tenant-name'] == tenant_name:
                    self.tenant_id = tenant['tenant-id']
                    logger.debug("Tenant id is %s ." % self.tenant_id)

    def add_customer_subscription(self):
        self.subscription_version = None
        subscription_check = 0
        for cloud_region, cloud_region_values in (self.config_params["cloud_region_data"]).items():
            if subscription_check == 0:
                subscription_string = "oclip subscription-create -x {} -c {} -z {} -e {} " \
                                      "-y {} -r {} -m {} -u {} -p {}" \
                    .format(self.config_params["customer_name"],
                            self.tenant_id,
                            self.config_params["cloud-owner"],
                            self.config_params["service_name"],
                            cloud_region_values.get("default-tenant"),
                            cloud_region, self.config_params["aai_url"],
                            self.config_params["aai_username"],
                            self.config_params["aai_password"])
            else:
                subscription_string = "oclip subscription-cloud-add -x {} -c {} " \
                                      "-z {} -e {} -y {} -r {} -m {} -u {} -p {}" \
                    .format(self.config_params["customer_name"], self.tenant_id,
                            self.config_params["cloud-owner"], self.config_params["service_name"],
                            cloud_region_values.get("default-tenant"), cloud_region,
                            self.config_params["aai_url"],
                            self.config_params["aai_username"],
                            self.config_params["aai_password"])
            os.system(subscription_string)
            subscription_check += 1

        subscription_url = self.base_url + "/aai/v11/business/customers/customer/{}" \
                                           "/service-subscriptions/service-subscription/{}" \
            .format(self.config_params["customer_name"], self.config_params["service_name"])
        resp = requests.get(url=subscription_url, headers=self.aai_header, verify=False)
        if resp.status_code == 200:
            self.subscription_version = resp.json()['resource-version']
            logger.debug("Subscription resource-version is %s." % self.subscription_version)

    def remove_customer_subscription(self):
        logger.debug("Remove subscription--beginning")
        subscription_delete_string = 'oclip subscription-delete -x {} -y {} -g {} -m {} -u {} -p {}'.format(
            self.config_params["customer_name"], self.config_params["service_name"], self.subscription_version,
            self.config_params["aai_url"],
            self.config_params["aai_username"], self.config_params["aai_password"])
        os.system(subscription_delete_string)
        logger.debug("Delete subscription--successful")

    def register_vnfm_helper(self, vnfm_key, values):
        logger.debug("Create vnfm--beginning")
        self.esr_vnfm_version = None
        self.esr_vnfm_id = str(uuid.uuid4())
        vnfm_create_string = 'oclip vnfm-create -b {} -c {} -e {} -v {} -g {} -x {} ' \
                             '-y {} -i {} -j {} -q {} -m {} -u {} -p {}' \
            .format(vnfm_key, values.get("type"), values.get("vendor"),
                    values.get("version"), values.get("url"), values.get("vim-id"),
                    self.esr_vnfm_id, values.get("user-name"), values.get("user-password"),
                    values.get("vnfm-version"), self.config_params["aai_url"],
                    self.config_params["aai_username"], self.config_params["aai_password"])

        os.system(vnfm_create_string)
        logger.debug("Create vnfm--successful")
        vnfm_url = self.base_url + "/aai/v11/external-system/esr-vnfm-list"
        resp = requests.get(url=vnfm_url, headers=self.aai_header, verify=False)
        if resp.status_code == 200:
            for vnfm in (resp.json())["esr-vnfm"]:
                if vnfm['vnfm-id'] == self.esr_vnfm_id:
                    self.esr_vnfm_version = vnfm['resource-version']
                    logger.debug("Vnfm %s resource-version is %s."
                                 % (self.esr_vnfm_id, self.esr_vnfm_version))

    def register_vnfm(self):
        vnfm_params = self.config_params["vnfm_params"]
        for vnfm_key, vnfm_values in vnfm_params.items():
            self.register_vnfm_helper(vnfm_key, vnfm_values)

    def unregister_vnfm(self):
        logger.debug("Delete vnfm %s" % self.esr_vnfm_id)
        logger.debug("Delete vnfm--beginning")
        vnfm_delete_string = 'oclip vnfm-delete -x {} -y {} -m {} -u {} -p {}'.format(
            self.esr_vnfm_id, self.esr_vnfm_version, self.config_params["aai_url"],
            self.config_params["aai_username"], self.config_params["aai_password"])
        os.system(vnfm_delete_string)
        self.esr_vnfm_version = self.esr_vnfm_id = None
        logger.debug("Delete vnfm--successful")

    def create_ns(self):
        ns = self.config_params["ns"]
        data = {
            "context": {
                "globalCustomerId": self.config_params["customer_name"],
                "serviceType": self.config_params["service_name"]
            },
            "csarId": self.ns_package_id,
            "nsName": ns.get("name"),
            "description": "description"
        }
        ns_header = {'content-type': 'application/json', 'accept': 'application/json'}
        ns_url = self.base_url + "/api/nslcm/v1/ns"
        ns_resp = requests.post(ns_url, data=json.dumps(data), headers=ns_header, verify=False)
        if 201 == ns_resp.status_code:
            ns_instance_id = ns_resp.json().get("nsInstanceId")
            logger.debug("create ns successfully, the ns instance id is %s" % ns_instance_id)
            return ns_instance_id
        else:
            return None

    def instantiate_ns(self):
        logger.debug("Instantiate ns beginning")
        locationConstraints = [
            {
                "vnfProfileId": x,
                "locationConstraints": {
                    "vimId": self.config_params["location"]
                }
            } for x in self.vnfdId_list]
        data = {
            "additionalParamForNs": {
                "sdnControllerId": self.config_params["sdc-controller-id"]
            },
            "locationConstraints": locationConstraints
        }

        header = {'content-type': 'application/json', 'accept': 'application/json'}
        instance_url = self.base_url + "/api/nslcm/v1/ns/" + self.ns_instance_id + "/instantiate"

        instance_resp = requests.post(instance_url, data=json.dumps(data), headers=header, verify=False)
        if 200 == instance_resp.status_code:
            ns_instance_jod_id = instance_resp.json().get("jobId")
            logger.debug("Instantiate ns successfully, the job id is %s" % ns_instance_jod_id)
            return ns_instance_jod_id
        else:
            raise Exception("Instantiate ns failed.")

    def create_ns_package(self):
        logger.debug("Create ns package is beginning")
        ns = self.config_params["ns"]
        ns_url = self.base_url + "/api/nsd/v1/ns_descriptors"
        ns_headers = {'content-type': 'application/json', 'accept': 'application/json'}
        ns_data = {'userDefinedData': {ns.get("key"): ns.get("value")}}
        ns_package_reps = requests.post(ns_url, data=json.dumps(ns_data), headers=ns_headers, verify=False)
        if 201 == ns_package_reps.status_code:
            logger.debug("Create ns package successful, the ns package id is %s"
                         % (ns_package_reps.json()["id"]))
            return ns_package_reps.json()["id"]
        else:
            return None

    def delete_ns_package(self):
        logger.debug("Delete ns package %s is beginning" % self.ns_package_id)
        vnf_url = self.base_url + "/api/nsd/v1/ns_descriptors/%s" % self.ns_package_id
        resp = requests.delete(url=vnf_url, verify=False)
        if 204 == resp.status_code:
            logger.debug("Delete ns package %s successfully." % self.ns_package_id)
            self.ns_package_id = None
        else:
            logger.debug("Delete ns package %s failed." % self.ns_package_id)

    def create_upload_vnf_package(self):
        logger.debug("Create vnf package is beginning")
        package_list = []
        vnfs = self.config_params["vnfs"]
        vnf_url = self.base_url + "/api/vnfpkgm/v1/vnf_packages"
        header = {'content-type': 'application/json', 'accept': 'application/json'}
        for vnf_key, vnf_values in vnfs.items():
            vnf_data = {'userDefinedData': {vnf_values.get("key"): vnf_values.get("value")}}
            vnf_package_reps = requests.post(vnf_url, data=json.dumps(vnf_data), headers=header, verify=False)
            if 201 == vnf_package_reps.status_code:
                logger.debug("Create vnf package successful, the vnf package id is %s"
                             % (vnf_package_reps.json()["id"]))
                package_id = vnf_package_reps.json()["id"]
                package_list.append(package_id)
                vnf_upload_url = '{}/api/vnfpkgm/v1/vnf_packages/{}/package_content' \
                    .format(self.config_params["vfc-url"], package_id)
                logger.debug(vnf_upload_url)
                file_path = os.path.dirname(os.path.abspath(__file__))
                csar_file = file_path + "/" + vnf_values.get("path")
                logger.debug(csar_file)
                with open(csar_file, 'rb', encoding='utf-8') as vnf_file:
                    logger.debug(vnf_file)
                for i in range(10):
                    resp = requests.put(vnf_upload_url, files={'file': vnf_file}, verify=False)
                    logger.debug(resp.status_code)
                    if 202 == resp.status_code:
                        break
                    else:
                        time.sleep(1)
        return package_list

    def delete_vnf_package(self):
        logger.debug("Delete vnf package is beginning")
        for vnf_package_id in self.vnf_package_list:
            vnf_url = self.base_url + "/api/vnfpkgm/v1/vnf_packages/%s" % vnf_package_id
            
            resp = requests.delete(url=vnf_url, verify=False)
            if 204 == resp.status_code:
                logger.debug("Delete vnf package %s successfully." % vnf_package_id)
            else:
                logger.debug("Delete vnf package %s failed." % vnf_package_id)

    def upload_ns_package(self):
        ns = self.config_params["ns"]
        ns_upload_url = '{}/api/nsd/v1/ns_descriptors/{}/nsd_content'.format(self.config_params["vfc-url"],
                                                                             self.ns_package_id)
        logger.debug(ns_upload_url)
        file_path = os.path.dirname(os.path.abspath(__file__))
        ns_vgw = file_path + "/" + ns["path"]
        with open(ns_vgw, 'rb', encoding='utf-8') as ns_file:
            logger.debug(ns_file)
        for i in range(10):
            
            resp = requests.put(ns_upload_url, files={'file': ns_file}, verify=False)
            logger.debug(resp.status_code)
            if 204 == resp.status_code:
                break
            else:
                time.sleep(1)
        return resp

    def get_vnf_package(self):
        vnfdId_list = []
        for vnf_package_id in self.vnf_package_list:
            vnf_package_url = self.base_url + '/api/vnfpkgm/v1/vnf_packages/%s' % vnf_package_id
            
            vnf_resp = requests.get(vnf_package_url, verify=False)
            if 200 == vnf_resp.status_code:
                vnfdId = vnf_resp.json().get("vnfdId")
                logger.debug("vnfdId is %s" % vnfdId)
                vnfdId_list.append(vnfdId)
        return vnfdId_list

    def getVnf(self, vnfs):
        vnf_list = []
        for vnf in vnfs:
            if 'relationship-list' in vnf:
                for relation in vnf["relationship-list"]["relationship"]:
                    if "service-instance" == relation["related-to"] and self.ns_instance_id in relation["related-link"]:
                        vnf_list.append(vnf)
        return vnf_list

    @staticmethod
    def findVserver(vnf_list):
        vserver_list = []
        for vnf in vnf_list:
            if 'relationship-list' in vnf:
                for relation in vnf["relationship-list"]["relationship"]:
                    if "vserver" == relation["related-to"]:
                        for relationData in relation["relationship-data"]:
                            if "vserver.vserver-id" == relationData["relationship-key"]:
                                vserver_list.append(relationData["relationship-value"])
        return vserver_list

    def waitProcessFinished(self, job_id, action):
        logger.debug("Wait for the %s ns finished." % action)
        job_url = self.base_url + "/api/nslcm/v1/jobs/%s" % job_id
        progress = 0
        for i in range(1500):
            
            job_resp = requests.get(url=job_url, verify=False)
            if 200 == job_resp.status_code and "responseDescriptor" in job_resp.json():
                progress_rep = (job_resp.json())["responseDescriptor"]["progress"]
                if 100 != progress_rep and 255 == progress_rep:
                    logger.debug("Ns %s %s failed." % (self.ns_instance_id, action))
                    break
                elif progress_rep != progress:
                    progress = progress_rep
                    logger.debug("Ns %s %s process is %s." % (self.ns_instance_id, action, progress))
                    time.sleep(0.2)
                else:
                    logger.debug("Ns %s %s process is %s." % (self.ns_instance_id, action, progress_rep))
                    logger.debug("Ns %s %s successfully." % (self.ns_instance_id, action))
                    break

    def terminateNs(self):
        logger.debug("Terminate ns--beginning")
        ns_url = self.base_url + "/api/nslcm/v1/ns/%s" % self.ns_instance_id
        data = {
            "gracefulTerminationTimeout": 1600,
            "terminationType": "FORCEFUL"
        }
        
        res = requests.post(url=ns_url + "/terminate", data=data, verify=False)
        self.assertEqual(202, res.status_code)
        terminate_ns_job_id = res.json()["jobId"]
        logger.debug("Terminate job is %s" % terminate_ns_job_id)
        self.waitProcessFinished(terminate_ns_job_id, "terminate")

    def deleteNs(self):
        logger.debug("Delete ns %s --beginning" % self.ns_instance_id)
        ns_url = self.base_url + "/api/nslcm/v1/ns/%s" % self.ns_instance_id
        
        res = requests.delete(ns_url, verify=False)
        if 204 == res.status_code:
            logger.debug("Ns %s delete successfully." % self.ns_instance_id)
            self.ns_instance_id = None

    def testNs(self):

        logger.debug("Use csar file is uploaded by local")
        self.vnf_package_list = self.create_upload_vnf_package()
        self.assertIsNotNone(self.vnf_package_list)

        self.ns_package_id = self.create_ns_package()
        self.assertIsNotNone(self.ns_package_id)

        logger.debug("Get vnfdId list.")
        self.vnfdId_list = self.get_vnf_package()

        logger.debug("Upload ns package from csar beginning")
        self.upload_ns_package()
        logger.debug("Upload ns package from csar successfully")

        # 7. VFC part
        logger.debug("Create ns beginning")

        self.ns_instance_id = self.create_ns()
        self.assertIsNotNone(self.ns_instance_id)
        try:
            self.ns_instance_jod_id = self.instantiate_ns()
            logger.debug("NS %s instantiate job is %s" % (self.ns_instance_id, self.ns_instance_jod_id))
        except Exception as e:
            logger.error(e.args[0])

        self.assertIsNotNone(self.ns_instance_jod_id)

        self.waitProcessFinished(self.ns_instance_jod_id, "instantiate")

        vnf_aai_url = self.base_url + "/aai/v11/network/generic-vnfs"
        
        vnf_resp = requests.get(url=vnf_aai_url, headers=self.aai_header, verify=False)
        self.assertEqual(200, vnf_resp.status_code)

        vnfs = vnf_resp.json()["generic-vnf"]
        vnf_list = self.getVnf(vnfs)
        self.assertEqual(5, len(vnf_list))
        logger.debug("There are %s vnfs are created." % len(vnf_list))
        for vnf in vnf_list:
            logger.debug("The vnf %s are created successfully." % vnf.get("vnf-id"))

        vserver_list = self.findVserver(vnf_list)
        logger.debug("The vserver %s is created successfully." % len(vserver_list))
        self.assertEqual(8, len(vserver_list))

        cloud_region_id = list(self.config_params["cloud_region_data"].keys())[0]

        for vserver_id in vserver_list:
            vserver_aai_url = self.base_url + "/aai/v11/cloud-infrastructure/cloud-regions/cloud-region" \
                                              "/{}/{}/tenants/tenant/{}/vservers/vserver/{}?depth=all" \
                .format(self.config_params["cloud-owner"], cloud_region_id, self.tenant_id, vserver_id)
            
            vserver_resp = requests.get(url=vserver_aai_url, headers=self.aai_header, verify=False)
            self.assertEqual(200, vserver_resp.status_code)
            logger.debug("The vserver %s is created successfully." % vserver_id)
