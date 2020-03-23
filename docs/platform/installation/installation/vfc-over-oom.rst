.. contents::
   :depth: 3
..

   **VFC Installation over OOM**
   **V0.1**

**1 Scope**
=============

This is a guide to help developer or tester to try to install VF-C over OOM

**2 Component & function**
==========================

Now VF-C have the following repos in https://gerrit.onap.org/r/#/admin/projects/?filter=vfc

+--------------------------+-----------------------------------------------------+
|     **Repo Name**        |     Description                                     |
+==========================+=====================================================+
|     vfc/nfvo/lcm         |      NS life cycle management                       |
+--------------------------+-----------------------------------------------------+
| vfc/nfvo/resmanagement   |      NS Resource Management                         |
+--------------------------+-----------------------------------------------------+
|vfc/nfvo/driver/vnfm/svnfm|     Specific VNFM drivers                           |
+--------------------------+-----------------------------------------------------+
|vfc/nfvo/driver/vnfm/gvnfm|     Generic VNFM drivers                            |
+--------------------------+-----------------------------------------------------+
|vfc/nfvo/driver/sfc       |     SFC Driver                                      |
+--------------------------+-----------------------------------------------------+
|org.onap.vfc.nfvo.wfengine|     Work flow engine                                |
+--------------------------+-----------------------------------------------------+
|EMS-driver                |     VNF fcaps collect                               |
+--------------------------+-----------------------------------------------------+
|vfc/gvnfm/vnflcm          |     Generic VNFM VNF LCM                            |
+--------------------------+-----------------------------------------------------+
|vfc/gvnfm/vnfmgr          |     Generic VNFM VNF Mgr                            |
+--------------------------+-----------------------------------------------------+
|vfc/gvnfm/vnfres          |     Generic VNFM VNF Resource Management            |
+--------------------------+-----------------------------------------------------+
|vfc/nfvo/multivimproxy    | Multi-vim proxy, provide the multivim indirect mode |
|                          | proxy which can forward virtual resource requests to|
|						   | multivim and do some resource checking              |
+--------------------------+-----------------------------------------------------+
|vfc/nfvo/db               | Stand-alone database microservice, provides the     |
|                          |   database services for each VF-C component         |
+--------------------------+-----------------------------------------------------+

Note:
  a. vfc/nfvo/driver/sfc it migrate from Open-O seed code and now haven't been used in any usecase in ONAP. 
  b. vfc/nfvo/resmanagement is used to do the resource granting, but now VF-C has been integrated with OOF, this component will be deprecated in the future release.
  c. vfc/nfvo/db provide the stand-alone database microservice in casablanca release, but now VF-C leverages OOM shared MariaDB-Gelera cluster. This repo still has redis to be used by VF-C component.


VF-C Docker Images

::

  docker run -d -p 3306:3306 -p 6379:6379 --name vfc-db -v /var/lib/mysql nexus3.onap.org:10001/onap/vfc/db
  we use  ${VFC_DB_IP} as the IP of vfc-db component.
  nexus3.onap.org:10001/onap/vfc/db:1.3.0
  nexus3.onap.org:10001/onap/vfc/emsdriver:1.3.0
  nexus3.onap.org:10001/onap/vfc/gvnfmdriver:1.3.0
  nexus3.onap.org:10001/onap/vfc/jujudriver:1.3.0
  nexus3.onap.org:10001/onap/vfc/multivimproxy:1.3.0
  nexus3.onap.org:10001/onap/vfc/nfvo/svnfm/huawei:1.3.0
  nexus3.onap.org:10001/onap/vfc/nfvo/svnfm/nokia:1.3.0
  nexus3.onap.org:10001/onap/vfc/nfvo/svnfm/nokiav2:1.3.0
  nexus3.onap.org:10001/onap/vfc/nslcm:1.3.0
  nexus3.onap.org:10001/onap/vfc/resmanagement:1.3.0
  nexus3.onap.org:10001/onap/vfc/vnflcm:1.3.0
  nexus3.onap.org:10001/onap/vfc/vnfmgr:1.3.0
  nexus3.onap.org:10001/onap/vfc/vnfres:1.3.0
  nexus3.onap.org:10001/onap/vfc/wfengine-activiti:1.3.0
  nexus3.onap.org:10001/onap/vfc/wfengine-mgrservice:1.3.0
  nexus3.onap.org:10001/onap/vfc/ztesdncdriver:1.3.0
  nexus3.onap.org:10001/onap/vfc/ztevnfmdriver:1.3.0
  

**3 VF-C Deployment**
=====================

For initialization of docker there are 2 deployment options currently adpoted in ONAP:
- using heat template
- using OOM

From Casablanca release, OOM is the recommended way, so here mainly give the steps for OOM based deployment

For OOM deployment you can refer to the below links:

https://onap.readthedocs.io/en/latest/submodules/oom.git/docs/oom_setup_kubernetes_rancher.html
https://onap.readthedocs.io/en/latest/submodules/oom.git/docs/oom_quickstart_guide.html#quick-start-label

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
	# Global configuration defaults.
	#################################################################
	global:
		nodePortPrefix: 302
		readinessRepository: oomk8s
		readinessImage: readiness-check:2.0.0
		loggingRepository: docker.elastic.co
		loggingImage: beats/filebeat:5.5.0

	#################################################################
	# Application configuration defaults.
	#################################################################
	# application image
	flavor: small

	repository: nexus3.onap.org:10001
	image: onap/vfc/nslcm:1.3.7
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

Step3: Delete teh existing pods already deployed

