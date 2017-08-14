# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import mock
import uuid
from rest_framework import status
from django.test import TestCase
from django.test import Client
from lcm.pub.database.models import NSDModel, NSInstModel
from lcm.pub.utils.jobutil import JobUtil, JOB_MODEL_STATUS, JOB_TYPE
from lcm.ns.const import NS_INST_STATUS
from lcm.pub.utils import restcall
from lcm.pub.utils import toscautil
from lcm.ns.ns_heal import NSHealService

class TestHealNsViews(TestCase):
    def setUp(self):
        self.nsd_id = str(uuid.uuid4())
        self.ns_package_id = str(uuid.uuid4())
        self.ns_inst_id = str(uuid.uuid4())
        self.job_id = JobUtil.create_job("NS", JOB_TYPE.HEAL_VNF, self.ns_inst_id)
        NSDModel(id=self.ns_package_id, nsd_id=self.nsd_id, name='name').save()

        self.client = Client()
        self.context = '{"vnfs": ["a", "b"], "sfcs": ["c"], "vls": ["d", "e", "f"]}'
        NSInstModel(id=self.ns_inst_id, name="abc", nspackage_id="7", nsd_id="111").save()

    def tearDown(self):
        NSInstModel.objects.filter().delete()

    @mock.patch.object(NSHealService, 'run')
    def test_ns_heal(self, mock_run):
        data = {
            'nsdid': self.nsd_id,
            'nsname': 'ns',
            'description': 'description'}
        response = self.client.post("/openoapi/nslcm/v1/ns/%s/heal" % self.nsd_id, data=data)
        self.failUnlessEqual(status.HTTP_202_ACCEPTED, response.status_code)

    @mock.patch.object(restcall, 'call_req')
    def test_ns_heal_thread(self, mock_call):

        data = {
            'nsdid': self.nsd_id,
            'nsname': 'ns',
            'description': 'description'
        }

        NSHealService(self.ns_inst_id, data, self.job_id)
        self.assertTrue(NSInstModel.objects.get(id=self.ns_inst_id).status, NS_INST_STATUS.ACTIVE)

    def test_swagger_ok(self):
        resp = self.client.get("/openoapi/nslcm/v1/swagger.json", format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
