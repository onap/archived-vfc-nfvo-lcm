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

import logging
import sys
import traceback
import threading

from lcm.pub.nfvi.vim.api.openstack import glancebase
from lcm.pub.nfvi.vim.lib.syscomm import fun_name
from lcm.pub.nfvi.vim import const

logger = logging.getLogger(__name__)


class ImageUploadThread(threading.Thread):
    def __init__(self, glance, image_id, image_path):
        threading.Thread.__init__(self)
        self.glance = glance
        self.image_id = image_id
        self.image_path = image_path

    def run(self):
        try:
            self.glance.images.upload(self.image_id, open(self.image_path, 'rb'))
        except Exception as ex:
            logger.error(traceback.format_exc())
            err_msg = ex.message if ex.message else str(sys.exc_info())
            logger.error("Failed to upload image(%s): %s", self.image_id, err_msg)
        except:
            logger.error(traceback.format_exc())
            logger.error("Failed to upload image(%s): [%s]", self.image_id, str(sys.exc_info()))


def create_image(auth_info, data):
    ret = None
    glance = glancebase.get_glance(fun_name(), auth_info)

    exist_img = [img for img in glance.images.list() if img.name == data["image_name"]]
    if exist_img:
        ret = [0, {"id": exist_img[0].id, "name": data["image_name"], const.RES_TYPE_KEY: const.RES_TYPE_EXIST}]
    else:
        img = glance.images.create(
            name=data["image_name"],
            disk_format=data["image_type"],
            visibility='public',
            container_format='bare')
        ret = [0, {"id": img.id, "name": data["image_name"], const.RES_TYPE_KEY: const.RES_TYPE_NEW}]
        try:
            ImageUploadThread(glance, img.id, data["image_path"]).start()
        except:
            logger.error(traceback.format_exc())
            logger.error(str(sys.exc_info()))
    return ret


def get_image(auth_info, image_id):
    from glanceclient.exc import HTTPNotFound
    glance = glancebase.get_glance(fun_name(), auth_info)
    img = None
    try:
        img = glance.images.get(image_id)
    except HTTPNotFound:
        logger.warn("Exception: %s" % str(sys.exc_info()))
        return [2, "Image(%s) does not exist" % image_id]
    ret_img_info = get_single_image(img)
    if 'status' in ret_img_info and 'deleted' == ret_img_info["status"]:
        return [2, "Image(%s) is deleted" % image_id]
    return [0, ret_img_info]


def delete_image(auth_info, image_id):
    from glanceclient.exc import HTTPNotFound
    glance = glancebase.get_glance(fun_name(), auth_info)
    try:
        glance.images.delete(image_id)
    except HTTPNotFound:
        logger.warn("Exception: %s" % str(sys.exc_info()))
        return [0, "Image(%s) does not exist" % image_id]
    return [0, "Image(%s) has been deleted" % image_id]


def get_images(auth_info):
    glance = glancebase.get_glance(fun_name(), auth_info)
    imgs = glance.images.list()
    return [0, {"image_list": [get_single_image(img) for img in imgs]}]


def get_single_image(img):
    img_size = 0
    try:
        img_size = img.size / 1024
    except:
        pass
    return {"id": img.id, "name": img.name, "size": img_size, "status": img.status}
