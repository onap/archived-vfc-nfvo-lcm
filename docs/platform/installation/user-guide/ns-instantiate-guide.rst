.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

NS LCM Guide Using VF-C
-----------------------

VF-C supports vCPE use case in R3, all VNFs are deployed through VF-C GVNFM .
This page describes how to use VF-C to instantiate NS

Before you try, please prepare two csar file: 

* VNF csar
* NS csar

If you don't have any csar, you can download the simple csar from https://wiki.onap.org/display/DW/VF-C+User+Guide 


Environment
+++++++++++
VF-C components can run as docker, docker service should be installed before install VF-C components.

The following scripts show the docker service install commands in centos7.

::

  yum install docker
  systemctl enable docker.service
  systemctl start docker.service

Steps
+++++



If you want to  try VF-C,  the small project set should include: VF-C , Multicloud, MSB, A&AI.

VF-C components need to register to MSB when starting, so MSB components should be installed first,you can refer the following link to install MSB.

http://onap.readthedocs.io/en/latest/submodules/msb/apigateway.git/docs/platform/installation.html

Note: In the following steps, we use ${MSB_IP} as the IP of msb_apigateway component.

1. Install vfc-nfvo-db component

::

  docker run -d -p 3306:3306 -p 6379:6379 --name vfc-db -v /var/lib/mysql nexus3.onap.org:10001/onap/vfc/db
  we use  ${VFC_DB_IP} as the IP of vfc-db component.

2. Install vfc-nfvo-lcm component.

::

  docker run -d -p 8403:8403 --name vfc-nslcm -e MSB_ADDR=${MSB_IP}:80 -e MYSQL_ADDR=${VFC_DB_IP}:3306
  nexus3.onap.org:10001/onap/vfc/nslcm

3. Install modeling-etsicatalog component.

::

  docker run -d -p 8806:8806 --name vfc-etsicatalog -e MSB_ADDR=${MSB_IP}:80 -e MYSQL_ADDR=${VFC_DB_IP}:3306 nexus3.onap.org:10001/onap/vfc/catalog

4. Install vfc-nfvo-gvnfmdriver component.

::

  docker run -d -p 8484:8484 --name vfc-gvnfmdriver -e MSB_ADDR=${MSB_IP}:80 nexus3.onap.org:10001/onap/vfc/gvnfmdriver

5. Install vfc-gvnfm-vnflcm component.

::

  docker run -d -p 8801:8801 --name vfc-vnflcm -e MSB_ADDR=${MSB_IP}:80 -e MYSQL_ADDR=${VFC_DB_IP}:3306 nexus3.onap.org:10001/onap/vfc/vnflcm


ESR Registration
++++++++++++++++


Before we instantiate a service, we need to register vim and vnfm which is used to deploy vnfs.

  1.VIM Registration

  |image1|

  .. |image1| image:: vim.png
   :width: 1000px
   :height: 600px


  2. GVNFM Registration

  For VF-C, because we use GVNFM to deploy vnfs , so you can register GVNFM in esr gui as follows:

  |image2|

  .. |image2| image:: gvnfm.png
   :width: 1000px
   :height: 600px


Note: 
  a. type should be gvnfmdriver which is the same with gvnfmdriver microservice.
  b. url is the msb-iag NodeIp:port.
  c. vim corresponds to cloudowner_cloudregionid which registered in step1.

Package Onboarding
++++++++++++++++++


VF-C R3 support VNF/PNF/NS csar package upload from local csar file. VNF/PNF csar package should be uploaded first, then NS csar package can be uploaded.
Before onboarding a package,  should create one record first. 


1. Create VNF package record  in catalog DB

::

  curl -X POST \

  http://172.30.3.104:30280/api/vnfpkgm/v1/vnf_packages \

  -H 'Postman-Token: f9c45dea-b7bb-4acd-89e1-b9b1c3d70d8a' \
  -H 'accept: application/json' \
  -H 'cache-control: no-cache' \
  -H 'content-type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW' \
  -F 'userDefinedData= "key2": "value2"'

Note:  
  a. 172.30.3.104:30280 is the node IP and exposed port where the msb-iag pod is located. 
  b. userDefinedData is the key value pair which defined for the vnf package we created

2. Upload VNF package to VF-C catalog

::

  curl -X PUT \
  http://172.30.3.104:30280/api/vnfpkgm/v1/vnf_packages/38037a12-a0d4-4aa4-ac50-cd6b05ce0b24/package_content \
  -H 'Postman-Token: 88ada218-86fd-4cd7-a06e-cc462f5df651' \
  -H 'cache-control: no-cache'
  -H 'accept: application/json' \
  -H 'content-type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW' \
  -F 'file=@C:\ONAP\Integration\R3\vCPE\vnf-vsn.csar'

Note:
  a. 38037a12-a0d4-4aa4-ac50-cd6b05ce0b24 is the vnf_pkg_id which we get from the first step.
  b. -F is used to specify the local vnf package file

3. Create NS package record in catalog DB

::

  curl -X POST \

  http://172.30.3.104:30280/api/nsd/v1/ns_descriptors \
  -H 'Postman-Token: 71b11910-1708-471c-84bb-5b0dd8d214a2' \
  -H 'accept: application/json' \
  -H 'cache-control: no-cache' \
  -H 'content-type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW' \
  -F 'userDefinedData= "key1": "value1"'

