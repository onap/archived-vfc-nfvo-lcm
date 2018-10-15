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
import threading
import json
from threading import Thread
from lcm.workflows.graphflow.flow.graph import Graph
from lcm.workflows.graphflow.flow.load import load_class_from_config
from lcm.workflows.graphflow.flow.manager import TaskManager

logger = logging.getLogger(__name__)


def _execute_task(exec_class):
    logger.debug("graph task class %s" % exec_class)
    exec_class.execute()


def create_instance(class_key, class_set, *args):
    if class_key in class_set:
        import_class = class_set[class_key]
        return import_class(*args)
    else:
        return None


class GraphFlow(Thread):
    def __init__(self, graph, task_para_dict, config):
        Thread.__init__(self)
        self._graph = Graph(graph)
        self._task_para_dict = task_para_dict
        self._imp_class_set = load_class_from_config(config)
        self.task_manager = TaskManager()

    def run(self):
        logger.debug("GraphFlow begin. graph:%s, task_para_dict:%s", self._graph, json.dumps(self._task_para_dict))
        self.sort_nodes = self._graph.topo_sort()
        for node in self.sort_nodes:
            pre_nodes = self._graph.get_pre_nodes(node)
            logger.debug("current node %s, pre_nodes %s" % (node, pre_nodes))
            if len(pre_nodes) > 0:
                self.task_manager.wait_tasks_done(pre_nodes)
                if self.task_manager.is_all_task_finished(pre_nodes):
                    self.create_task(node)
                    logger.debug("GraphFlow create node %s", node)
                else:
                    logger.debug("GraphFlow, end, error")
                    break
            else:
                self.create_task(node)
                logger.debug("GraphFlow create node %s", node)
        logger.debug("GraphFlow, end")

    def create_task(self, node):
        task_para = self._task_para_dict[node]
        task_para["key"] = node
        task_para["status"] = "started"
        task_para["manager"] = self.task_manager
        if "type" in task_para:
            class_key = task_para["type"]
            exec_task = create_instance(class_key, self._imp_class_set, task_para)
            self.task_manager.add_task(node, exec_task)
            thread_task = threading.Thread(target=_execute_task, args=(exec_task,))
            thread_task.start()
            return True
        else:
            return False
