.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0


VF-C Architecture
-----------------
VF-C High Level Architecture.


|image0|

.. |image0| image:: vfc-internal-component.png
   :width: 5.97047in
   :height: 4.63208in

This shows all VF-C components, each component is a standalone microservice, these microservice including:

* nslcm is the core components, mainly responsible for network service management.
* catalog is used to package management, including NS/VNF/PNF package management.
* Resource Manager is used to management the instance created by VF-C and also responsible for resource granting.
* SVNFM Driver, now VF-C has three vendor's Specific VNFM driver, including nokia/huawei/zte driver, each driver is a microservice.
* GVNFM Driver, now have two generic VNFM driver, including gvnfm driver and juju driver. 
* SFC Driver, it migrate from Open-O seed code and now haven't been used in any usecase in ONAP. 
* Wfengine-mgrservice, it provides the workflow management service, now it has been integrated with activiti workflow and provide the unified interface to external components.
* Wfengine-activiti, it is as the activiti work flow microservice.
* Multivim-proxy,provide the multivim indirect mode proxy which can forward virtual resource requests to multivim and do some resource checking.  
* EMS Driver, used for VNF performance and alarm data collection and report to DCAE VES collector.
* GVNFM, it includes three micorservice: vnflcm, vnfmgr and vnfres and the core is vnflcm which responsible for VNF life cycle management.
* DB, provide database services for each VF-C component.  

Note:
  a. SFC Driver migrated from Open-O seed code and now haven't been used in any usecase in ONAP. 
  b. Resource resmanagement is used to do the resource granting, but now VF-C has been integrated with OOF, this component will be deprecated in the future release.
  c. DB provides the stand-alone database microservice in casablanca release, but now VF-C leverages OOM shared MariaDB-Gelera cluster. This repo still has redis to be used by VF-C component. 

 
|image1|

.. |image1| image:: vfc-dependence.png
   :width: 5.97047in
   :height: 4.63208in
   
As you can see in this picture, VF-C has many dependencies with other projects, such as SO, Policy, A&AI, SDC, DCAE, Multi-cloud and so on.

* NFVO provides north bound interface to SO to take part in fulfilling the orchestration and operation of end2end service.And provides standard south bound interface to VNFMs. 

* GVNFM provides LCM for VNFs which do not require a vendor VNFM and works with NFV-O component to take part in fulfilling the LCM of NS.

* VF-C provides VNFM driver interfaces, vendor can implement these integrates to integrate with VF-C. Now, VF-C has integrated with three vendor VNFM, including ZTE, Huawe, Nokia. 

* In addition, VF-C also provides interface to Policy and works with DCAE for Close Loop Automation.
   
* In Casablanca release, VF-C also integrated with OOF to do the resource homing and placement.