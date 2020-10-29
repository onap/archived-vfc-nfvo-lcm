.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. _release_notes:


VF-C Release Notes
==================

VF-C includes two main components, NFV-O and GVNFM, to implement life cycle
management and FCAPS of VNF and NS. VF-C takes part in end to end service
orchestration and close loop automation by working with SO, DCAE and Policy.
VF-C also provides standard southbound interface to VNFMs and can integrate
with multi vendor VNFMs via drivers.


Version: 1.4.1
--------------

:Release Date: 2020-10-29

**New Features**

- Functional Enhancement:

1. Improve Instance storage function
2. Remove components which are no longer used or maintained.

- Maturity Enhancement:

1. Update to Java 11
2. Optimize docker image
3. Update dependency lib
4. Increase code coverage


Released components:

NFVO
 - vfc-nfvo-lcm 1.4.1
 - vfc-nfvo-driver-gvnfm-gvnfmadapter 1.4.0
 - vfc-nfvo-driver-svnfm-ztedriver 1.3.8
 - vfc-nfvo-driver-svnfm-huawei 1.3.8
 - vfc-nfvo-db 1.3.4

GVNFM
 - vfc-gvnfm-vnflcm 1.4.0
 - vfc-gvnfm-vnfmgr 1.3.9
 - vfc-gvnfm-vnfres 1.3.8

**Known Issues**

  Though VFC itself has migrated to python 3, however, the deployment of VFC still has python 2.7 pods since it uses public mariadb image. Please refer to: https://jira.onap.org/browse/VFC-1740 for details.


**Security Notes**
    NA

Quick Links:

- `VFC project page <https://wiki.onap.org/display/DW/Virtual+Function+Controller+Project>`_
- `Passing Badge information for VFC <https://bestpractices.coreinfrastructure.org/en/projects/1608>`_

**Upgrade Notes**
    NA

**Deprecation Notes**

 The following components are not in the scope of the Guilin release since they are no longer used or maintained.

 - vfc/nfvo/driver/ems
 - vfc/nfvo/multivimproxy
 - vfc/nfvo/driver/vnfm/gvnfm/juju
 - vfc/nfvo/driver/vnfm/svnfm/nokia
 - vfc/nfvo/wfengine
 - vfc/nfvo/driver/sfc

**Other**
    NA


Version: 1.3.9
--------------

:Release Date: 2020-03-17

**New Features**

- Functional Enhancement:

1. Migrate VF-C catalog to Modeling etsicatalog 
2. Using the common database (MariaDB) and encrypting the database password.
3. Remove the root permission and change the user of VFC project to ONAP.
4. Add the function of auto register MSB switch for startup project.
5. Increase the communication access form between components through the HTTPS encrypted access form of MSB.
6. SOL005 compliance NS instantiation, query and termination commands have been added to cli.


- Maturity Enhancement:

1. Enhance the security of database access
2. Enhance the stability of instantiation process and improve efficiency and productivity.
3. Improve the stability of instance termination process and deletion process, and improve the success rate of subscription record deletion.
4. Adapt to MSB https for microservice service registration and access.


Released components:

NFVO
 - vfc-nfvo-lcm 1.3.9
 - vfc-nfvo-resmanagement 1.3.1
 - vfc-nfvo-driver-gvnfm-gvnfmadapter 1.3.9
 - vfc-nfvo-driver-gvnfm-juju 1.3.9
 - vfc-nfvo-driver-svnfm-ztedriver 1.3.6
 - vfc-nfvo-driver-svnfm-huawei 1.3.6
 - vfc-nfvo-driver-svnfm-Nokia2 1.3.6
 - vfc-nfvo-db 1.3.3
 - vfc-nfvo-sfc 1.3.1
 - vfc-nfvo-ems 1.3.1
 - vfc-nfvo-multivimproxy 1.3.1
 - vfc-nfvo-wfengine-mgrservice 1.3.3
 - vfc-nfvo-wfengine-activiti 1.3.3

GVNFM
 - vfc-gvnfm-vnflcm 1.3.9
 - vfc-gvnfm-vnfmgr 1.3.8
 - vfc-gvnfm-vnfres 1.3.7

