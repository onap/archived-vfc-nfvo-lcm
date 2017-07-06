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

"""
import unittest
import os
import time

from lcm.pub.nfvi.vim import vimadaptor
from lcm.pub.nfvi.vim.test.openstack import pub
from lcm.pub.nfvi.vim import const


class TestImage(unittest.TestCase):
    def setUp(self):
        self.api = vimadaptor.VimAdaptor(pub.connect_info)
        self.currentdir = os.path.dirname(os.path.abspath(__file__))
    def tearDown(self):
        pass
    def createImg(self, data):
        return self.api.create_image(data)

    def test_image_all(self):
        image_data = {
            "image_name": "cirros",
            "image_path": self.currentdir + "/testdata/cirros.qcow2",
            "image_type": "qcow2"
        }

        # create image
        ret = self.createImg(image_data)
        self.assertEqual(0, ret[0])
        if ret[1][const.RES_TYPE_KEY] == const.RES_TYPE_EXIST:
            self.api.delete_image(image_id = ret[1]["id"])
            ret = self.createImg(image_data)
        self.assertEqual(0, ret[0])
        imageid = ret[1]["id"]
        retryTimes = 0
        while retryTimes < 10:
            ret = self.api.get_image(image_id = imageid)
            self.assertEqual(0, ret[0])
            if ret[1]["status"] == 'active':
                break
            time.sleep(2)

        # image is exist
        ret = self.createImg(image_data)
        self.assertEqual(0, ret[0])
        self.assertEqual(const.RES_TYPE_EXIST, ret[1][const.RES_TYPE_KEY])

        # get all images
        ret = self.api.get_images()
        self.assertEqual(0, ret[0])
        flag = False
        for image in ret[1]['image_list']:
            if image_data["image_name"] == image["name"]:
                flag = True
                break
        self.assertTrue(flag)

        # delete image
        ret = self.api.delete_image(image_id = imageid)
        self.assertEqual(0, ret[0])

        # get_image except
        ret = self.api.get_image(image_id = imageid)
        self.assertEqual(2, ret[0])

        # delete image except
        ret = self.api.delete_image(image_id = imageid)
        self.assertEqual(0, ret[0])

        # Exception
        image_data["image_path"] = "aaaa"
        ret = self.createImg(image_data)
        self.assertEqual(0, ret[0])

        imageid = ret[1]["id"]
        self.api.delete_image(image_id = imageid)
"""