Note:
  a. userDefinedData is the key value pair which defined for the ns package we created

4. Upload NS package to VF-C catalog

::

  curl -X PUT \
  http://172.30.3.104:30280/api/nsd/v1/ns_descriptors/79ca81ec-10e0-44e4-bc85-ba968f345711/nsd_content \
  -H 'Postman-Token: f16e4a54-a514-4878-b307-9b80c630166e' \
  -H 'cache-control: no-cache'
  -H 'accept: application/json' \
  -H 'content-type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW' \
  -F 'file=@C:\ONAP\Integration\R3\vCPE\ns.csar'

Note:
  a.  -F is used to specify the local ns package file


NS Life Cycle Management
++++++++++++++++++++++++


Currently VF-C GVNFM support NS create/Instantiate/terminate/delete/heal.

VF-C R3 healing only suport restart a vm of an VNF. 

1. NS Create 

::

  curl -X POST \
  http://172.30.3.104:30280/api/nslcm/v1/ns \
  -H 'Postman-Token: 27e2c576-2d9b-4753-a6b0-6262a4a7ec86' \
  -H 'accept: application/json' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  -d '{
       "context": {
                "globalCustomerId": "global-customer-id-test1",
                "serviceType": "service-type-test1"
        },
        "csarId": "79ca81ec-10e0-44e4-bc85-ba968f345711",
        "nsName": "ns_vsn",
        "description": "description"
        }'

Note:
  a. globalCustomerId  and serviceType is defined in A&AI.
  b. csar Id is the NS package id  which is consistent with the catalog ns package id.
  c. nsName is the NS name 

2. NS Instantiate

::

   curl -X POST \
  http://172.30.3.104:30280/api/nslcm/v1/ns/f0b4c09f-c653-438a-b091-5218b0f806ec/instantiate \
  -H 'Postman-Token: 2a9542b2-3364-4a40-8513-45e10b8ca2ce' \
  -H 'accept: application/json' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
    -d '{
         "additionalParamForNs": {
                "sdnControllerId": "2"
         },
         "locationConstraints": [{
                "vnfProfileId": "45711f40-3f43-415b-bb45-46e5c6940735",
                "locationConstraints": {
                      "vimId": "CPE-DC_RegionOne"
                }
                }]
         }'

Note:
  a.  f0b4c09f-c653-438a-b091-5218b0f806ec is the ns instance id which create in step 1 : NS create.
  b.  locationConstraints  is an array which contains all the vnfs included under NS locationConstraints is used to define the VIM( cloudOwner_cloudRegionId)  that the VNF will be deployed vnfProfileId is the vnf descriptor id which defined in NS template  under  node_templates . 


 |image3|

  .. |image3| image:: image2018-12-10_12-1-36.png
   :width: 5.97047in
   :height: 2.63208in

  c.   before instantiate, you should create one volumntype which called root.

3. NS Heal

::

  curl -X PUT \
   http://172.30.3.104:30280/api/nslcm/v1/ns/f0b4c09f-c653-438a-b091-5218b0f806ec/heal \
  -H 'Content-Type: application/json' \
  -H 'Postman-Token: f18754b8-ed68-43b0-ae55-b8b8780e5c6a' \
  -H 'accept: application/json' \
  -H 'cache-control: no-cache' \
  -d '{   "vnfInstanceId": "044b705c-e44d-4733-ab64-987f46d9b567", 
                    "cause": "restartvm",  
                    "additionalParams": {    
                                                        "action": "restartvm",  
                                                         "actionvminfo": {   
                                                         "vmid": "1623cd25-ae6f-4880-8132-15914367e47b",
                                                         "vduid": "",    
                                                          "vmname": "1623cd25-ae6f-4880-8132-15914367e47b"  
        }}  
        }'

Note:
  a.  f0b4c09f-c653-438a-b091-5218b0f806ec  is the ns instance id which create in step 1 : NS create.
  b.   "vnfInstanceId": "044b705c-e44d-4733-ab64-987f46d9b567" is the VNF instanceId, we can get this from A&AI or VF-C DB.
  c.  action only support restartvm  in Casablanca release.
  d.  actionvminfo only supports to include one vm , vmid is the vmid which is the same with the vmid in cloud. 

4. NS Terminate

::

  curl -X POST \
  http://172.30.3.104:30280/api/nslcm/v1/ns/f0b4c09f-c653-438a-b091-5218b0f806ec/terminate \
  -H 'Postman-Token: 5190e46f-f612-432a-90d8-161ea67778b2' \
  -H 'accept: application/json' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  -d 'gracefulTerminationTimeout: 600,
  \terminationType: FORCEFUL'

Note:
  a.  f0b4c09f-c653-438a-b091-5218b0f806ec  is the ns instance id which create in step 1 : NS create.
  b.  terminateType supports FORCEFUL and GRACEFULLc.  gracefulTerminationTimeout is the wait time before execute terminate.

5. NS delete

::

  curl -X DELETE \
  http://172.30.3.104:30280/api/nslcm/v1/ns/f0b4c09f-c653-438a-b091-5218b0f806ec \
  -H 'Postman-Token: 62b35de6-1785-40ed-8026-06d73f9770d8' \
  -H 'cache-control: no-cache'

Note:
  a.  f0b4c09f-c653-438a-b091-5218b0f806ec is the ns instance id which create in step 1 : NS create