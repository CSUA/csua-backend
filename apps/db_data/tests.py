from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from apps.ldap.test_helpers import LDAPTestCase

from .models import (
    Officer,
    Officership,
    Person,
    Politburo,
    PolitburoMembership,
    Semester,
)
from .staff_views import update_or_create_officer


class TestPages(LDAPTestCase):
    def setUp(self):
        super().setUp()
        pnunez_user = User.objects.create_user(
            first_name="Phillip",
            last_name="Nunez",
            username="pnunez",
            email="pnunez@csua.berkeley.edu",
            password="passwurd",
            is_staff=True,
        )
        pnunez_person = Person(pnunez_user)
        pnunez_person.save()
        pnunez_officer = Officer(person=pnunez_person)
        pnunez_officer.save()
        semester = Semester(id="fa72", name="Fall 1972", current=True)
        semester.save()
        officership = Officership(
            officer=pnunez_officer,
            semester=semester,
            blurb="I love the CSUA",
            office_hours="Fri 6-7 PM",
        )
        officership.save()

        president = Politburo(
            position="president",
            title="Hoser President",
            description="The president is a cool person.",
            contact="Reach out to [name] to be epic.",
        )
        president.save()
        pnunez_prez = PolitburoMembership(
            politburo=president, semester=semester, person=pnunez_person
        )
        pnunez_prez.save()

    def test_officers(self):
        response = self.client.get("/officers/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Phillip")

    def test_pb(self):
        response = self.client.get("/politburo/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Phillip")

    def test_sponsors(self):
        response = self.client.get("/sponsors/")
        self.assertEqual(response.status_code, 200)

    def test_tutoring(self):
        response = self.client.get("/tutoring/")
        self.assertEqual(response.status_code, 200)

    def test_events(self):
        response = self.client.get("/events/")
        self.assertEqual(response.status_code, 200)

    def test_update_or_create_officer_staff_only(self):
        url = reverse("add-officer")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.client.login(username="pnunez", password="passwurd")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_or_create_officer_failure(self):
        url = reverse("add-officer")
        self.client.login(username="pnunez", password="passwurd")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url, data={"username": "pnunez"}, follow=True)
        self.assertFormError(response, "form", None, ["User pnunez is not in LDAP"])
        response = self.client.post(url, data={"username": "cnunez"}, follow=True)
        self.assertContains(response, "User cnunez created")
        self.assertContains(response, "Person cnunez created")
        self.assertContains(response, "Officer cnunez created")
        self.assertContains(response, "Added cnunez to officers LDAP group")