**Bug Fixes**

 - Fix bug for duplication query and delete vserver and network in AAI resource during terminating ns.
 - Fix terminate ns API is unstable.
 - Fix bug for fail to delete subscription for vnfm during terminating ns.
 - Fix the bug for fail parse contextArray, initial it to [].
 - Fix the deduplication AAI resource issues.
 - Fix the bug of vim_id data type error when creating vnfs.
 - Fix the failure of parsing the acquired data format during SFC creation.
 - Fix the failure of blocking due to multithreading during instantiation.

**Known Issues**


**Security Notes**
    NA

Quick Links:

- `VFC project page <https://wiki.onap.org/display/DW/Virtual+Function+Controller+Project>`_
- `Passing Badge information for VFC <https://bestpractices.coreinfrastructure.org/en/projects/1608>`_
- `CLI command about VFC operation <https://onap.readthedocs.io/en/latest/submodules/vfc/nfvo/lcm.git/docs/platform/cli-userguide/index.html#vfc-part>`_

**Upgrade Notes**
    NA

**Deprecation Notes**
    NA

**Other**
    NA




Version: 1.3.4
--------------

:Release Date: 2019-08-20

**New Features**

- Functional Enhancement:

1. Upgrade component environments from Python 2 to Python 3 and upgrade package dependencies to stable versions
2. Good connectivity and stability of information transmission between nslcm drivers and vnflcm
3. Solving Layer_protocol Protocol Protocol Supporting Uniformity and Increasing Compatibility

- Standard Alignment-SOL005 Alignment

- Maturity Enhancement:

1. Increase read and write stability of AAI interaction
2. Enhance the stability of vnflcm and nslcm message subscription notification function
3. Enhance the reliability of MSB registration information and message reading



Released components:

NFVO
 - vfc-nfvo-lcm 1.3.4
 - vfc-nfvo-catalog 1.3.4
 - vfc-nfvo-driver-gvnfm-gvnfmadapter 1.3.5
 - vfc-nfvo-driver-svnfm-ztedriver 1.3.3
 - vfc-nfvo-db 1.3.1
GVNFM
 - vfc-gvnfm-vnflcm 1.3.4
 - vfc-gvnfm-vnfmgr 1.3.4
 - vfc-gvnfm-vnfres 1.3.4

**Bug Fixes**

 - Fix bug for failure in creating subscriptions for vnfm
 - Fix network name conflict problem when creating network writing to AAI
 - Fix bug for failure in creating ns vl to aai
 - Fix the bug for table NFVO_NSINST field status update incorrect

**Known Issues**


**Security Notes**

VFC code has been formally scanned during build time using NexusIQ and all Critical
vulnerabilities have been addressed, items that remain open have been assessed
for risk and determined to be false positive. The VFC open Critical security
vulnerabilities and their risk assessment have been documented as part
of the `project <https://wiki.onap.org/pages/viewpage.action?pageId=68542814>`_.

Quick Links:

- `VFC project page <https://wiki.onap.org/display/DW/Virtual+Function+Controller+Project>`_
- `Passing Badge information for VFC <https://bestpractices.coreinfrastructure.org/en/projects/1608>`_
- `Project Vulnerability Review Table for VFC <https://wiki.onap.org/pages/viewpage.action?pageId=68542814>`_

**Upgrade Notes**
    NA

**Deprecation Notes**
    NA

**Other**
    NA




Version: 1.3.0
--------------

:Release Date: 2019-06-06

**New Features**

- Functional Enhancement: 

1. Upgrade Multicloud API to support consistent identification of cloud region functional requirement 
2. OOF Integration Optimization.Optimize the methodology for VNF(vdu) placement, add the process for placement with selected candidates(VIM)
3. Align VNFD SOL2.5.1 and model multi-version support

- Standard Alignment-SOL005 Alignment

- Maturity Enhancement:

1. Mysql  DB migrate to OOM shared MariaDB Galera Cluster
2. Configuration inject automatically
3. Add data persistent storage to avoid data loss due to pod restart



Released components:

NFVO
 - vfc-nfvo-lcm 1.3.2
 - vfc-nfvo-catalog 1.3.2
 - vfc-nfvo-resmgr 1.3.0
 - vfc-nfvo-driver-emsdriver 1.3.0
 - vfc-nfvo-driver-gvnfm-gvnfmadapter 1.3.3
 - vfc-nfvo-driver-gvnfm-jujudriver 1.3.1
 - vfc-nfvo-driver-svnfm-ztedriver 1.3.1
 - vfc-nfvo-driver-svnfm-huaweidriver 1.3.0
 - vfc-nfvo-driver-svnfm-nokiav2driver 1.3.1
 - vfc-nfvo-driver-sfc-ztesfcdriver 1.3.1
 - vfc-nfvo-multivimproxy 1.3.0
 - vfc-nfvo-db 1.3.0
