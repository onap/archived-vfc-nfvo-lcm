# Copyright 2016 ZTE Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from django.db import models


class NSDModel(models.Model):
    class Meta:
        db_table = 'NFVO_NSPACKAGE'

    id = models.CharField(db_column='ID', primary_key=True, max_length=200)
    nsd_id = models.CharField(db_column='NSDID', max_length=200)
    name = models.CharField(db_column='NAME', max_length=200)
    vendor = models.CharField(db_column='VENDOR', max_length=200, null=True, blank=True)
    description = models.CharField(db_column='DESCRIPTION', max_length=200, null=True, blank=True)
    version = models.CharField(db_column='VERSION', max_length=200, null=True, blank=True)
    nsd_model = models.TextField(db_column='NSDMODEL', max_length=65535, null=True, blank=True)


class NSInstModel(models.Model):
    class Meta:
        db_table = 'NFVO_NSINST'

    id = models.CharField(db_column='ID', primary_key=True, max_length=200)
    name = models.CharField(db_column='NAME', max_length=200)
    nspackage_id = models.CharField(db_column='NSPACKAGEID', max_length=200, null=True, blank=True)
    nsd_id = models.CharField(db_column='NSDID', max_length=200)
    description = models.CharField(db_column='DESCRIPTION', max_length=255, null=True, blank=True)
    sdncontroller_id = models.CharField(db_column='SDNCONTROLLERID', max_length=200, null=True, blank=True)
    flavour_id = models.CharField(db_column='FLAVOURID', max_length=200, null=True, blank=True)
    ns_level = models.CharField(db_column='NSLEVEL', max_length=200, null=True, blank=True)
    status = models.CharField(db_column='STATUS', max_length=200, null=True, blank=True)
    nsd_model = models.TextField(db_column='NSDMODEL', max_length=20000, null=True, blank=True)
    input_params = models.TextField(db_column='INPUTPARAMS', max_length=2000, null=True, blank=True)
    scale_params = models.TextField(db_column='SCALEPARAMS', max_length=2000, null=True, blank=True)
    create_time = models.CharField(db_column='CREATETIME', max_length=200, null=True, blank=True)
    lastuptime = models.CharField(db_column='LASTUPTIME', max_length=200, null=True, blank=True)


class NfPackageModel(models.Model):
    uuid = models.CharField(db_column='UUID', primary_key=True, max_length=255)
    nfpackageid = models.CharField(db_column='NFPACKAGEID', max_length=200)
    vnfdid = models.CharField(db_column='VNFDID', max_length=255)
    vendor = models.CharField(db_column='VENDOR', max_length=255)
    vnfdversion = models.CharField(db_column='VNFDVERSION', max_length=255)
    vnfversion = models.CharField(db_column='VNFVERSION', max_length=255)
    vnfdmodel = models.TextField(db_column='VNFDMODEL', max_length=65535, blank=True, null=True)

    class Meta:
        db_table = 'NFVO_NFPACKAGE'


