# Copyright 2016-2017 ZTE Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# import json
from django.test import TestCase

from rest_framework.test import APIClient
# from rest_framework import status


class SwaggerViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def tearDown(self):
        pass

    # def test_swagger(self):
    #  response = self.client.get("/api/nslcm/v1/swagger.json")
    #  self.assertEqual(status.HTTP_200_OK, response.status_code, response.content)
    #  with open('vfc.json', 'w') as swagger_file:
    #      swagger_file.write(json.dumps(response.data))
