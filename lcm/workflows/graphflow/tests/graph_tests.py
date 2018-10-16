# Copyright 2018 ZTE Corporation.
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
import logging

from django.test import TestCase
from lcm.workflows.graphflow.flow.graph import Graph

logger = logging.getLogger(__name__)


class TestToscaparser(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_graph(self):
        data = {
            "cucp": [],
            "du": [],
            "vl_flat_net": ["cucp", "cuup"],
            "vl_ext_net": ["cucp", "cuup"],
            "cuup": []
        }
        graph = Graph(data)
        self.assertEqual(['vl_ext_net', 'vl_flat_net'].sort(), graph.get_pre_nodes("cucp").sort())