class VnfPackageFileModel(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    vnfpid = models.CharField(db_column='NFPACKAGEID', max_length=50)
    filename = models.CharField(db_column='FILENAME', max_length=100)
    filetype = models.CharField(db_column='FILETYPE', max_length=2)
    imageid = models.CharField(db_column='IMAGEID', max_length=50)
    vimid = models.CharField(db_column='VIMID', max_length=50)
    vimuser = models.CharField(db_column='VIMUSER', max_length=50)
    tenant = models.CharField(db_column='TENANT', max_length=50)
    purpose = models.CharField(db_column='PURPOSE', max_length=1000)
    status = models.CharField(db_column='STATUS', max_length=10)

    class Meta:
        db_table = 'NFVO_NFPACKAGEFILE'


class FPInstModel(models.Model):
    class Meta:
        db_table = 'NFVO_FPINST'

    fpid = models.CharField(db_column='FPID', max_length=255)
    fpinstid = models.CharField(db_column='FPINSTID', max_length=255, primary_key=True)
    fpname = models.CharField(db_column='FPNAME', max_length=255)
    nsinstid = models.CharField(db_column='NSINSTID', max_length=255)
    vnffginstid = models.CharField(db_column='VNFFGINSTID', max_length=255)
    symmetric = models.IntegerField(db_column='SYMMETRIC', null=True)
    policyinfo = models.TextField(db_column='POLICYINFO', max_length=65535)
    forworderpaths = models.CharField(db_column='FORWORDERPATHS', max_length=255, null=True, blank=True)
    status = models.CharField(db_column='STATUS', max_length=255)
    sdncontrollerid = models.CharField(db_column='SDNCONTROLLERID', max_length=255)
    sfcid = models.CharField(db_column='SFCID', max_length=255)
    flowclassifiers = models.CharField(db_column='FLOWCLASSIFIERS', max_length=255)
    portpairgroups = models.TextField(db_column='PORTPAIRGROUPS', max_length=65535)


class VNFFGInstModel(models.Model):
    class Meta:
        db_table = 'NFVO_VNFFGINST'

    vnffgdid = models.CharField(db_column='VNFFGDID', max_length=255)
    vnffginstid = models.CharField(db_column='VNFFGINSTID', max_length=255, primary_key=True)
    nsinstid = models.CharField(db_column='NSINSTID', max_length=255)
    desc = models.CharField(db_column='DESC', max_length=255, blank=True, null=True)
    vendor = models.CharField(db_column='VENDOR', max_length=255, blank=True, null=True)
    version = models.CharField(db_column='VERSION', max_length=255, blank=True, null=True)
    endpointnumber = models.IntegerField(db_column='ENDPOINTNUMBER')
    vllist = models.CharField(db_column='VLLIST', max_length=1024)
    cplist = models.CharField(db_column='CPLIST', max_length=1024)
    vnflist = models.CharField(db_column='VNFLIST', max_length=1024)
    fplist = models.CharField(db_column='FPLIST', max_length=1024)
    status = models.CharField(db_column='STATUS', max_length=255)


class NfInstModel(models.Model):
    class Meta:
        db_table = 'NFVO_NFINST'

    nfinstid = models.CharField(db_column='NFINSTID', max_length=200, primary_key=True)
    mnfinstid = models.CharField(db_column='M_NFINSTID', max_length=200, blank=True, null=True)
    nf_name = models.CharField(db_column='NFNAME', max_length=100, blank=True, null=True)
    template_id = models.CharField(db_column='TEMPLATEID', max_length=200, blank=True, null=True)
    vnf_id = models.CharField(db_column='VNFID', max_length=200, blank=True, null=True)
    package_id = models.CharField(db_column='PACKAGEID', max_length=200, blank=True, null=True)
    vnfm_inst_id = models.CharField(db_column='VNFMINSTID', max_length=200, blank=True, null=True)
    ns_inst_id = models.CharField(db_column='NSINSTID', max_length=200, blank=True, null=True)
    status = models.CharField(db_column='STATUS', max_length=20, blank=True, null=True)
    flavour_id = models.CharField(db_column='FLAVOURID', max_length=200, blank=True, null=True)
    vnf_level = models.CharField(db_column='VNFLEVEL', max_length=200, blank=True, null=True)
    location = models.CharField(db_column='LOCATION', max_length=200, blank=True, null=True)
    max_vm = models.IntegerField(db_column='MAXVM', null=True)
    max_cpu = models.IntegerField(db_column='MAXCPU', null=True)
    max_ram = models.IntegerField(db_column='MAXRAM', null=True)
    max_hd = models.IntegerField(db_column='MAXHD', null=True)
    max_shd = models.IntegerField(db_column='MAXSHD', null=True)
    max_net = models.IntegerField(db_column='MAXNET', null=True)
    version = models.CharField(db_column='VERSION', max_length=255, null=True)
    vendor = models.CharField(db_column='VENDOR', max_length=255, null=True, blank=True)
    vnfd_model = models.TextField(db_column='VNFDMODEL', max_length=20000, blank=True, null=True)
    input_params = models.TextField(db_column='INPUTPARAMS', max_length=2000, blank=True, null=True)
    scale_params = models.TextField(db_column='SCALEPARAMS', max_length=2000, null=True, blank=True)
    create_time = models.CharField(db_column='CREATETIME', max_length=200, null=True, blank=True)
    lastuptime = models.CharField(db_column='LASTUPTIME', max_length=200, blank=True, null=True)
    extension = models.TextField(db_column='EXTENSION', max_length=65535, blank=True, null=True)


class VmInstModel(models.Model):
    class Meta:
        db_table = 'NFVO_VMINST'

    vmid = models.CharField(db_column='VMID', primary_key=True, max_length=255)
    vimid = models.CharField(db_column='VIMID', max_length=255)
    resouceid = models.CharField(db_column='RESOURCEID', max_length=255)
    insttype = models.IntegerField(db_column='INSTTYPE', null=True)
    instid = models.CharField(db_column='INSTID', max_length=255, null=True)
    vmname = models.CharField(db_column='VMNAME', max_length=255)
    operationalstate = models.IntegerField(db_column='OPERATIONALSTATE', default=1)
    zoneid = models.CharField(db_column='ZONEID', max_length=255, null=True)
    tenant = models.CharField(db_column='TENANT', max_length=255, null=True)
    hostid = models.CharField(db_column='HOSTID', max_length=255)
    detailinfo = models.CharField(db_column='DETAILINFO', max_length=255, null=True)


class VNFCInstModel(models.Model):
    class Meta:
        db_table = 'NFVO_VNFCINST'

    vnfcinstanceid = models.CharField(db_column='VNFCINSTANCEID', max_length=255, primary_key=True)
    vduid = models.CharField(db_column='VDUID', max_length=255)
    nfinstid = models.CharField(db_column='NFINSTID', max_length=255)
    vmid = models.CharField(db_column='VMID', max_length=255)
    status = models.CharField(db_column='STATUS', max_length=255)


class CPInstModel(models.Model):
    class Meta:
        db_table = 'NFVO_CPINST'

    cpinstanceid = models.CharField(db_column='CPINSTANCEID', max_length=255, primary_key=True)
    cpdid = models.CharField(db_column='CPDID', max_length=255)
    cpinstancename = models.CharField(db_column='CPINSTANCENAME', max_length=255)
    ownertype = models.IntegerField(db_column='OWNERTYPE')
    ownerid = models.CharField(db_column='OWNERID', max_length=255)
    relatedtype = models.IntegerField(db_column='RELATEDTYPE')
    relatedvl = models.CharField(db_column='RELATEDVL', max_length=255, blank=True, null=True)
    relatedcp = models.CharField(db_column='RELATEDCP', max_length=255, blank=True, null=True)
    relatedport = models.CharField(db_column='RELATEDPORT', max_length=255, blank=True, null=True)
    status = models.CharField(db_column='STATUS', max_length=255)


class VLInstModel(models.Model):
    class Meta:
        db_table = 'NFVO_VLINST'

    vlinstanceid = models.CharField(db_column='VLINSTANCEID', max_length=255, primary_key=True)
    vldid = models.CharField(db_column='VLDID', max_length=255)
    vlinstancename = models.CharField(db_column='VLINSTANCENAME', max_length=255, blank=True, null=True)
    ownertype = models.IntegerField(db_column='OWNERTYPE')
    ownerid = models.CharField(db_column='OWNERID', max_length=255)
    relatednetworkid = models.CharField(db_column='RELATEDNETWORKID', max_length=255, blank=True, null=True)
    relatedsubnetworkid = models.CharField(db_column='RELATEDSUBNETWORKID', max_length=255, blank=True, null=True)
    vltype = models.IntegerField(db_column='VLTYPE', default=0)
    vimid = models.CharField(db_column='VIMID', max_length=255)
    tenant = models.CharField(db_column='TENANT', max_length=255)
    status = models.CharField(db_column='STATUS', max_length=255)


class PortInstModel(models.Model):
    class Meta:
        db_table = 'NFVO_PORTINST'

    portid = models.CharField(db_column='PORTID', max_length=255, primary_key=True)
    networkid = models.CharField(db_column='NETWORKID', max_length=255)
    subnetworkid = models.CharField(db_column='SUBNETWORKID', max_length=255)
    vimid = models.CharField(db_column='VIMID', max_length=255)
    resourceid = models.CharField(db_column='RESOURCEID', max_length=255)
    name = models.CharField(db_column='NAME', max_length=255)
    instid = models.CharField(db_column='INSTID', max_length=255)
    cpinstanceid = models.CharField(db_column='CPINSTANCEID', max_length=255)
    bandwidth = models.CharField(db_column='BANDWIDTH', max_length=255)
    operationalstate = models.CharField(db_column='OPERATIONALSTATE', max_length=255)
    ipaddress = models.CharField(db_column='IPADDRESS', max_length=255)
    macaddress = models.CharField(db_column='MACADDRESS', max_length=255)
    floatipaddress = models.CharField(db_column='FLOATIPADDRESS', max_length=255)
    serviceipaddress = models.CharField(db_column='SERVICEIPADDRESS', max_length=255)
    typevirtualnic = models.CharField(db_column='TYPEVIRTUALNIC', max_length=255)
    sfcencapsulation = models.CharField(db_column='SFCENCAPSULATION', max_length=255)
    direction = models.CharField(db_column='DIRECTION', max_length=255)
    tenant = models.CharField(db_column='TENANT', max_length=255)


class JobModel(models.Model):
    class Meta:
        db_table = 'NFVO_JOB'

    jobid = models.CharField(db_column='JOBID', primary_key=True, max_length=255)
    jobtype = models.CharField(db_column='JOBTYPE', max_length=255)
    jobaction = models.CharField(db_column='JOBACTION', max_length=255)
    resid = models.CharField(db_column='RESID', max_length=255)
    status = models.IntegerField(db_column='STATUS', null=True, blank=True)
    starttime = models.CharField(db_column='STARTTIME', max_length=255, null=True, blank=True)
    endtime = models.CharField(db_column='ENDTIME', max_length=255, null=True, blank=True)
    progress = models.IntegerField(db_column='PROGRESS', null=True, blank=True)
    user = models.CharField(db_column='USER', max_length=255, null=True, blank=True)
    parentjobid = models.CharField(db_column='PARENTJOBID', max_length=255, null=True, blank=True)
    resname = models.CharField(db_column='RESNAME', max_length=255, null=True, blank=True)

    def toJSON(self):
        import json
        return json.dumps(dict([(attr, getattr(self, attr)) for attr in [f.name for f in self._meta.fields]]))


class JobStatusModel(models.Model):
    class Meta:
        db_table = 'NFVO_JOB_STATUS'

    indexid = models.IntegerField(db_column='INDEXID')
    jobid = models.CharField(db_column='JOBID', max_length=255)
    status = models.CharField(db_column='STATUS', max_length=255)
    progress = models.IntegerField(db_column='PROGRESS', null=True, blank=True)
    descp = models.TextField(db_column='DESCP', max_length=65535)
    errcode = models.CharField(db_column='ERRCODE', max_length=255, null=True, blank=True)
    addtime = models.CharField(db_column='ADDTIME', max_length=255, null=True, blank=True)

    def toJSON(self):
        import json
        return json.dumps(dict([(attr, getattr(self, attr)) for attr in [f.name for f in self._meta.fields]]))


class DefPkgMappingModel(models.Model):
    class Meta:
        db_table = 't_lcm_defPackage_mapping'

    service_id = models.CharField(db_column='serviceId', max_length=255, primary_key=True)
    service_def_id = models.CharField(db_column='serviceDefId', max_length=255)
    template_id = models.CharField(db_column='templateId', max_length=255)
    template_name = models.CharField(db_column='templateName', max_length=255)


class InputParamMappingModel(models.Model):
    class Meta:
        db_table = 't_lcm_inputParam_mapping'

    service_id = models.CharField(db_column='serviceId', max_length=255)
    input_key = models.CharField(db_column='inputKey', max_length=255)
    input_value = models.CharField(db_column='inputValue', max_length=255, null=True, blank=True)


class ServiceBaseInfoModel(models.Model):
    class Meta:
        db_table = 't_lcm_servicebaseinfo'

    service_id = models.CharField(db_column='serviceId', max_length=255, primary_key=True)
    service_name = models.CharField(db_column='serviceName', max_length=255)
    service_type = models.CharField(db_column='serviceType', max_length=20)
    description = models.CharField(db_column='description', max_length=255, null=True, blank=True)
    active_status = models.CharField(db_column='activeStatus', max_length=20)
    status = models.CharField(db_column='status', max_length=20)
    creator = models.CharField(db_column='creator', max_length=50)
    create_time = models.BigIntegerField(db_column='createTime', max_length=20)
    
 