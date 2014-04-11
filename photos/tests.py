import json

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from .models import Location

class AuthenticatedViews(TestCase):

    def ajax_post_test(self, form_data, url, action):
        response = self.client.post(url, form_data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        result = json.loads(response.content.decode("utf-8"))
        self.assertEqual(result['action'], action)

    def setUp(self):
        self.user = User.objects.create_superuser('jacob', 'jacob@example.com', 'secret')
        self.client = Client()
        self.client.login(username='jacob', password='secret')

    def test_location_create(self):
        """
        Test that a location can be created via an AJAX POST request.
        Test that a location can't be created without a name.
        """
        self.ajax_post_test({'name': 'Test Location'}, reverse('location_create'), 'redirect')
        self.ajax_post_test({}, reverse('location_create'), 'display')

    def test_person_create(self):
        """
        Test that a person can be created via an AJAX POST request.
        Test that a person can't be created without a name.
        """
        self.ajax_post_test({'name': 'Test Person'}, reverse('person_create'), 'redirect')
        self.ajax_post_test({}, reverse('person_create'), 'display')
