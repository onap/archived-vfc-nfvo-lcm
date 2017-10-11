Nokia VNFM Driver Installation guide
====================================
    1. Download .zip installer package

    2. Unzip this installer to the installation directory (ex: /opt/openo/nfvo/)

    3. Refer the README.txt from the installation directory, to install and configure this     service. Please refer the same README document below for easy reference:

Introduction:
=============
     This document provides the required steps for installation
     and configuration this service.

Installation steps:
====================
    Install following software:
        - Java 1.8 or lattest
        - MySql Server 5.7 or lattest.
        - Apache Tomcat Server 8.0 or lattest

    Set the following environment variables:
        - JAVA_HOME: Set to JAVA JDK installed location
        - CATALINIA_HOME: Set to Tomcat installed location
        - CATALINIA_BASE: Set to the location, where this
          service installer is unzipped, its optional
        - PATH: Update it with the location of command 'mysql'

    - In command console, cd to 'bin' directory under the location,
      where this service installer is unzipped and
      run ./init_db.sh <db user> <db password> <db server ip> <db port>
      CAUTION: Existing vnfm_db will be cleaned before
      initializing the schema, so please take a back-up of it
      before executing it next time.

Configuration steps:
====================
    - Update the db credentials in 'application.properties' under webapps directory.
    - Update the VNFM address in 'application.properties' under webapps directory.
    - Update the service name and version of MSB services in 'application.properties' under webapps directory.
    - Update the MSB address in $PATH/etc/conf/restclient.json
    - Update the service ip address in $PATH/etc/adapterInfo/jujuadapterinfo.json



How to run?
===========
    - In command console, cd to 'bin' directory under the location,
      where this service installer is unzipped and
      run ./startup.sh

      *NOTE*: It starts the tomcat at predefined http port. To change
      default port, update the port in tomcat configuration file
      'conf/server.xml'
      - Verify that 'Tomcat started.' is reported on the console.
    - Once service is started, please verify below details:
        - from MSB service, verify that "nokia-vnfm-driver"  is reported from GET request on "/openoapi/microservices/v1/services"
        - from this service, run one of the supported REST API mentioned in open-o NFVO wiki and verify that the
          expected response is returned.


How to stop?
=============
    - In command console, cd to 'bin' directory under the location,
      where this service installer is unzipped and
      run ./shutdown.sh