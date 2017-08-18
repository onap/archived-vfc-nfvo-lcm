--
-- Copyright  2017 ZTE Corporation.
--
-- Licensed under the Apache License, Version 2.0 (the "License");
-- you may not use this file except in compliance with the License.
-- You may obtain a copy of the License at
--
--     http://www.apache.org/licenses/LICENSE-2.0
--
-- Unless required by applicable law or agreed to in writing, software
-- distributed under the License is distributed on an "AS IS" BASIS,
-- WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
-- See the License for the specific language governing permissions and
-- limitations under the License.
--

use vfcnfvolcm;

DROP TABLE IF EXISTS NFVO_CPINST;
CREATE TABLE NFVO_CPINST ( 
  `CPINSTANCEID` varchar(255) NOT NULL PRIMARY KEY, 
  `CPDID` varchar(255) NOT NULL, 
  `CPINSTANCENAME` varchar(255) NOT NULL, 
  `OWNERTYPE` integer NOT NULL, 
  `OWNERID` varchar(255) NOT NULL, 
  `RELATEDTYPE` integer NOT NULL, 
  `RELATEDVL` varchar(255) NULL, 
  `RELATEDCP` varchar(255) NULL, 
  `RELATEDPORT` varchar(255) NULL, 
  `STATUS` varchar(255) NOT NULL 
);

DROP TABLE IF EXISTS NFVO_FPINST;
CREATE TABLE NFVO_FPINST ( 
  `FPID` varchar(255) NOT NULL, 
  `FPINSTID` varchar(255) NOT NULL PRIMARY KEY, 
  `FPNAME` varchar(255) NOT NULL, 
  `NSINSTID` varchar(255) NOT NULL, 
  `VNFFGINSTID` varchar(255) NOT NULL, 
  `SYMMETRIC` integer NULL, 
  `POLICYINFO` longtext NOT NULL, 
  `FORWORDERPATHS` varchar(255) NULL, 
  `STATUS` varchar(255) NOT NULL, 
  `SDNCONTROLLERID` varchar(255) NOT NULL, 
  `SFCID` varchar(255) NOT NULL, 
  `FLOWCLASSIFIERS` varchar(255) NOT NULL, 
  `PORTPAIRGROUPS` longtext NOT NULL
);

DROP TABLE IF EXISTS NFVO_JOB;
CREATE TABLE NFVO_JOB ( 
  `JOBID` varchar(255) NOT NULL PRIMARY KEY, 
  `JOBTYPE` varchar (255) NOT NULL, 
  `JOBACTION` varchar(255) NOT NULL, 
  `RESID` varchar(255) NOT NULL, 
  `STATUS` integer NULL, 
  `STARTTIME` varchar(255) NULL, 
  `ENDTIME` varchar(255) NULL, 
  `PROGRESS` integer NULL, 
  `USER` varchar(255) NULL, 
  `PARENTJOBID` varchar(255) NULL, 
  `RESNAME` varchar(255) NULL
);

