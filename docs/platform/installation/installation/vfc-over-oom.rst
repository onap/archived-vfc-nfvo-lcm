.. contents::
   :depth: 3
..

   **VFC Installation over OOM**
   **V0.1**

1 **Scope**
=============

This is a guide to help developer or tester to try to install VF-C over OOM

2 **Component & function**
==========================

Repos:
~~~~~~

Now VF-C have the following repos in https://gerrit.onap.org/r/admin/repos/q/filter:vfc

.. list-table::
   :widths: 30 60 10
   :header-rows: 1

   * - URL
     - Method
     - Description
   * - vfc/nfvo/lcm
     - NS life cycle management
     -
   * - vfc/nfvo/driver/vnfm/svnfm
     - Specific VNFM drivers
     -
   * - vfc/nfvo/driver/vnfm/gvnfm
     - Generic VNFM drivers
     -
   * - vfc/nfvo/db
     - Stand-alone database microservice, provides the database service for each VF-C component
     -
   * - vfc/nfvo/driver/ems
     - VNF fcaps collect
     - Deprecated
   * - vfc/nfvo/driver/sfc
     - SFC Driver
     - Deprecated
   * - vfc/nfvo/resmanagement
     - NS Resource Management
     - Deprecated
   * - vfc/nfvo/wfengine
     - Work flow engine
     - Deprecated
   * - vfc/nfvo/multivimproxy
     - Multi-vim proxy provides the multivim indirect mode proxy
     - Deprecated
   * - vfc/gvnfm/vnflcm
     - Generic VNFM VNF LCM
     -
   * - vfc/gvnfm/vnfmgr
     - Generic VNFM VNF Mgr
     -
   * - vfc/gvnfm/vnfres
     - Generic VNFM VNF Resource Management
     -

VF-C Docker Images:
~~~~~~~~~~~~~~~~~~~~~~~~

::

  nexus3.onap.org:10001/onap/vfc/nslcm
  nexus3.onap.org:10001/onap/vfc/db
  nexus3.onap.org:10001/onap/vfc/gvnfmdriver
  nexus3.onap.org:10001/onap/vfc/nfvo/svnfm/huawei
  nexus3.onap.org:10001/onap/vfc/ztevnfmdriver
  nexus3.onap.org:10001/onap/vfc/vnflcm
  nexus3.onap.org:10001/onap/vfc/vnfmgr
  nexus3.onap.org:10001/onap/vfc/vnfres


Deprecated from Guilin Release:
::

  nexus3.onap.org:10001/onap/vfc/nfvo/svnfm/nokia
  nexus3.onap.org:10001/onap/vfc/nfvo/svnfm/nokiav2
  nexus3.onap.org:10001/onap/vfc/emsdriver
  nexus3.onap.org:10001/onap/vfc/jujudriver
  nexus3.onap.org:10001/onap/vfc/multivimproxy
  nexus3.onap.org:10001/onap/vfc/resmanagement
  nexus3.onap.org:10001/onap/vfc/wfengine-activiti
  nexus3.onap.org:10001/onap/vfc/wfengine-mgrservice
  nexus3.onap.org:10001/onap/vfc/ztesdncdriver


**3 VF-C Deployment**
=====================

For initialization of docker there are 2 deployment options currently used in ONAP:
- using heat template
- using OOM

From Casablanca release, OOM is the recommended way, so here mainly give the steps for OOM based deployment

For OOM deployment you can refer to the OOM section in ONAP documentation.

.. * https://docs.onap.org/projects/onap-oom/en/latest/oom_user_guide.html#oom-user-guide
.. * https://docs.onap.org/projects/onap-oom/en/latest/oom_quickstart_guide.html#oom-quickstart-guide

1. First ensure VF-C is marked true against field enabled in the oom/kubernetes/onap/values.yaml for successful deployment.

::

	vfc:
		enabled: true
	vid:
		enabled: true
	vnfsdk:
		enabled: true
	vvp:
		enabled: false



2. Upgrade Images in OOM charts

