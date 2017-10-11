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

- First, MSB components should be installed, you can ref the following link to install MSB.

  http://onap.readthedocs.io/en/latest/submodules/msb/apigateway.git/docs/platform/installation.html

- Install vfc-nfvo-lcm component.

::

docker run -d --name vfc-nslcm -v /var/lib/mysql -e MSB_ADDR=${MSB_IP}:80 nexus3.onap.org:10001/onap/vfc/nslcm

For testing, we can use curl command to access the swagger api.

::

curl http://${MSB_IP}:80/api/nslcm/v1/swagger.json