DROP TABLE IF EXISTS NFVO_JOB_STATUS;
CREATE TABLE NFVO_JOB_STATUS (
  `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, 
  `INDEXID` integer NOT NULL, 
  `JOBID` varchar(255) NOT NULL, 
  `STATUS` varchar(255) NOT NULL, 
  `PROGRESS` integer NULL, 
  `DESCP` longtext NOT NULL, 
  `ERRCODE` varchar(255) NULL, 
  `ADDTIME` varchar(255) NULL
);

DROP TABLE IF EXISTS NFVO_NFINST;
CREATE TABLE NFVO_NFINST (
  `NFINSTID` varchar(200) NOT NULL PRIMARY KEY, 
  `M_NFINSTID` varchar(200) NULL, 
  `NFNAME` varchar(100) NULL, 
  `TEMPLATEID` varchar(200) NULL, 
  `VNFID` varchar(200) NULL, 
  `PACKAGEID` varchar(200) NULL, 
  `VNFMINSTID` varchar(200) NULL, 
  `NSINSTID` varchar(200) NULL, 
  `STATUS` varchar(20) NULL, 
  `FLAVOURID` varchar(200) NULL, 
  `VNFLEVEL` varchar(200) NULL, 
  `LOCATION` varchar(200) NULL, 
  `MAXVM` integer NULL, 
  `MAXCPU` integer NULL, 
  `MAXRAM` integer NULL, 
  `MAXHD` integer NULL, 
  `MAXSHD` integer NULL, 
  `MAXNET` integer NULL, 
  `VERSION` varchar(255) NULL, 
  `VENDOR` varchar(255) NULL, 
  `VNFDMODEL` longtext NULL, 
  `INPUTPARAMS` longtext NULL, 
  `SCALEPARAMS` longtext NULL, 
  `CREATETIME` varchar(200) NULL, 
  `LASTUPTIME` varchar(200) NULL, 
  `EXTENSION` longtext NULL
);

DROP TABLE IF EXISTS NFVO_NFPACKAGE;
CREATE TABLE NFVO_NFPACKAGE (
  `UUID` varchar(255) NOT NULL PRIMARY KEY, 
  `NFPACKAGEID` varchar(200) NOT NULL, 
  `VNFDID` varchar(255) NOT NULL, 
  `VENDOR` varchar(255) NOT NULL, 
  `VNFDVERSION` varchar(255) NOT NULL, 
  `VNFVERSION` varchar(255) NOT NULL, 
  `VNFDMODEL` longtext NULL,
  `VNFDPATH` varchar(300) NULL
);

DROP TABLE IF EXISTS NFVO_NSPACKAGE;
CREATE TABLE NFVO_NSPACKAGE (
  `ID` varchar(200) NOT NULL PRIMARY KEY, 
  `NSDID` varchar(200) NOT NULL, 
  `NAME` varchar(200) NOT NULL, 
  `VENDOR` varchar(200) NULL, 
  `DESCRIPTION` varchar(200) NULL, 
  `VERSION` varchar(200) NULL, 
  `NSDMODEL` longtext NULL,
  `NSDPATH` varchar(300) NULL
);

DROP TABLE IF EXISTS NFVO_NSINST;
CREATE TABLE NFVO_NSINST (
  `ID` varchar(200) NOT NULL PRIMARY KEY, 
  `NAME` varchar(200) NOT NULL, 
  `NSPACKAGEID` varchar(200) NULL, 
  `NSDID` varchar(200) NOT NULL, 
  `DESCRIPTION` varchar(255) NULL, 
  `SDNCONTROLLERID` varchar(200) NULL, 
  `FLAVOURID` varchar(200) NULL, 
  `NSLEVEL` varchar(200) NULL, 
  `STATUS` varchar(200) NULL, 
  `NSDMODEL` longtext NULL, 
  `INPUTPARAMS` longtext NULL, 
  `SCALEPARAMS` longtext NULL,
  `CREATETIME` varchar(200) NULL, 
  `LASTUPTIME` varchar(200) NULL 
);

DROP TABLE IF EXISTS NFVO_PORTINST;
CREATE TABLE NFVO_PORTINST (
  `PORTID` varchar(255) NOT NULL PRIMARY KEY, 
  `NETWORKID` varchar(255) NOT NULL, 
  `SUBNETWORKID` varchar(255) NOT NULL, 
  `VIMID` varchar(255) NOT NULL, 
  `RESOURCEID` varchar(255) NOT NULL, 
  `NAME` varchar(255) NOT NULL, 
  `INSTID` varchar(255) NOT NULL, 
  `CPINSTANCEID` varchar(255) NOT NULL, 
  `BANDWIDTH` varchar(255) NOT NULL, 
  `OPERATIONALSTATE` varchar(255) NOT NULL,
  `IPADDRESS` varchar(255) NOT NULL,
  `MACADDRESS` varchar(255) NOT NULL,
  `FLOATIPADDRESS` varchar(255) NOT NULL,
  `SERVICEIPADDRESS` varchar(255) NOT NULL,
  `TYPEVIRTUALNIC` varchar(255) NOT NULL,
  `SFCENCAPSULATION` varchar(255) NOT NULL,
  `DIRECTION` varchar (255) NOT NULL,
  `TENANT` varchar(255) NOT NULL
); 

DROP TABLE IF EXISTS NFVO_VLINST;
CREATE TABLE NFVO_VLINST (
  `VLINSTANCEID` varchar(255) NOT NULL PRIMARY KEY,
  `VLDID` varchar(255) NOT NULL,
  `VLINSTANCENAME` varchar(255) NULL,
  `OWNERTYPE` integer NOT NULL,
  `OWNERID` varchar(255) NOT NULL,
  `RELATEDNETWORKID` varchar(255) NULL,
  `RELATEDSUBNETWORKID` varchar(255) NULL,
  `VLTYPE` integer NOT NULL,
  `VIMID` varchar(255) NOT NULL,
  `TENANT` varchar(255) NOT NULL,
  `STATUS` varchar(255) NOT NULL
); 

DROP TABLE IF EXISTS NFVO_VMINST;
CREATE TABLE NFVO_VMINST (
  `VMID` varchar(255) NOT NULL PRIMARY KEY,
  `VIMID` varchar (255) NOT NULL,
  `RESOURCEID` varchar(255) NOT NULL,
  `INSTTYPE` integer NULL,
  `INSTID` varchar(255) NULL,
  `VMNAME` varchar(255) NOT NULL,
  `OPERATIONALSTATE` integer NOT NULL,
  `ZONEID` varchar(255) NULL,
  `TENANT` varchar(255) NULL,
  `HOSTID` varchar(255) NOT NULL,
  `DETAILINFO` varchar(255) NULL
); 

DROP TABLE IF EXISTS NFVO_VNFCINST;
CREATE TABLE NFVO_VNFCINST (
  `VNFCINSTANCEID` varchar(255) NOT NULL PRIMARY KEY,
  `VDUID` varchar(255) NOT NULL,
  `NFINSTID` varchar(255) NOT NULL,
  `VMID` varchar(255) NOT NULL,
  `STATUS` varchar(255) NOT NULL
); 

DROP TABLE IF EXISTS NFVO_VNFFGINST;
CREATE TABLE NFVO_VNFFGINST (
  `VNFFGDID` varchar(255) NOT NULL,
  `VNFFGINSTID` varchar(255) NOT NULL PRIMARY KEY,
  `NSINSTID` varchar(255) NOT NULL,
  `DESC` varchar(255) NULL,
  `VENDOR` varchar(255) NULL,
  `VERSION` varchar(255) NULL,
  `ENDPOINTNUMBER` integer NOT NULL,
  `VLLIST` varchar(1024) NOT NULL,
  `CPLIST` varchar(1024) NOT NULL,
  `VNFLIST` varchar(1024) NOT NULL,
  `FPLIST` varchar(1024) NOT NULL,
  `STATUS` varchar(255) NOT NULL
); 

DROP TABLE IF EXISTS NFVO_NFPACKAGEFILE;
CREATE TABLE NFVO_NFPACKAGEFILE (
  `ID` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `NFPACKAGEID` varchar(50) NOT NULL,
  `FILENAME` varchar(100) NOT NULL,
  `FILETYPE` varchar(2) NOT NULL,
  `IMAGEID` varchar(50) NOT NULL,
  `VIMID` varchar(50) NOT NULL,
  `VIMUSER` varchar(50) NOT NULL,
  `TENANT` varchar(50) NOT NULL,
  `PURPOSE` varchar(1000) NOT NULL,
  `STATUS` varchar(10) NOT NULL 
);
 
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS t_lcm_servicebaseinfo; 
SET FOREIGN_KEY_CHECKS = 1;
CREATE TABLE t_lcm_servicebaseinfo ( 
    serviceId         VARCHAR(255)      NOT NULL, 
    serviceName       VARCHAR(255)      NOT NULL,
    serviceType       VARCHAR(20)       NOT NULL,
    description       VARCHAR(255)      NULL, 
    activeStatus      VARCHAR(20)       NOT NULL, 
    status            VARCHAR(20)       NOT NULL, 
    creator           VARCHAR(50)       NOT NULL,
    createTime       BIGINT            NOT NULL,
    CONSTRAINT t_lcm_servicebaseinfo PRIMARY KEY(serviceId)
); 
DROP TABLE IF EXISTS t_lcm_defPackage_mapping; 
CREATE TABLE t_lcm_defPackage_mapping ( 
    serviceId         VARCHAR(255)      NOT NULL, 
    serviceDefId      VARCHAR(255)      NOT NULL, 
    templateId        VARCHAR(255)      NOT NULL, 
    templateName      VARCHAR(255)       NOT NULL,
	CONSTRAINT t_lcm_defPackage_mapping PRIMARY KEY(serviceId),
	CONSTRAINT t_lcm_defPackage_mapping FOREIGN KEY (serviceId) REFERENCES t_lcm_servicebaseinfo (serviceId)
); 
DROP TABLE IF EXISTS t_lcm_inputParam_mapping; 
CREATE TABLE t_lcm_inputParam_mapping ( 
    serviceId         VARCHAR(255)      NOT NULL, 
    inputKey          VARCHAR(255)      NOT NULL, 
    inputValue        mediumtext      NULL,
	CONSTRAINT t_lcm_inputParam_mapping PRIMARY KEY(serviceId,inputKey),
	CONSTRAINT t_lcm_inputParam_mapping FOREIGN KEY (serviceId) REFERENCES t_lcm_servicebaseinfo (serviceId)
); 
