.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

VF-C Installation
-----------------
Describe the environment and steps to install VF-C components.


Environment
+++++++++++
VF-C components can run as docker, docker server should be installed before install VF-C components.

Steps
+++++

- Install MSB components.
  
VF-C components need to register to MSB when starting, so MSB components should be installed first, you can ref the following link to install MSB.

http://onap.readthedocs.io/en/latest/submodules/msb/apigateway.git/docs/platform/installation.html

Note: In the following steps, we use ${MSB_IP} as the IP of msb_apigateway component.

- Install vfc-nfvo-lcm component.

::

  docker run -d --name vfc-nslcm -v /var/lib/mysql -e MSB_ADDR=${MSB_IP}:80 nexus3.onap.org:10001/onap/vfc/nslcm
    
For testing, we can use curl command to access the swagger api.

::

  curl http://${MSB_IP}:80/api/nslcm/v1/swagger.json

- Install vfc-nfvo-wfengine components.

Totally, there are two docker images should be installed before you can use the workflow normally, \
one is wfengine-activiti for manage the original activiti service, the other is for manage engine service.


1. Pull related docker images

::

    docker pull $NEXUS_DOCKER_REPO/onap/vfc/wfengine-activiti:$DOCKER_IMAGE_VERSION
    docker pull $NEXUS_DOCKER_REPO/onap/vfc/wfengine-mgrservice:$DOCKER_IMAGE_VERSION

2. Run the two docker images 
     
The first container is wfengine-activiti,there are some parameters should be injected into container. \
OPENPALETTE_MSB_IP represents msb server address and OPENPALETTE_MSB_PORT is the relative port, \
SERVICE_IP represents the docker run environment server address. 

::

     docker run -i -t -d --name vfc_wfengine_activiti -p 8804:8080 -e SERVICE_IP=$OPENO_IP -e SERVICE_PORT=8804
     -e OPENPALETTE_MSB_IP=$OPENO_IP -e OPENPALETTE_MSB_PORT=80 $NEXUS_DOCKER_REPO/onap/vfc/wfengine-activiti:$DOCKER_IMAGE_VERSION

     docker run -i -t -d --name vfc_wfengine_mgrservice -p 8805:10550 -e SERVICE_IP=$OPENO_IP -e SERVICE_PORT=8805 
     -e OPENPALETTE_MSB_IP=$OPENO_IP -e OPENPALETTE_MSB_PORT=80 $NEXUS_DOCKER_REPO/onap/vfc/wfengine-mgrservice:$DOCKER_IMAGE_VERSION

- Install vfc-nfvo-catalog component.

::

  docker run -d --name vfc-catalog -v /var/lib/mysql -e MSB_ADDR=${MSB_IP}:80 nexus3.onap.org:10001/onap/vfc/catalog
    
For testing, we can use curl command to access the swagger api.

::

  curl http://${MSB_IP}:80/api/catalog/v1/swagger.json

- Install vfc-nfvo-resmanagement component.

::

  docker run -d --name vfc-resmanagement -e MSB_ADDR=${MSB_IP}:80 nexus3.onap.org:10001/onap/vfc/resmanagement
    
For testing, we can use curl command to access the swagger api.

::

  curl http://${MSB_IP}:80/api/resmgr/v1/swagger.json

- Install vfc-nfvo-resmanagement component.

::

  docker run -d --name vfc-resmanagement -e MSB_ADDR=${MSB_IP}:80 nexus3.onap.org:10001/onap/vfc/resmanagement
    
For testing, we can use curl command to access the swagger api.

::

  curl http://${MSB_IP}:80/api/resmgr/v1/swagger.json

- Install vfc-nfvo-sfcdriver component.

::

  docker run -d --name vfc-ztesdncdriver -e MSB_ADDR=${MSB_IP}:80 nexus3.onap.org:10001/onap/vfc/ztesdncdriver
    
For testing, we can use curl command to access the swagger api.

::

  curl http://${MSB_IP}:80/api/ztesdncdriver/v1/swagger

- Install vfc-nfvo-emsdriver component.

::

  docker run -d --name vfc-emsdriver -e MSB_ADDR=${MSB_IP}:80 nexus3.onap.org:10001/onap/vfc/emsdriver
    
For testing, we can use curl command to access the swagger api.

::

  curl http://${MSB_IP}:80/api/emsdriver/v1/swagger

- Install vfc-gvnfm components.

::

  docker run -d --name vfc-vnflcm -v /var/lib/mysql -e MSB_ADDR=${MSB_IP}:80 nexus3.onap.org:10001/onap/vfc/vnflcm
  docker run -d --name vfc-vnfmgr -v /var/lib/mysql -e MSB_ADDR=${MSB_IP}:80 nexus3.onap.org:10001/onap/vfc/vnfmgr
  docker run -d --name vfc-vnfres -v /var/lib/mysql -e MSB_ADDR=${MSB_IP}:80 nexus3.onap.org:10001/onap/vfc/vnfres
    
For testing, we can use curl command to access the swagger api.

::

  curl http://${MSB_IP}:80/api/vnflcm/v1/swagger.json
  curl http://${MSB_IP}:80/api/vnfmgr/v1/swagger.json
  curl http://${MSB_IP}:80/api/vnfres/v1/swagger.json

- Install vfc-gvnfmdriver components.

::

  docker run -d --name vfc-gvnfmdriver -e MSB_ADDR=${MSB_IP}:80 nexus3.onap.org:10001/onap/vfc/gvnfmdriver
  docker run -d --name vfc-jujudriver -e MSB_ADDR=${MSB_IP}:80 nexus3.onap.org:10001/onap/vfc/jujudriver
    
For testing, we can use curl command to access the swagger api.

::

  curl http://${MSB_IP}:80/api/gvnfmdriver/v1/swagger.json
  curl http://${MSB_IP}:80/openoapi/jujuvnfm/v1/swagger.json

- Install vfc-svnfmdriver components.

::

  docker run -d --name vfc-ztevmanagerdriver -e MSB_ADDR=${MSB_IP}:80 nexus3.onap.org:10001/onap/vfc/ztevmanagerdriver
  docker run -d --name vfc-svnfm-huawei -e MSB_ADDR=${MSB_IP}:80 nexus3.onap.org:10001/onap/vfc/nfvo/svnfm/huawei
    
For testing, we can use curl command to access the swagger api.

::

  curl http://${MSB_IP}:80/api/ztevmanagerdriver/v1/swagger.json
  curl http://${MSB_IP}:80/api/hwvnfm/v1/swagger.json
