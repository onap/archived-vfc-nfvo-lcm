.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0


VF-C Release Notes
==================

.. note::
..	* This Release Notes must be updated each time the team decides to Release new artifacts.
..	* The scope of this Release Notes is for this particular component. In other words, each ONAP component has its Release Notes.
..	* This Release Notes is cumulative, the most recently Released artifact is made visible in the top of this Release Notes.
..	* Except the date and the version number, all the other sections are optional but there must be at least one section describing the purpose of this new release.
..	* This note must be removed after content has been added.

VF-C includes two main components, NFV-O and GVNFM, to implement life cycle management and FCAPS of VNF and NS. VF-C takes part in end to end service orchestration and close loop automation by working with SO, DCAE and Policy. 
VF-C also provides standard southbound interface to VNFMs and can integrate with multi vendor VNFMs via drivers.

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

 - VFC-896  vim-id in AAI is handled as a mandatory parameter
 - VFC-890  The hard coded SDC user and password in catalog & LCM is not present in SDC
 - VFC-891  The AAI credentials is hard coded in LCM	

**Security Notes**

VFC code has been formally scanned during build time using NexusIQ and all Critical vulnerabilities have been addressed, items that remain open have been assessed for risk and determined to be false positive. The VFC open Critical security vulnerabilities and their risk assessment have been documented as part of the `project <https://wiki.onap.org/pages/viewpage.action?pageId=25437810>`_.

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
- VNF lifecycle management, including VNF nstance creation, termination and healing
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