GVNFM
 - vfc-gvnfm-vnflcm 1.3.2
 - vfc-gvnfm-vnfmgr 1.3.2
 - vfc-gvnfm-vnfres 1.3.2
Workflow
 - workflow-engine-mgr-service 1.3.0
 - activiti-extension 1.3.0

**Bug Fixes**

**Known Issues**

 - `VFC-1402 <https://jira.onap.org/browse/VFC-1402>`_ Lost connection to Mariadb server during query in vnflcm.
 - `VFC-1411 <https://jira.onap.org/browse/VFC-1411>`_ The network can not be deleted in ns terminate.

**Security Notes**

VFC code has been formally scanned during build time using NexusIQ and all Critical
vulnerabilities have been addressed, items that remain open have been assessed
for risk and determined to be false positive. The VFC open Critical security
vulnerabilities and their risk assessment have been documented as part
of the `project <https://wiki.onap.org/pages/viewpage.action?pageId=51282550>`_.

Quick Links:

- `VFC project page <https://wiki.onap.org/display/DW/Virtual+Function+Controller+Project>`_
- `Passing Badge information for VFC <https://bestpractices.coreinfrastructure.org/en/projects/1608>`_
- `Project Vulnerability Review Table for VFC <https://wiki.onap.org/pages/viewpage.action?pageId=51282550>`_

**Upgrade Notes**
	NA

**Deprecation Notes**
	NA

**Other**
	NA

Version: 1.2.0
--------------

:Release Date: 2018-11-30

**New Features**

- NS Orchestration supports PNF:1.NSLCM supports NSD, composed of VNF, PNF, and VL;2.Catalog supports PNFD and updates NSD DM
- Hardware Platform Awareness (HPA) Support:1.integrate with OOF;2.VF-C can parse R2+ TOSCA MODEL which includes HPA feature
- Standard Alignment:SOL003 Alignment in GVNFM and Catalog
- Standalone DB Microservice

Released components:

NFVO
 - vfc-nfvo-lcm 1.2.2
 - vfc-nfvo-catalog 1.2.2
 - vfc-nfvo-resmgr 1.2.1
 - vfc-nfvo-driver-emsdriver 1.2.1
 - vfc-nfvo-driver-gvnfm-gvnfmadapter 1.2.2
 - vfc-nfvo-driver-gvnfm-jujudriver 1.2.1
 - vfc-nfvo-driver-svnfm-ztedriver 1.2.1
 - vfc-nfvo-driver-svnfm-huaweidriver 1.2.1
 - vfc-nfvo-driver-svnfm-nokiav2driver 1.2.1
 - vfc-nfvo-driver-sfc-ztesfcdriver 1.2.0
 - vfc-nfvo-multivimproxy 1.2.1
 - vfc-nfvo-db 1.2.2
GVNFM
 - vfc-gvnfm-vnflcm 1.2.2
 - vfc-gvnfm-vnfmgr 1.2.1
 - vfc-gvnfm-vnfres 1.2.1
Workflow
 - workflow-engine-mgr-service
 - activiti-extension

**Bug Fixes**

**Known Issues**

 - `VFC-896 <https://jira.onap.org/browse/VFC-896>`_  vim-id in AAI is handled as a mandatory parameter
 - `VFC-890 <https://jira.onap.org/browse/VFC-890>`_  The hard coded SDC user and password in catalog & LCM is not present in SDC
 - `VFC-891 <https://jira.onap.org/browse/VFC-891>`_  The AAI credentials is hard coded in LCM
 - SDC-1897 - Parser exported CSAR with error OPEN (Will be fixed at Dublin),VFC could ignore that error. To ignore that error, we need either apply the patch at https://jira.opnfv.org/browse/PARSER-187 locally in nfv-toscaparser which VFC uses or wait for nfv-toscaparser got that fixed.

**Security Notes**

VFC code has been formally scanned during build time using NexusIQ and all Critical
vulnerabilities have been addressed, items that remain open have been assessed
for risk and determined to be false positive. The VFC open Critical security
vulnerabilities and their risk assessment have been documented as part
of the `project <https://wiki.onap.org/pages/viewpage.action?pageId=45298878>`_.