Ensure the component version is right, you should check the respective component image version in VF-C charts.
If you need update the version, please modify values.yaml

eg.

::
	
    oom/kubernetes/vfc/charts/vfc-nslcm/values.yaml

    #################################################################
    # Application configuration defaults.
    #################################################################
    # application image
    flavor: small

    repository: nexus3.onap.org:10001
    image: onap/vfc/nslcm:1.4.1
    pullPolicy: Always
	

3. Rebuild all repos in helm

Every time you change the charts, you need to rebuild all repos to ensure the change can take effect.

Step1: Build vfc repo

::

	cd oom/kubernetes
	make vfc 

Step2: Build ONAP repo

::

	cd oom/kubernetes
	make onap(here can also execute make all)

Step3: Delete the release already deployed

::

	cd oom/kubernetes
	helm delete dev-vfc --purge

Step4: Deploy the new pods

::

	cd oom/kubernetes
	helm install local/vfc --namespace onap --name dev-vfc


Now VF-C will be upgraded with the new image version 

You will see all the pods are running
	
::

    dev-vfc-generic-vnfm-driver-6fcf454665-6pmfv       2/2     Running            0          11d
    dev-vfc-huawei-vnfm-driver-6f6c465c76-ktpch        2/2     Running            0          11d
    dev-vfc-mariadb-0                                  2/2     Running            0          11d
    dev-vfc-mariadb-1                                  2/2     Running            2          11d
    dev-vfc-mariadb-2                                  2/2     Running            0          11d
    dev-vfc-nslcm-6dd99f94f4-vxdkc                     2/2     Running            0          11d
    dev-vfc-redis-5d7d494fdf-crv8c                     1/1     Running            0          11d
    dev-vfc-vnflcm-5497c66465-f5mh7                    2/2     Running            0          11d
    dev-vfc-vnfmgr-5459b488d9-6vg75                    2/2     Running            0          11d
    dev-vfc-vnfres-5577d674cf-g9fz7                    2/2     Running            0          11d
    dev-vfc-zte-vnfm-driver-6685b74f95-r5phc           2/2     Running            2          11d


**4 VF-C health check**
========================

When VF-C pods are up, if you want to check the service status, you can visit the following APIs in K8S cluster to check.
These swagger API will also show the APIs VF-C provided.

+--------------------------+---------------------------------------------------------------------------+
|     **Component Name**   |     health check API                                                      |
+==========================+===========================================================================+
|     vfc/nfvo/lcm         |     http://ClusterIP:8403/api/nslcm/v1/swagger.yaml                       |
+--------------------------+---------------------------------------------------------------------------+
|vfc/gvnfm/vnflcm          |     http://ClusterIP:8801/api/vnflcm/v1/swagger.yaml                      |
+--------------------------+---------------------------------------------------------------------------+
|vfc/gvnfm/vnfmgr          |     http://ClusterIP:8803/api/vnfmgr/v1/swagger.yaml                      |
+--------------------------+---------------------------------------------------------------------------+
|vfc/gvnfm/vnfres          |     http://ClusterIP:8802/api/vnfres/v1/swagger.yaml                      |
+--------------------------+---------------------------------------------------------------------------+

Here are only a few components as an example.

Take vnflcm as an example, you can visit the API as follow:

