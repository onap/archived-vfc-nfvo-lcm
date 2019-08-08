.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0


VF-C Offered APIs
==================

.. contents::
   :depth: 2

Now VF-C provides the NS life cycle management APIs to UUI,SO,Policy and package management APIs to UUI.
For VNFM vendor, VF-C also provides the VNFM integration APIs, they can reference these APIs to implement their VNFMDriver to integrate with VF-C and ONAP.

  |image0|

  .. |image0| image:: vfc-api.png
   :width: 1000px
   :height: 600px

NFVO provided interfaces:

* Network Service LCM interface

  Provides Network Service LCM interface(NS instantiate/scale/heal/terminate/query/…) 
  
* VNF Operation Granting interface

  Provides VNF Operation Granting interface and make granting decision
  
* NS package management interface

  Provides runtime NS package management interface
  
* VNF package management interface

  Provides runtime VNF package management interface


GVNFM provided interfaces:

* VNF LCM interface

  Provides the VNF LCM interface(VNF instantiate/terminate/query/…)

More interface defination can be found in the following part.

VFC Northbound API
------------------

Network services lifecycle management APIs

In Dublin release, VF-C provides SOL005 compliant APIs as follows

::

    api/nslcm/v1/ns_instances
    api/nslcm/v1/ns_instances/(?P<ns_instance_id>[0-9a-zA-Z_-]+)
    api/nslcm/v1/ns_instances/(?P<ns_instance_id>[0-9a-zA-Z_-]+)/instantiate
    api/nslcm/v1/ns_instances/(?P<ns_instance_id>[0-9a-zA-Z_-]+)/update
    api/nslcm/v1/ns_instances/(?P<ns_instance_id>[0-9a-zA-Z_-]+)/scale
    api/nslcm/v1/ns_instances/(?P<ns_instance_id>[0-9a-zA-Z_-]+)/heal
    api/nslcm/v1/ns_instances/(?P<ns_instance_id>[0-9a-zA-Z_-]+)/terminate
    api/nslcm/v1/ns_lcm_op_occs/(?P<lcmopoccid>[0-9a-zA-Z_-]+)
    api/nslcm/v1/subscriptions
    api/nslcm/v1/ns_lcm_op_occs

But for the previous APIs, we still keep in Dublin, but the following APIs will be deprecated in the future release

::

	api/nslcm/v1/ns
    api/nslcm/v1/ns/(?P<ns_instance_id>[0-9a-zA-Z_-]+)/instantiate
    api/nslcm/v1/ns/(?P<ns_instance_id>[0-9a-zA-Z_-]+)/terminate
    api/nslcm/v1/ns/(?P<ns_instance_id>[0-9a-zA-Z_-]+)
    api/nslcm/v1/ns/(?P<ns_instance_id>[0-9a-zA-Z_-]+)/postdeal
    api/nslcm/v1/ns/(?P<ns_instance_id>[0-9a-zA-Z_-]+)/scale
    api/nslcm/v1/ns/(?P<ns_instance_id>[0-9a-zA-Z_-]+)/heal
    api/nslcm/v1/ns/(?P<ns_instance_id>[0-9a-zA-Z_-]+)/update
	

More APIs defination and reference can be found in the following page:

.. toctree::
   :maxdepth: 1
   
   NSLCM_API/index


VNFM Integration APIs 
---------------------

VNFM Driver Integration Related APIs, these APIs are mainly provided for Vendor, if you want to integrate with VF-C and ONAP, you can reference these APIs to implement your VNFMDriver
These integration APIs includ two part:

* The VNF life cycle management APIs for the VNFMDriver should be implemented
* The NFVO APIs for the VNFMDri1 will be request, like grant APIs 

.. toctree:: 
   :maxdepth: 1
   
   VNFMDriver_API/index



GVNFM Northbound & Southbound APIs
----------------------------------

VF-C provides the Generic VFNM , it can be as the GVNFM reference implementaton.
Now the Northbound APIs of GVNFM has been compete with SOL003 and it now can be integrate with VF-C NFVO.
In tosca-based vCPE use case, the GVNFM function have been verified in Casablanca release.

GVNFM Northbound & Southbound APIs for VNF Integration

.. toctree:: 
   :maxdepth: 1

   VNFLCM_API/index


CATALOG  APIs
-------------

CATALOG APIs for VNF Integration

.. toctree::
   :maxdepth: 1

   CATALOG_API/index   