Quick Links:

- `VFC project page <https://wiki.onap.org/display/DW/Virtual+Function+Controller+Project>`_
- `Passing Badge information for VFC <https://bestpractices.coreinfrastructure.org/en/projects/1608>`_
- `Project Vulnerability Review Table for VFC <https://wiki.onap.org/pages/viewpage.action?pageId=45298878>`_

**Upgrade Notes**
	NA

**Deprecation Notes**
	NA

**Other**
	NA

Version: 1.1.0
--------------

:Release Date: 2018-06-07

**New Features**

- NS/VNF manual scaling supporting for VoLTE use case
- VNF Integration, integration with VNF via GVNFM
- S3P improvement

Released components:

NFVO
 - vfc-nfvo-lcm
 - vfc-nfvo-catalog
 - vfc-nfvo-resmgr
 - vfc-nfvo-driver-emsdriver
 - vfc-nfvo-driver-gvnfm-gvnfmadapter
 - vfc-nfvo-driver-gvnfm-jujudriver
 - vfc-nfvo-driver-svnfm-ztedriver
 - vfc-nfvo-driver-svnfm-huaweidriver
 - vfc-nfvo-driver-svnfm-nokiadriver
 - vfc-nfvo-driver-svnfm-nokiav2driver
 - vfc-nfvo-driver-sfc-ztesfcdriver
 - vfc-nfvo-multivimproxy
GVNFM
 - vfc-gvnfm-vnflcm
 - vfc-gvnfm-vnfmgr
 - vfc-gvnfm-vnfres
Workflow
 - workflow-engine-mgr-service
 - activiti-extension

**Bug Fixes**

This is the initial release

**Known Issues**

 - `VFC-896 <https://jira.onap.org/browse/VFC-896>`_  vim-id in AAI is handled as a mandatory parameter
 - `VFC-890 <https://jira.onap.org/browse/VFC-890>`_  The hard coded SDC user and password in catalog & LCM is not present in SDC
 - `VFC-891 <https://jira.onap.org/browse/VFC-891>`_  The AAI credentials is hard coded in LCM

**Security Notes**

VFC code has been formally scanned during build time using NexusIQ and all Critical
vulnerabilities have been addressed, items that remain open have been assessed
for risk and determined to be false positive. The VFC open Critical security
vulnerabilities and their risk assessment have been documented as part
of the `project <https://wiki.onap.org/pages/viewpage.action?pageId=25437810>`_.

Quick Links:

- `VFC project page <https://wiki.onap.org/display/DW/Virtual+Function+Controller+Project>`_
- `Passing Badge information for VFC <https://bestpractices.coreinfrastructure.org/en/projects/1608>`_
- `Project Vulnerability Review Table for VFC <https://wiki.onap.org/pages/viewpage.action?pageId=25437810>`_

**Upgrade Notes**
	NA

**Deprecation Notes**
	NA

**Other**
	NA

Version: 1.0.0
--------------

:Release Date: 2017-11-16

**New Features**

- NS lifecycle management, including NS instance creation, termination and healing
- VNF lifecycle management, including VNF instance creation, termination and healing
- VNF FCAPS, collecting FCAPS data from vendor EMS
- VNFM Integration, integration with specific VNFMs of vendors to deploy commercial VNFs
- VNF Integration, integration with VNF via GVNFM

Released components:

NFVO
 - vfc-nfvo-lcm
 - vfc-nfvo-catalog
 - vfc-nfvo-resmgr
 - vfc-nfvo-driver-emsdriver
 - vfc-nfvo-driver-gvnfm-gvnfmadapter
 - vfc-nfvo-driver-gvnfm-jujudriver
 - vfc-nfvo-driver-svnfm-ztedriver
 - vfc-nfvo-driver-svnfm-huaweidriver
 - vfc-nfvo-driver-svnfm-nokiadriver
 - vfc-nfvo-driver-sfc-ztesfcdriver
GVNFM
 - vfc-gvnfm-vnflcm
 - vfc-gvnfm-vnfmgr
 - vfc-gvnfm-vnfres
Workflow
 - workflow-engine-mgr-service
 - activiti-extension

**Bug Fixes**

This is the initial release

**Known Issues**

None

**Security Issues**

None

**Upgrade Notes**

This is the initial release

**Deprecation Notes**

This is the initial release

**Other**
	NA

===========

End of Release Notes
