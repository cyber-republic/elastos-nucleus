from django.test import TestCase
from django.test import client
from selenium import webdriver
from decouple import config
import random


class test_qrcodes(TestCase):
    def setUp(self):
        self.client = client.Client()
        self.response = self.client.get('')

    def test_elastos_url_exists(self):
        assert 'elastos_url' in self.response.context

    def test_elastos_url_base(self):
        assert 'elastos://credaccess/' in self.response.context['elastos_url']

    def test_elaphant_url_exists(self):
        assert 'elaphant_url' in self.response.context

    def test_elaphant_url_base(self):
        assert 'elaphant://identity?' in self.response.context['elaphant_url']

    def tearDown(self):
        self.client = None


class test_login(TestCase):

    def setUp(self) -> None:
        self.client = client.Client()

    def test_login_required(self):
        response = self.client.get('/service/generate_key' , follow=True)
        print(response)



    def tearDown(self) -> None:
        pass