::

	cd oom/kubernetes
	helm del dev-vfc --purge

Step4: Deploy the new pods

::

	cd oom/kubernetes
	helm instal local/vfc --namespace onap --name dev-vfc


Now VF-C will be upgraded with the new image version 

You will see all the pod is runing 
	
::

	cd oom/kubernetes
	dev-vfc-vfc-db-6c57b4fd47-7kbnj                               1/1       Running            2          79d
	dev-vfc-vfc-ems-driver-65bd9bf5b-65gtg                        1/1       Running            48         79d
	dev-vfc-vfc-generic-vnfm-driver-698c8d6698-2ctlg              2/2       Running            4          79d
	dev-vfc-vfc-huawei-vnfm-driver-6d5db69469-277vb               2/2       Running            7          79d
	dev-vfc-vfc-juju-vnfm-driver-68d4556dfd-hncrm                 2/2       Running            4          79d
	dev-vfc-vfc-multivim-proxy-74d8fc568d-gn8gp                   1/1       Running            6          79d
	dev-vfc-vfc-nokia-v2vnfm-driver-759687787f-fdfsg              1/1       Running            2          79d
	dev-vfc-vfc-nokia-vnfm-driver-9cbcb9697-z7hp4                 2/2       Running            6          79d
	dev-vfc-vfc-nslcm-97c97759f-x9r9h                             2/2       Running            9          79d
	dev-vfc-vfc-resmgr-84b9b579c9-b7cbj                           2/2       Running            7          79d
	dev-vfc-vfc-vnflcm-7cbdfcfd9b-bqwz8                           2/2       Running            13         79d
	dev-vfc-vfc-vnfmgr-54bdfb84c4-kwbds                           2/2       Running            6          79d
	dev-vfc-vfc-vnfres-7fdbc88945-t9nhd                           2/2       Running            5          79d
	dev-vfc-vfc-workflow-5b745cf488-7z7nd                         1/1       Running            2          79d
	dev-vfc-vfc-workflow-engine-6d5d8ffc7c-pjpmc                  1/1       Running            2          79d
	dev-vfc-vfc-zte-sdnc-driver-6554df5856-ctjxh                  1/1       Running            7          79d
	dev-vfc-vfc-zte-vnfm-driver-7dbd4f887-thvvg                   2/2       Running            8          79d


**4 VF-C health check**
========================

When VF-C pod is up, if you want to check the service status, you can visit the following APIs in K8S cluster to check.
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

Here are only a few componnets as an example.

Take vnflcm as an example, you can visit the api as follow:

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

When you are doing the testing and would like to replace some new file like binary or some script and want to check the new resut.
Before you replace the file to the running pod,you need to close the pod livenessProbe and readinessProbe first to avoid the pod restart.

Take vfc-nslcm pod as an example:

::

    kubectl -n onap edit deployment dev-vfc-vfc-nslcm

    spec:
      containers:
      - env:
        - name: MSB_ADDR
          value: msb-iag:80
        - name: MYSQL_ADDR
          value: vfc-db:3306
        image: 172.30.1.66:10001/onap/vfc/nslcm:1.3.7
        imagePullPolicy: Always
        #livenessProbe:
          #failureThreshold: 3
          #initialDelaySeconds: 120
          #periodSeconds: 10
          #successThreshold: 1
          #tcpSocket:
            #port: 8806
          #timeoutSeconds: 1
        name: vfc-nslcm
        ports:
        - containerPort: 8806
          protocol: TCP
        #readinessProbe:
          #failureThreshold: 3
          #initialDelaySeconds: 10
          #periodSeconds: 10
          #successThreshold: 1
          #tcpSocket:
            #port: 8806
          #timeoutSeconds: 1
		  

Then you can replace the file into the pod. 


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
                     
    kubectl get pod -o wide
                
    kubectl get pod -n onap
                
* Connected to the docker in pod

::
      
    Check the docker's name , return two dockers' name after execution, -c specifie the docker that needed ti go in.     
            
    kubectl -n onap get pod dev-vfc-nslcm-68cb7c9878-v4kt2 -o jsonpath={.spec.containers[*].name}
                
    kubectl -n onap exec -it dev-vfc-nslcm-68cb7c9878-v4kt2 -c vfc-nslcm /bin/bash
            
* Copy files (take the catlog example). When the data copy is lost after the pod is restarted or migrated, the multi-copy pod copy operation only exists for the current pod

::
    
    Copy from local to dockers in pod

    kubectl -n onap cp copy_test.sh  dev-vfc-nslcm-68cb7c9878-v4kt2: -c vfc-nslcm
                
    Copy pod's content to local��
                
    kubectl -n onap cp dev-vfc-nslcm-68cb7c9878-v4kt2:copy_test.sh -c vfc-nslcm /tmp/copy_test.sh
                
* Remote command (to see the current path of the container as an example)

::
    
    kubectl -n onap exec -it dev-vfc-nslcm-68cb7c9878-v4kt2 -c vfc-nslcm pwd
                
* View pod basic information and logs (no -c parameter added for single container pod)

::
                
    kubectl  -n onap describe  pod dev-vfc-nslcm-68cb7c9878-v4kt2
                  
    kubectl -n onap logs dev-vfc-nslcm-68cb7c9878-v4kt2 -c vfc-nslcm
  
* Check the service listener port and manually expose the port, which is commonly used for testing, such as nginx under test namespace

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
                    
* pod expansion and shrinkage

::
    
    pod expansion��kubectl  scale deployment nginx --replicas 3

    pod shrinkage�� kubectl  scale deployment nginx --replicas 1
    
    