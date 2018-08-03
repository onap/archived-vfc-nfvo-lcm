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
import json

from django.core.management.base import BaseCommand
from django.test import Client


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            '--name',
            action='store',
            dest='name',
            default='swagger.json',
            help='name of swagger file.',
        )

    def handle(self, *args, **options):
        self.client = Client()
        response = self.client.get("/api/nslcm/v1/swagger.json")
        with open(options['name'], 'w') as swagger_file:
            swagger_file.write(json.dumps(response.data))
        print "swagger api is written to %s" % options['name']
