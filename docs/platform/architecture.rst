.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0


VF-C Architecture
-----------------
VF-C High Level Architecture.


|image0|

.. |image0| image:: vfc-arc.png
   :width: 5.97047in
   :height: 4.63208in
   
As you can see in this picture, VF-C has many dependencies with other projects, such as SO, Policy, A&AI, SDC, DCAE, Multi-cloud and so on.

* NFVO provides north bound interface to SO to take part in fulfilling the orchestration and operation of end2end service.And provides standard south bound interface to VNFMs. 

* GVNFM provides LCM for VNFs which do not require a vendor VNFM and works with NFV-O component to take part in fulfilling the LCM of NS.

* VF-C provides VNFM driver interfaces, vendor can implement these integrates to integrate with VF-C. Now, VF-C has integrated with three vendor VNFM, including ZTE, Huawe, Nokia. 

* In addition, VF-C also provides interface to Policy and works with DCAE for Close Loop Automation.
   