::

    ubuntu@oom-mr01-rancher:~$ kubectl -n onap get svc|grep vnflcm
    vfc-vnflcm                         ClusterIP      10.43.71.4      <none>                                 8801/TCP                                                      87d
    ubuntu@oom-mr01-rancher:~$ curl http://10.43.71.4:8801/api/vnflcm/v1/swagger.json
    {"swagger": "2.0", "info": {"title": "vnflcm API", "description": "\n\nThe `swagger-ui` view can be found [here](/api/vnflcm/v1/swagger).\n
    The `ReDoc` view can be found [here](/api/vnflcm/v1/redoc).\nThe swagger YAML document can be found [here](/api/vnflcm/v1/swagger.yaml).\n
    The swagger JSON document can be found [here](/api/vnflcm/v1/swagger.json)."........
	
	
Because VF-C expose service by ClusterIP, so that you can only visit the APIs in K8S cluster.

If you want to visit VF-C APIs outside of K8S cluster, you can visit these APIs via MSB, because all VF-C APIs have been registered to MSB.

You can execute the following steps:

::

	ubuntu@oom-mr01-rancher:~$ kubectl -n onap get pod -o wide|grep msb-iag
	dev-msb-msb-iag-6fbb5b4dbd-pxs8z                              2/2       Running            4          28d       10.42.72.222    mr01-node1   <none>
	ubuntu@oom-mr01-rancher:~$ cat /etc/hosts |grep mr01-node1
	172.60.2.39   mr01-node1
	ubuntu@oom-mr01-rancher:~$ kubectl -n onap get svc|grep msb-iag
	msb-iag                            NodePort       10.43.213.250   <none>                                 80:30280/TCP,443:30283/TCP                                    87d
	ubuntu@oom-mr01-rancher:~$ curl http://172.60.2.39:30280/api/vnflcm/v1/swagger.json
	{"swagger": "2.0", "info": {"title": "vnflcm API", "description": "\n\nThe `swagger-ui` view can be found [here](/api/vnflcm/v1/swagger).\n
	The `ReDoc` view can be found [here](/api/vnflcm/v1/redoc).\nThe swagger YAML document can be found [here](/api/vnflcm/v1/swagger.yaml).\n
	The swagger JSON document can be found [here](/api/vnflcm/v1/swagger.json)."........


You can visit the http://172.60.2.39:30280/api/vnflcm/v1/swagger.json in the browser


**5 Debug and Testing in running Pod**
======================================

When you are doing the testing and would like to replace some new file like binary or some script and want to check the new result.

Take vfc-nslcm pod as an example:

::

    kubectl -n onap edit deployment dev-vfc-nslcm

    spec:
      containers:
      - args:
        - -c
        - MYSQL_AUTH=${MYSQL_ROOT_USER}:${MYSQL_ROOT_PASSWORD} ./docker-entrypoint.sh
        command:
        - sh
        env:
        - name: MSB_HOST
          value: https://msb-iag:443
        - name: SSL_ENABLED
          value: "false"
        - name: MYSQL_ADDR
          value: vfc-mariadb:3306
        - name: MYSQL_ROOT_USER
          value: root
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              key: password
              name: dev-vfc-db-root-pass
        - name: REDIS_HOST
          value: vfc-redis
        - name: REDIS_PORT
          value: "6379"
        - name: REG_TO_MSB_WHEN_START
          value: "false"
        image: 192.168.235.22:10001/onap/vfc/nslcm:1.4.1
        imagePullPolicy: IfNotPresent
        livenessProbe:
          failureThreshold: 3
          initialDelaySeconds: 120
          periodSeconds: 10
          successThreshold: 1
          tcpSocket:
            port: 8403
          timeoutSeconds: 1
        name: vfc-nslcm
        ports:
        - containerPort: 8403
          protocol: TCP
        readinessProbe:

Then you can replace the value into the pod.


**6 Kubectl basic command**
======================================

Basic operation of kubernests cluster(Take the namespace of onap in linux client as an example)

* Check the cluster node

::
            
    kubectl  get node
                 
* Check cluster namespace

::
               
    kubectl  get ns
                
* View the pod information and the pod on which the node is located, under the namespace specified (for example, namespace on onap)

::
                     
    kubectl get pod -o wide -n onap

* Connected to the docker in pod

::
      
    Check the docker's name , return two dockers' name after execution, -c specifie the docker that needed ti go in.     
            
    kubectl -n onap get pod dev-vfc-nslcm-68cb7c9878-v4kt2 -o jsonpath={.spec.containers[*].name}
                
    kubectl -n onap exec -it dev-vfc-nslcm-68cb7c9878-v4kt2 -c vfc-nslcm /bin/bash
            
* Copy files (take the catalog example). When the data copy is lost after the pod is restarted or migrated, the multi-copy pod copy operation only exists for the current pod

::
    
    Copy from local to dockers in pod

    kubectl -n onap cp copy_test.sh  dev-vfc-nslcm-68cb7c9878-v4kt2: -c vfc-nslcm
                
    Copy pod's content to local machine
                
    kubectl -n onap cp dev-vfc-nslcm-68cb7c9878-v4kt2:copy_test.sh -c vfc-nslcm /tmp/copy_test.sh
                
* Remote command (to see the current path of the container as an example)

::
    
    kubectl -n onap exec -it dev-vfc-nslcm-68cb7c9878-v4kt2 -c vfc-nslcm pwd
                
* View pod basic information and logs (no -c parameter added for single container pod)

::
                
    kubectl -n onap describe pod dev-vfc-nslcm-68cb7c9878-v4kt2
                  
    kubectl -n onap logs dev-vfc-nslcm-68cb7c9878-v4kt2 -c vfc-nslcm
  
* Check the service listening port and manually expose the port, which is commonly used for testing, such as nginx under test namespace

::
                 
    1>Build namespace
	
        kubectl create namespace test
                  
    2>create pod with 3 replication
	
        kubectl run nginx --image=nginx --replicas=3 -n test
                  
    3>Pod exposed ports for nginx (target port, source port target-port)
                        
        kubectl expose deployment nginx --port=88 --target-port=80 --type=LoadBalancer -n test
                  
        or
                  
        kubectl expose deployment nginx --port=88 --target-port=80 --type=NodePort -n test

    4> Check svc(ports that pod exposed , The cluster internally accesses this pod via port 88., external access to the cluster using floatingip+30531)
                  
        kubectl get svc -n test
                  
        NAME      TYPE           CLUSTER-IP     EXTERNAL-IP   PORT(S)          AGE
        nginx     LoadBalancer   10.43.45.186   10.0.0.3      88:30531/TCP   3m
                   
        NAME      TYPE           CLUSTER-IP     EXTERNAL-IP              PORT(S)                    AGE
        nginx     NodePort       10.43.45.186                               88:30531/TCP   3m
                   
                   
        Nodes within the CLUSTER can be accessed via cluster-ip +88 port
        Outside the cluster, it is accessible via either EXTERNAL IP or the Floating IP+30531, which is the node name of the pod
        The floatingip corresponding to the node name can be viewed in the /etc/hosts of the rancher machine or in the documentation

                               
* Modify the container image and pod strategy (deployment, statefulset), the completion of modification will trigger the rolling update

::
                  
    1>To determine whether the pod is a stateful application (efullset) or a stateful application (deployment)
                    
        kubectl  -n onap describe  pod dev-vfc-nslcm-68cb7c9878-v4kt2 |grep Controlled
                    
    2>Stateless application deployment              
                    
        kubectl  -n onap get deploy |grep  nslcm
                    
        kubectl -n onap edit deploy  dev-vfc-nslcm-68cb7c9878-v4kt2
            
    3>Stateful application statefulset
                    
        kubectl  -n onap get statefulset |grep cassandra
                        
        kubectl -n onap edit statefulset dev-aai-cassandra                    
                    
              
* Restart pod(After removing the pod, deployment will recreate a same pod and randomly assign it to any node.)

::
                 
    kubectl -n onap delete pod dev-vfc-nslcm-68cb7c9878-v4kt2 -c vfc-nslcm
              

* View the virtual machine where the portal-app resides in order to add host resolution          

::
      
    10.0.0.13 corresponding Floating IP is 172.30.3.36
                    
    kubectl -n onap get svc  |grep portal-app  
                    
    portal-app                 LoadBalancer   10.43.181.163   10.0.0.13     8989:30215/TCP,8403:30213/TCP,8010:30214/TCP,8443:30225/TCP
                    
* Pod expansion and shrinkage

  pod expansion::

    kubectl scale deployment nginx --replicas=3

  pod shrinkage::

    kubectl scale deployment nginx --replicas=1
