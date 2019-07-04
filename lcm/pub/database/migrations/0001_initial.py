# Copyright 2019 ZTE Corporation.
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

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CPInstModel',
            fields=[
                ('cpinstanceid', models.CharField(db_column='CPINSTANCEID', max_length=255, primary_key=True, serialize=False)),
                ('cpdid', models.CharField(db_column='CPDID', max_length=255)),
                ('cpinstancename', models.CharField(db_column='CPINSTANCENAME', max_length=255)),
                ('ownertype', models.IntegerField(db_column='OWNERTYPE')),
                ('ownerid', models.CharField(db_column='OWNERID', max_length=255)),
                ('relatedtype', models.IntegerField(db_column='RELATEDTYPE')),
                ('relatedvl', models.CharField(blank=True, db_column='RELATEDVL', max_length=255, null=True)),
                ('relatedcp', models.CharField(blank=True, db_column='RELATEDCP', max_length=255, null=True)),
                ('relatedport', models.CharField(blank=True, db_column='RELATEDPORT', max_length=255, null=True)),
                ('status', models.CharField(db_column='STATUS', max_length=255)),
            ],
            options={
                'db_table': 'NFVO_CPINST',
            },
        ),
        migrations.CreateModel(
            name='DefPkgMappingModel',
            fields=[
                ('service_id', models.CharField(db_column='serviceId', max_length=255, primary_key=True, serialize=False)),
                ('service_def_id', models.CharField(db_column='serviceDefId', max_length=255)),
                ('template_id', models.CharField(db_column='templateId', max_length=255)),
                ('template_name', models.CharField(db_column='templateName', max_length=255)),
            ],
            options={
                'db_table': 't_lcm_defPackage_mapping',
            },
        ),
        migrations.CreateModel(
            name='FPInstModel',
            fields=[
                ('fpid', models.CharField(db_column='FPID', max_length=255)),
                ('fpinstid', models.CharField(db_column='FPINSTID', max_length=255, primary_key=True, serialize=False)),
                ('fpname', models.CharField(db_column='FPNAME', max_length=255)),
                ('nsinstid', models.CharField(db_column='NSINSTID', max_length=255)),
                ('vnffginstid', models.CharField(db_column='VNFFGINSTID', max_length=255)),
                ('symmetric', models.IntegerField(db_column='SYMMETRIC', null=True)),
                ('policyinfo', models.TextField(db_column='POLICYINFO', max_length=65535)),
                ('forworderpaths', models.CharField(blank=True, db_column='FORWORDERPATHS', max_length=255, null=True)),
                ('status', models.CharField(db_column='STATUS', max_length=255)),
                ('sdncontrollerid', models.CharField(db_column='SDNCONTROLLERID', max_length=255)),
                ('sfcid', models.CharField(db_column='SFCID', max_length=255)),
                ('flowclassifiers', models.CharField(db_column='FLOWCLASSIFIERS', max_length=255)),
                ('portpairgroups', models.TextField(db_column='PORTPAIRGROUPS', max_length=65535)),
            ],
            options={
                'db_table': 'NFVO_FPINST',
            },
        ),
        migrations.CreateModel(
            name='InputParamMappingModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_id', models.CharField(db_column='serviceId', max_length=255)),
                ('input_key', models.CharField(db_column='inputKey', max_length=255)),
                ('input_value', models.CharField(blank=True, db_column='inputValue', max_length=255, null=True)),
            ],
            options={
                'db_table': 't_lcm_inputParam_mapping',
            },
        ),
        migrations.CreateModel(
            name='JobModel',
            fields=[
                ('jobid', models.CharField(db_column='JOBID', max_length=255, primary_key=True, serialize=False)),
                ('jobtype', models.CharField(db_column='JOBTYPE', max_length=255)),
                ('jobaction', models.CharField(db_column='JOBACTION', max_length=255)),
                ('resid', models.CharField(db_column='RESID', max_length=255)),
                ('status', models.IntegerField(blank=True, db_column='STATUS', null=True)),
                ('starttime', models.CharField(blank=True, db_column='STARTTIME', max_length=255, null=True)),
                ('endtime', models.CharField(blank=True, db_column='ENDTIME', max_length=255, null=True)),
                ('progress', models.IntegerField(blank=True, db_column='PROGRESS', null=True)),
                ('user', models.CharField(blank=True, db_column='USER', max_length=255, null=True)),
                ('parentjobid', models.CharField(blank=True, db_column='PARENTJOBID', max_length=255, null=True)),
                ('resname', models.CharField(blank=True, db_column='RESNAME', max_length=255, null=True)),
            ],
            options={
                'db_table': 'NFVO_JOB',
            },
        ),
        migrations.CreateModel(
            name='JobStatusModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('indexid', models.IntegerField(db_column='INDEXID')),
                ('jobid', models.CharField(db_column='JOBID', max_length=255)),
                ('status', models.CharField(db_column='STATUS', max_length=255)),
                ('progress', models.IntegerField(blank=True, db_column='PROGRESS', null=True)),
                ('descp', models.TextField(db_column='DESCP', max_length=65535)),
                ('errcode', models.CharField(blank=True, db_column='ERRCODE', max_length=255, null=True)),
                ('addtime', models.CharField(blank=True, db_column='ADDTIME', max_length=255, null=True)),
            ],
            options={
                'db_table': 'NFVO_JOB_STATUS',
            },
        ),
        migrations.CreateModel(
            name='NfInstModel',
            fields=[
                ('nfinstid', models.CharField(db_column='NFINSTID', max_length=200, primary_key=True, serialize=False)),
                ('mnfinstid', models.CharField(blank=True, db_column='M_NFINSTID', max_length=200, null=True)),
                ('nf_name', models.CharField(blank=True, db_column='NFNAME', max_length=100, null=True)),
                ('template_id', models.CharField(blank=True, db_column='TEMPLATEID', max_length=200, null=True)),
                ('vnf_id', models.CharField(blank=True, db_column='VNFID', max_length=200, null=True)),
                ('package_id', models.CharField(blank=True, db_column='PACKAGEID', max_length=200, null=True)),
                ('vnfm_inst_id', models.CharField(blank=True, db_column='VNFMINSTID', max_length=200, null=True)),
                ('ns_inst_id', models.CharField(blank=True, db_column='NSINSTID', max_length=200, null=True)),
                ('status', models.CharField(blank=True, db_column='STATUS', max_length=20, null=True)),
                ('flavour_id', models.CharField(blank=True, db_column='FLAVOURID', max_length=200, null=True)),
                ('vnf_level', models.CharField(blank=True, db_column='VNFLEVEL', max_length=200, null=True)),
                ('location', models.CharField(blank=True, db_column='LOCATION', max_length=200, null=True)),
                ('max_vm', models.IntegerField(db_column='MAXVM', null=True)),
                ('max_cpu', models.IntegerField(db_column='MAXCPU', null=True)),
                ('max_ram', models.IntegerField(db_column='MAXRAM', null=True)),
                ('max_hd', models.IntegerField(db_column='MAXHD', null=True)),
                ('max_shd', models.IntegerField(db_column='MAXSHD', null=True)),
                ('max_net', models.IntegerField(db_column='MAXNET', null=True)),
                ('version', models.CharField(db_column='VERSION', max_length=255, null=True)),
                ('vendor', models.CharField(blank=True, db_column='VENDOR', max_length=255, null=True)),
                ('vnfd_model', models.TextField(blank=True, db_column='VNFDMODEL', max_length=20000, null=True)),
                ('input_params', models.TextField(blank=True, db_column='INPUTPARAMS', max_length=2000, null=True)),
                ('scale_params', models.TextField(blank=True, db_column='SCALEPARAMS', max_length=2000, null=True)),
                ('create_time', models.CharField(blank=True, db_column='CREATETIME', max_length=200, null=True)),
                ('lastuptime', models.CharField(blank=True, db_column='LASTUPTIME', max_length=200, null=True)),
                ('extension', models.TextField(blank=True, db_column='EXTENSION', max_length=65535, null=True)),
            ],
            options={
                'db_table': 'NFVO_NFINST',
            },
        ),
        migrations.CreateModel(
            name='NfPackageModel',
            fields=[
                ('uuid', models.CharField(db_column='UUID', max_length=255, primary_key=True, serialize=False)),
                ('nfpackageid', models.CharField(db_column='NFPACKAGEID', max_length=200)),
                ('vnfdid', models.CharField(db_column='VNFDID', max_length=255)),
                ('vendor', models.CharField(db_column='VENDOR', max_length=255)),
                ('vnfdversion', models.CharField(db_column='VNFDVERSION', max_length=255)),
                ('vnfversion', models.CharField(db_column='VNFVERSION', max_length=255)),
                ('vnfdmodel', models.TextField(blank=True, db_column='VNFDMODEL', max_length=65535, null=True)),
                ('vnfd_path', models.CharField(blank=True, db_column='VNFDPATH', max_length=300, null=True)),
            ],
            options={
                'db_table': 'NFVO_NFPACKAGE',
            },
        ),
        migrations.CreateModel(
            name='NSDModel',
            fields=[
                ('id', models.CharField(db_column='ID', max_length=200, primary_key=True, serialize=False)),
                ('nsd_id', models.CharField(db_column='NSDID', max_length=200)),
                ('name', models.CharField(db_column='NAME', max_length=200)),
                ('vendor', models.CharField(blank=True, db_column='VENDOR', max_length=200, null=True)),
                ('description', models.CharField(blank=True, db_column='DESCRIPTION', max_length=200, null=True)),
                ('version', models.CharField(blank=True, db_column='VERSION', max_length=200, null=True)),
                ('nsd_model', models.TextField(blank=True, db_column='NSDMODEL', max_length=65535, null=True)),
                ('nsd_path', models.CharField(blank=True, db_column='NSDPATH', max_length=300, null=True)),
            ],
            options={
                'db_table': 'NFVO_NSPACKAGE',
            },
        ),
        migrations.CreateModel(
            name='NSInstModel',
            fields=[
                ('id', models.CharField(db_column='ID', max_length=200, primary_key=True, serialize=False)),
                ('name', models.CharField(db_column='NAME', max_length=200)),
                ('nspackage_id', models.CharField(blank=True, db_column='NSPACKAGEID', max_length=200, null=True)),
                ('nsd_id', models.CharField(db_column='NSDID', max_length=200)),
                ('nsd_invariant_id', models.CharField(db_column='NSDINVARIANTID', max_length=200)),
                ('description', models.CharField(blank=True, db_column='DESCRIPTION', max_length=255, null=True)),
                ('sdncontroller_id', models.CharField(blank=True, db_column='SDNCONTROLLERID', max_length=200, null=True)),
                ('flavour_id', models.CharField(blank=True, db_column='FLAVOURID', max_length=200, null=True)),
                ('ns_level', models.CharField(blank=True, db_column='NSLEVEL', max_length=200, null=True)),
                ('status', models.CharField(blank=True, db_column='STATUS', max_length=200, null=True)),
                ('nsd_model', models.TextField(blank=True, db_column='NSDMODEL', max_length=20000, null=True)),
                ('input_params', models.TextField(blank=True, db_column='INPUTPARAMS', max_length=2000, null=True)),
                ('scale_params', models.TextField(blank=True, db_column='SCALEPARAMS', max_length=2000, null=True)),
                ('create_time', models.CharField(blank=True, db_column='CREATETIME', max_length=200, null=True)),
                ('lastuptime', models.CharField(blank=True, db_column='LASTUPTIME', max_length=200, null=True)),
                ('global_customer_id', models.CharField(blank=True, db_column='GLOBALCUSTOMERID', max_length=50, null=True)),
                ('service_type', models.CharField(blank=True, db_column='SERVICETYPE', max_length=50, null=True)),
            ],
            options={
                'db_table': 'NFVO_NSINST',
            },
        ),
        migrations.CreateModel(
            name='NSLcmOpOccModel',
            fields=[
                ('id', models.CharField(db_column='ID', max_length=255, primary_key=True, serialize=False)),
                ('operation_state', models.CharField(db_column='OPERATIONSTATE', max_length=30)),
                ('state_entered_time', models.CharField(db_column='STATEENTEREDTIME', max_length=30)),
                ('start_time', models.CharField(db_column='STARTTIME', max_length=30)),
                ('ns_instance_id', models.CharField(db_column='NSINSTANCEID', max_length=255)),
                ('operation', models.CharField(db_column='OPERATION', max_length=30)),
                ('is_automatic_invocation', models.CharField(db_column='ISAUTOMATICINVOCATION', max_length=5)),
                ('operation_params', models.TextField(db_column='OPERATIONPARAMS')),
                ('is_cancel_pending', models.CharField(db_column='ISCANCELPENDING', max_length=5)),
                ('cancel_mode', models.TextField(db_column='CANCELMODE', null=True)),
                ('error', models.TextField(db_column='ERROR', null=True)),
                ('resource_changes', models.TextField(db_column='RESOURCECHANGES', null=True)),
                ('links', models.TextField(db_column='LINKS')),
            ],
            options={
                'db_table': 'NSLCMOPOCCS',
            },
        ),
        migrations.CreateModel(
            name='OOFDataModel',
            fields=[
                ('request_id', models.CharField(db_column='REQUESTID', max_length=255)),
                ('transaction_id', models.CharField(db_column='TRANSACTIONID', max_length=255)),
                ('request_status', models.CharField(db_column='REQUESTSTATUS', max_length=50)),
                ('request_module_name', models.CharField(db_column='RESOURCEMODULENAME', max_length=100)),
                ('service_resource_id', models.CharField(db_column='SERVICERESOURCEID', max_length=255, primary_key=True, serialize=False)),
                ('vim_id', models.CharField(blank=True, db_column='VIMID', max_length=255, null=True)),
                ('cloud_owner', models.CharField(blank=True, db_column='CLOUDOWNER', max_length=100, null=True)),
                ('cloud_region_id', models.CharField(blank=True, db_column='CLOUDREGIONID', max_length=255, null=True)),
                ('vdu_info', models.TextField(blank=True, db_column='VDUINFO', max_length=65535, null=True)),
            ],
            options={
                'db_table': 'NFVO_OOF_DATA',
            },
        ),
        migrations.CreateModel(
            name='PNFInstModel',
            fields=[
                ('pnfId', models.CharField(db_column='PNFID', max_length=255, primary_key=True, serialize=False)),
                ('pnfName', models.CharField(db_column='PNFNAME', max_length=255)),
                ('pnfdId', models.CharField(db_column='PNFDID', max_length=50)),
                ('pnfdInfoId', models.CharField(db_column='PNFDINFOID', max_length=100)),
                ('pnfProfileId', models.CharField(db_column='PNFPROFILEID', max_length=255)),
                ('cpInfo', models.TextField(blank=True, db_column='CPINFO', max_length=255, null=True)),
                ('emsId', models.CharField(db_column='EMSID', max_length=255, null=True)),
                ('nsInstances', models.TextField(blank=True, db_column='NSINSTANCES', max_length=1000, null=True)),
            ],
            options={
                'db_table': 'NFVO_PNFINST',
            },
        ),
        migrations.CreateModel(
            name='PortInstModel',
            fields=[
                ('portid', models.CharField(db_column='PORTID', max_length=255, primary_key=True, serialize=False)),
                ('networkid', models.CharField(db_column='NETWORKID', max_length=255)),
                ('subnetworkid', models.CharField(db_column='SUBNETWORKID', max_length=255)),
                ('vimid', models.CharField(db_column='VIMID', max_length=255)),
                ('resourceid', models.CharField(db_column='RESOURCEID', max_length=255)),
                ('name', models.CharField(db_column='NAME', max_length=255)),
                ('instid', models.CharField(db_column='INSTID', max_length=255)),
                ('cpinstanceid', models.CharField(db_column='CPINSTANCEID', max_length=255)),
                ('bandwidth', models.CharField(db_column='BANDWIDTH', max_length=255)),
                ('operationalstate', models.CharField(db_column='OPERATIONALSTATE', max_length=255)),
                ('ipaddress', models.CharField(db_column='IPADDRESS', max_length=255)),
                ('macaddress', models.CharField(db_column='MACADDRESS', max_length=255)),
                ('floatipaddress', models.CharField(db_column='FLOATIPADDRESS', max_length=255)),
                ('serviceipaddress', models.CharField(db_column='SERVICEIPADDRESS', max_length=255)),
                ('typevirtualnic', models.CharField(db_column='TYPEVIRTUALNIC', max_length=255)),
                ('sfcencapsulation', models.CharField(db_column='SFCENCAPSULATION', max_length=255)),
                ('direction', models.CharField(db_column='DIRECTION', max_length=255)),
                ('tenant', models.CharField(db_column='TENANT', max_length=255)),
            ],
            options={
                'db_table': 'NFVO_PORTINST',
            },
        ),
        migrations.CreateModel(
            name='ServiceBaseInfoModel',
            fields=[
                ('service_id', models.CharField(db_column='serviceId', max_length=255, primary_key=True, serialize=False)),
                ('service_name', models.CharField(db_column='serviceName', max_length=255)),
                ('service_type', models.CharField(db_column='serviceType', max_length=20)),
                ('description', models.CharField(blank=True, db_column='description', max_length=255, null=True)),
                ('active_status', models.CharField(db_column='activeStatus', max_length=20)),
                ('status', models.CharField(db_column='status', max_length=20)),
                ('creator', models.CharField(db_column='creator', max_length=50)),
                ('create_time', models.BigIntegerField(db_column='createTime')),
            ],
            options={
                'db_table': 't_lcm_servicebaseinfo',
            },
        ),
        migrations.CreateModel(
            name='SubscriptionModel',
            fields=[
                ('subscription_id', models.CharField(db_column='SUBSCRIPTIONID', max_length=255, primary_key=True, serialize=False)),
                ('vnf_instance_filter', models.TextField(db_column='VNFINSTANCEFILTER', null=True)),
                ('ns_instance_filter', models.TextField(db_column='NSINSTANCEFILTER', null=True)),
                ('notification_types', models.TextField(db_column='NOTIFICATIONTYPES', null=True)),
                ('operation_types', models.TextField(db_column='OPERATIONTYPES', null=True)),
                ('operation_states', models.TextField(db_column='OPERATIONSTATES', null=True)),
                ('ns_component_types', models.TextField(db_column='NSCOMPONENTTYPES', null=True)),
                ('lcm_opname_impacting_nscomponent', models.TextField(db_column='LCMOPNAMEIMPACTINGNSCOMPONENT', null=True)),
                ('lcm_opoccstatus_impacting_nscomponent', models.TextField(db_column='LCMOPOCCSTATUSIMPACTINGNSCOMPONENT', null=True)),
                ('callback_uri', models.CharField(db_column='CALLBACKURI', max_length=255)),
                ('links', models.TextField(db_column='LINKS', max_length=20000)),
                ('auth_info', models.TextField(blank=True, db_column='AUTHINFO', max_length=20000, null=True)),
            ],
            options={
                'db_table': 'NFVO_SUBSCRIPTION',
            },
        ),
        migrations.CreateModel(
            name='VLInstModel',
            fields=[
                ('vlinstanceid', models.CharField(db_column='VLINSTANCEID', max_length=255, primary_key=True, serialize=False)),
                ('vldid', models.CharField(db_column='VLDID', max_length=255)),
                ('vlinstancename', models.CharField(blank=True, db_column='VLINSTANCENAME', max_length=255, null=True)),
                ('ownertype', models.IntegerField(db_column='OWNERTYPE')),
                ('ownerid', models.CharField(db_column='OWNERID', max_length=255)),
                ('relatednetworkid', models.CharField(blank=True, db_column='RELATEDNETWORKID', max_length=255, null=True)),
                ('relatedsubnetworkid', models.CharField(blank=True, db_column='RELATEDSUBNETWORKID', max_length=255, null=True)),
                ('vltype', models.IntegerField(db_column='VLTYPE', default=0)),
                ('vimid', models.CharField(db_column='VIMID', max_length=255)),
                ('tenant', models.CharField(db_column='TENANT', max_length=255)),
                ('status', models.CharField(db_column='STATUS', max_length=255)),
            ],
            options={
                'db_table': 'NFVO_VLINST',
            },
        ),
        migrations.CreateModel(
            name='VmInstModel',
            fields=[
                ('vmid', models.CharField(db_column='VMID', max_length=255, primary_key=True, serialize=False)),
                ('vimid', models.CharField(db_column='VIMID', max_length=255)),
                ('resouceid', models.CharField(db_column='RESOURCEID', max_length=255)),
                ('insttype', models.IntegerField(db_column='INSTTYPE', null=True)),
                ('instid', models.CharField(db_column='INSTID', max_length=255, null=True)),
                ('vmname', models.CharField(db_column='VMNAME', max_length=255)),
                ('operationalstate', models.IntegerField(db_column='OPERATIONALSTATE', default=1)),
                ('zoneid', models.CharField(db_column='ZONEID', max_length=255, null=True)),
                ('tenant', models.CharField(db_column='TENANT', max_length=255, null=True)),
                ('hostid', models.CharField(db_column='HOSTID', max_length=255)),
                ('detailinfo', models.CharField(db_column='DETAILINFO', max_length=255, null=True)),
            ],
            options={
                'db_table': 'NFVO_VMINST',
            },
        ),
        migrations.CreateModel(
            name='VNFCInstModel',
            fields=[
                ('vnfcinstanceid', models.CharField(db_column='VNFCINSTANCEID', max_length=255, primary_key=True, serialize=False)),
                ('vduid', models.CharField(db_column='VDUID', max_length=255)),
                ('nfinstid', models.CharField(db_column='NFINSTID', max_length=255)),
                ('vmid', models.CharField(db_column='VMID', max_length=255)),
                ('status', models.CharField(db_column='STATUS', max_length=255)),
            ],
            options={
                'db_table': 'NFVO_VNFCINST',
            },
        ),
        migrations.CreateModel(
            name='VNFFGInstModel',
            fields=[
                ('vnffgdid', models.CharField(db_column='VNFFGDID', max_length=255)),
                ('vnffginstid', models.CharField(db_column='VNFFGINSTID', max_length=255, primary_key=True, serialize=False)),
                ('nsinstid', models.CharField(db_column='NSINSTID', max_length=255)),
                ('desc', models.CharField(blank=True, db_column='DESC', max_length=255, null=True)),
                ('vendor', models.CharField(blank=True, db_column='VENDOR', max_length=255, null=True)),
                ('version', models.CharField(blank=True, db_column='VERSION', max_length=255, null=True)),
                ('endpointnumber', models.IntegerField(db_column='ENDPOINTNUMBER')),
                ('vllist', models.CharField(db_column='VLLIST', max_length=1024)),
                ('cplist', models.CharField(db_column='CPLIST', max_length=1024)),
                ('vnflist', models.CharField(db_column='VNFLIST', max_length=1024)),
                ('fplist', models.CharField(db_column='FPLIST', max_length=1024)),
                ('status', models.CharField(db_column='STATUS', max_length=255)),
            ],
            options={
                'db_table': 'NFVO_VNFFGINST',
            },
        ),
        migrations.CreateModel(
            name='VnfPackageFileModel',
            fields=[
                ('id', models.AutoField(db_column='ID', primary_key=True, serialize=False)),
                ('vnfpid', models.CharField(db_column='NFPACKAGEID', max_length=50)),
                ('filename', models.CharField(db_column='FILENAME', max_length=100)),
                ('filetype', models.CharField(db_column='FILETYPE', max_length=2)),
                ('imageid', models.CharField(db_column='IMAGEID', max_length=50)),
                ('vimid', models.CharField(db_column='VIMID', max_length=50)),
                ('vimuser', models.CharField(db_column='VIMUSER', max_length=50)),
                ('tenant', models.CharField(db_column='TENANT', max_length=50)),
                ('purpose', models.CharField(db_column='PURPOSE', max_length=1000)),
                ('status', models.CharField(db_column='STATUS', max_length=10)),
            ],
            options={
                'db_table': 'NFVO_NFPACKAGEFILE',
            },
        ),
        migrations.CreateModel(
            name='WFPlanModel',
            fields=[
                ('deployed_id', models.CharField(db_column='DEPLOYEDID', max_length=255, primary_key=True, serialize=False)),
                ('process_id', models.CharField(db_column='PROCESSID', max_length=255)),
                ('status', models.CharField(db_column='STATUS', max_length=255)),
                ('message', models.CharField(db_column='MESSAGE', max_length=1024)),
                ('plan_name', models.CharField(db_column='PLANNAME', max_length=255)),
            ],
            options={
                'db_table': 'NFVO_WF_PLAN',
            },
        ),
    ]
