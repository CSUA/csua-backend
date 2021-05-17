from django.contrib.redirects.models import Redirect
from django.contrib.sites.models import Site
from django.test import Client, TestCase


class TestRedirectMiddleware(TestCase):
    OLD_PATH = "/facebook/"
    NEW_PATH = "https://facebook.com/csua/"

    def setUp(self):
        Redirect.objects.create(
            old_path=self.OLD_PATH,
            new_path=self.NEW_PATH,
            site=Site.objects.get_current(),
        )

    def test_redirects(self):
        self.makeSureItWorks("/facebook")
        self.makeSureItWorks("/facebook/")
        self.makeSureItWorks("/facebook?fbclid=poopy")
        self.makeSureItWorks("/facebook/?fbclid=stinky")

    def makeSureItWorks(self, url):
        response = self.client.get(url)
        self.assertRedirects(
            response, self.NEW_PATH, status_code=307, fetch_redirect_response=False
        )
