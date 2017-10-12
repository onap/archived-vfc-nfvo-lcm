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
  
  VF-C components need to register to MSB when starting, so MSB components should be installed first, \
  you can ref the following link to install MSB.
  http://onap.readthedocs.io/en/latest/submodules/msb/apigateway.git/docs/platform/installation.html
  Note: In the following steps, we use ${MSB_IP} as the ip of msb_apigateway component.

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

