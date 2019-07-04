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

import importlib
import logging


logger = logging.getLogger(__name__)


def load_module(imp_module):
    try:
        imp_module = importlib.import_module(imp_module)
    except Exception:
        logger.debug("load_module error: %s", imp_module)
        imp_module = None
    return imp_module


def load_class(imp_module, imp_class):
    try:
        cls = getattr(imp_module, imp_class)
    except Exception:
        logger.debug("load_class error: %s", imp_class)
        cls = None
    return cls


def load_class_from_config(config):
    class_set = {}
    for k, v in list(config.items()):
        imp_module = load_module(v["module"])
        cls = load_class(imp_module, v["class"])
        class_set[k] = cls
    return class_set
