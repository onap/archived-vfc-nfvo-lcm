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

from django.contrib import admin

from lcm.pub.database.models import NSDModel
from lcm.pub.database.models import NSInstModel
from lcm.pub.database.models import NfPackageModel
from lcm.pub.database.models import VnfPackageFileModel
from lcm.pub.database.models import FPInstModel
from lcm.pub.database.models import VNFFGInstModel
from lcm.pub.database.models import NfInstModel
from lcm.pub.database.models import VmInstModel
from lcm.pub.database.models import VNFCInstModel
from lcm.pub.database.models import CPInstModel
from lcm.pub.database.models import VLInstModel
from lcm.pub.database.models import PortInstModel
from lcm.pub.database.models import JobModel
from lcm.pub.database.models import JobStatusModel
from lcm.pub.database.models import DefPkgMappingModel
from lcm.pub.database.models import InputParamMappingModel
from lcm.pub.database.models import ServiceBaseInfoModel
from lcm.pub.database.models import WFPlanModel
from lcm.pub.database.models import OOFDataModel
from lcm.pub.database.models import SubscriptionModel
from lcm.pub.database.models import NSLcmOpOccModel
from lcm.pub.database.models import PNFInstModel


@admin.register(NSDModel)
class NSDModelAdmin(admin.ModelAdmin):
    list_display_links = ('id', 'name')
    fields = [
        "id",
        "nsd_id",
        "name",
        "vendor",
        "description",
        "version",
        "nsd_model",
        "nsd_path"
    ]

    list_display = [
        "id",
        "nsd_id",
        "name",
        "vendor",
        "description",
        "version",
        "nsd_model",
        "nsd_path"
    ]

    search_fields = (
        "id",
        "nsd_id",
        "name"
    )


@admin.register(NSInstModel)
class NSInstModelAdmin(admin.ModelAdmin):
    list_display_links = ('id', 'name')
    fields = [
        "id",
        "name",
        "nspackage_id",
        "nsd_id",
        "nsd_invariant_id",
        "description",
        "sdncontroller_id",
        "flavour_id",
        "ns_level",
        "status",
        "nsd_model",
        "input_params",
        "scale_params",
        "create_time",
        "lastuptime",
        "global_customer_id",
        "service_type"
    ]

    list_display = [
        "id",
        "name",
        "nspackage_id",
        "nsd_id",
        "nsd_invariant_id",
        "description",
        "sdncontroller_id",
        "flavour_id",
        "ns_level",
        "status",
        "nsd_model",
        "input_params",
        "scale_params",
        "create_time",
        "lastuptime",
        "global_customer_id",
        "service_type"
    ]

    search_fields = (
        "id",
        "name",
        "nsd_id"
    )


@admin.register(NfInstModel)
class NfInstModelAdmin(admin.ModelAdmin):
    list_display_links = ('nfinstid', 'nf_name')
    fields = [
        "nfinstid",
        "mnfinstid",
        "nf_name",
        "template_id",
        "vnf_id",
        "package_id",
        "vnfm_inst_id",
        "ns_inst_id",
        "status",
        "flavour_id",
        "vnf_level",
        "location",
        "max_vm",
        "max_cpu",
        "max_ram",
        "max_hd",
        "max_shd",
        "max_net",
        "version",
        "vendor",
        "vnfd_model",
        "input_params",
        "scale_params",
        "create_time",
        "lastuptime",
        "extension"
    ]

    list_display = [
        "nfinstid",
        "mnfinstid",
        "nf_name",
        "template_id",
        "vnf_id",
        "package_id",
        "vnfm_inst_id",
        "ns_inst_id",
        "status",
        "flavour_id",
        "vnf_level",
        "location",
        "max_vm",
        "max_cpu",
        "max_ram",
        "max_hd",
        "max_shd",
        "max_net",
        "version",
        "vendor",
        "vnfd_model",
        "input_params",
        "scale_params",
        "create_time",
        "lastuptime",
        "extension"
    ]

    search_fields = (
        "nfinstid",
        "nf_name",
        "ns_inst_id"
    )


@admin.register(VmInstModel)
class VmInstModelAdmin(admin.ModelAdmin):
    list_display_links = ('vmid', 'resouceid')
    fields = [
        "vmid",
        "vimid",
        "resouceid",
        "insttype",
        "instid",
        "vmname",
        "operationalstate",
        "zoneid",
        "tenant",
        "hostid",
        "detailinfo"
    ]

    list_display = [
        "vmid",
        "vimid",
        "resouceid",
        "insttype",
        "instid",
        "vmname",
        "operationalstate",
        "zoneid",
        "tenant",
        "hostid",
        "detailinfo"
    ]

    search_fields = (
        "vmid",
        "vimid",
        "resouceid"
    )


@admin.register(VNFCInstModel)
class VNFCInstModelAdmin(admin.ModelAdmin):
    list_display_links = ('vnfcinstanceid', 'vduid')
    fields = [
        "vnfcinstanceid",
        "vduid",
        "nfinstid",
        "vmid",
        "status"
    ]

    list_display = [
        "vnfcinstanceid",
        "vduid",
        "nfinstid",
        "vmid",
        "status"
    ]

    search_fields = (
        "vnfcinstanceid",
        "vduid",
        "nfinstid"
    )


@admin.register(VLInstModel)
class VLInstModelAdmin(admin.ModelAdmin):
    list_display_links = ('vlinstanceid', 'vldid')
    fields = [
        "vlinstanceid",
        "vldid",
        "vlinstancename",
        "ownertype",
        "ownerid",
        "relatednetworkid",
        "relatedsubnetworkid",
        "vltype",
        "vimid",
        "tenant",
        "status",
    ]

    list_display = [
        "vlinstanceid",
        "vldid",
        "vlinstancename",
        "ownertype",
        "ownerid",
        "relatednetworkid",
        "relatedsubnetworkid",
        "vltype",
        "vimid",
        "tenant",
        "status",
    ]

    search_fields = (
        "vlinstanceid",
        "vldid",
        "vlinstancename"
    )


@admin.register(OOFDataModel)
class OOFDataModelAdmin(admin.ModelAdmin):
    list_display_links = ('request_id', 'transaction_id')
    fields = [
        "request_id",
        "transaction_id",
        "request_status",
        "request_module_name",
        "service_resource_id",
        "vim_id",
        "cloud_owner",
        "cloud_region_id",
        "vdu_info"
    ]

    list_display = [
        "request_id",
        "transaction_id",
        "request_status",
        "request_module_name",
        "service_resource_id",
        "vim_id",
        "cloud_owner",
        "cloud_region_id",
        "vdu_info"
    ]

    search_fields = (
        "request_id",
        "transaction_id"
    )


admin.site.register(NfPackageModel)
admin.site.register(VnfPackageFileModel)
admin.site.register(FPInstModel)
admin.site.register(CPInstModel)
admin.site.register(VNFFGInstModel)
admin.site.register(PortInstModel)
admin.site.register(JobModel)
admin.site.register(JobStatusModel)
admin.site.register(DefPkgMappingModel)
admin.site.register(InputParamMappingModel)
admin.site.register(ServiceBaseInfoModel)
admin.site.register(WFPlanModel)
admin.site.register(SubscriptionModel)
admin.site.register(NSLcmOpOccModel)
admin.site.register(PNFInstModel)
