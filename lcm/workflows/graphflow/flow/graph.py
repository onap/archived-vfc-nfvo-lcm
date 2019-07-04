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
from collections import deque
from collections import OrderedDict

logger = logging.getLogger(__name__)


class Graph(object):

    def __init__(self, graph_dict=None):
        self.graph = OrderedDict()
        if graph_dict:
            for node, dep_nodes in list(graph_dict.items()):
                self.add_node(node, dep_nodes)

    def add_node(self, node, dep_nodes):
        if node not in self.graph:
            self.graph[node] = set()
        if isinstance(dep_nodes, list):
            for dep_node in dep_nodes:
                if dep_node not in self.graph:
                    self.graph[dep_node] = set()
                if dep_node not in self.graph[node]:
                    self.graph[node].add(dep_node)

    def get_pre_nodes(self, node):
        return [k for k in self.graph if node in self.graph[k]]

    def topo_sort(self):
        degree = {}
        for node in self.graph:
            degree[node] = 0
        for node in self.graph:
            for dependent in self.graph[node]:
                degree[dependent] += 1
        queue = deque()
        for node in degree:
            if degree[node] == 0:
                queue.appendleft(node)
        sort_list = []
        while queue:
            node = queue.pop()
            sort_list.append(node)
            for dependent in self.graph[node]:
                degree[dependent] -= 1
                if degree[dependent] == 0:
                    queue.appendleft(dependent)
        if len(sort_list) == len(self.graph):
            return sort_list
        else:
            return None

    def to_dict(self):
        dict = {}
        for node, dependents in list(self.graph.items()):
            dict[node] = []
            for dep in dependents:
                dict[node].append(dep)
        return dict
