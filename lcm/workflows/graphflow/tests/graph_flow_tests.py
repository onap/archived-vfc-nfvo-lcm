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

import unittest
import mock
import json
from lcm.pub.utils import restcall
from lcm.workflows.graphflow.flow.flow import GraphFlow


config = {
    "CreateSynVNF": {"module": "lcm.workflows.graphflow.tests.task_tests", "class": "CreateSynVNF"},
    "CreateAsynVNF": {"module": "lcm.workflows.graphflow.tests.task_tests", "class": "CreateAsynVNF"},
    "CreateASynRestVNF": {"module": "lcm.workflows.graphflow.tests.task_tests", "class": "CreateASynRestVNF"}
}


class test(object):
    def execute(self, args):
        print("test args %s" % args)


class GraphFlowTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_sync_task(self):
        deploy_graph = {
            "ran-cu-00": ["ran-du-00"],
            "ran-du-00": [],
        }
        TaskSet = {
            'ran-cu-00': {
                "type": "CreateSynVNF",
                "input": {
                    "nsInstanceId": 1,
                    "vnfId": 1
                },
                "timeOut": 10
            },
            'ran-du-00': {
                "type": "CreateSynVNF",
                "input": {
                    "nsInstanceId": 1,
                    "vnfId": 1
                },
                "timeOut": 10
            }
        }
        gf = GraphFlow(deploy_graph, TaskSet, config)
        gf.start()
        gf.join()
        gf.task_manager.wait_tasks_done(gf.sort_nodes)
        task_set = gf.task_manager.get_all_task()
        for task in list(task_set.values()):
            self.assertEqual(task.FINISHED, task.status)

    def test_async_task(self):
        deploy_graph = {
            "ran-cu-01": ["ran-du-01"],
            "ran-du-01": [],
        }
        TaskSet = {
            'ran-cu-01': {
                "type": "CreateAsynVNF",
                "input": {
                    "nsInstanceId": 1,
                    "vnfId": 1
                },
                "timeOut": 10
            },
            'ran-du-01': {
                "type": "CreateAsynVNF",
                "input": {
                    "nsInstanceId": 1,
                    "vnfId": 1
                },
                "timeOut": 10
            }
        }
        gf = GraphFlow(deploy_graph, TaskSet, config)
        gf.start()
        gf.join()
        gf.task_manager.wait_tasks_done(gf.sort_nodes)
        task_set = gf.task_manager.get_all_task()
        for task in list(task_set.values()):
            self.assertEqual(task.FINISHED, task.status)

    @mock.patch.object(restcall, 'call_req')
    def test_async_rest_task(self, mock_call_req):
        mock_call_req.return_value = [0, json.JSONEncoder().encode({
            'jobId': "1",
            "responseDescriptor": {"progress": 100}
        }), '200']

        deploy_graph = {
            "ran-cu-02": ["ran-du-02"],
            "ran-du-02": [],
        }
        TaskSet = {
            'ran-cu-02': {
                "type": "CreateASynRestVNF",
                "input": {
                    "url": "/test/",
                    "method": "POST",
                    "content": {}
                },
                "timeOut": 10
            },
            'ran-du-02': {
                "type": "CreateASynRestVNF",
                "input": {
                    "url": "/test/",
                    "method": "POST",
                    "content": {}
                },
                "timeOut": 10
            }
        }
        gf = GraphFlow(deploy_graph, TaskSet, config)
        gf.start()
        gf.join()
        gf.task_manager.wait_tasks_done(gf.sort_nodes)
        task_set = gf.task_manager.get_all_task()
        for task in list(task_set.values()):
            self.assertEqual(task.FINISHED, task.status)
