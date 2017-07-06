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

from lcm.pub.nfvi.vim.api.openstack import auth, network, image


class OpenstackApi:

    def login(self, connect_info):
        return auth.login(connect_info)

    def query_net(self, auth_info, net_id):
        return network.query_net(auth_info, net_id)

    def query_nets(self, auth_info):
        return network.query_nets(auth_info)

    def query_subnet(self, auth_info, subnet_id):
        return network.query_subnet(auth_info, subnet_id)

    def query_port(self, auth_info, port_id):
        return network.query_port(auth_info, port_id)

    def create_port(self, auth_info, data):
        return network.create_port(auth_info, data)

    def delete_port(self, auth_info, port_id):
        return network.delete_port(auth_info, port_id)

    def create_image(self, auth_info, data):
        return image.create_image(auth_info, data)

    def get_image(self, auth_info, image_id):
        return image.get_image(auth_info, image_id)

    def get_images(self, auth_info):
        return image.get_images(auth_info)

    def delete_image(self, auth_info, image_id):
        return image.delete_image(auth_info, image_id)

    def create_network(self, auth_info, data):
        return network.create_network(auth_info, data)

    def delete_network(self, auth_info, network_id):
        return network.delete_network(auth_info, network_id)

    def delete_subnet(self, auth_info, subnet_id):
        return network.delete_subnet(auth_info, subnet_id)
