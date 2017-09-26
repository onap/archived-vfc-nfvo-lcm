# Copyright 2017 ZTE Corporation.
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

from toscaparser.dataentity import DataEntity
from toscaparser.elements.constraints import Schema
from toscaparser.common.exception import ExceptionCollector


class DataEntityExt(object):
    '''A complex data value entity ext.'''
    @staticmethod
    def validate_datatype(type, value, entry_schema=None, custom_def=None):
        if value:
            if (type == Schema.STRING):
                return str(value)
            elif type == Schema.FLOAT:
                try:
                    return float(value)
                except Exception:
                    ExceptionCollector.appendException(ValueError(('"%s" is not an float.') % value))
            return DataEntity.validate_datatype(type, value, entry_schema, custom_def)
        return value
