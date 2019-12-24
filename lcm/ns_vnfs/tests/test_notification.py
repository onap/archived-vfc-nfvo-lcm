from django.test import TestCase, Client




class TestGetVnfViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.nf_inst_id = str(uuid.uuid4())
        NfInstModel(nfinstid=self.nf_inst_id, nf_name="vnf1", vnfm_inst_id="1", vnf_id="vnf_id1",
                    status=VNF_STATUS.ACTIVE, create_time=now_time(), lastuptime=now_time()).save()

    def tearDown(self):
        NfInstModel.objects.all().delete()

    def test_get_vnf(self):
        response = self.client.get("/api/nslcm/v1/ns/vnfs/%s" % self.nf_inst_id)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        context = json.loads(response.content)
        self.assertEqual(self.nf_inst_id, context["vnfInstId"])
