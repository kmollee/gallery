import json

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from .models import Location

class SuperusreViews(TestCase):

    def ajax_post(self, url, form_data):
        response = self.client.post(
            url, form_data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        return json.loads(response.content.decode("utf-8"))

    def setUp(self):
        # create a superuser so that we can test create/update
        self.user = User.objects.create_superuser(
            'jacob', 'jacob@example.com', 'secret')
        self.client = Client()
        self.client.login(username='jacob', password='secret')

    def test_location(self):
        """
        Test the following location workflow:
        - Create invalid location (fails).
        - Create a valid location.
        - View the location list and make sure it's there.
        - View the location.
        - Rename the location.
        - Delete the location.
        """
        # create invalid location, display form again
        result = self.ajax_post(reverse('location_create'), {'name': ''})

        # create valid location, redirects
        result = self.ajax_post(reverse('location_create'), {'name': 'test location'})
        self.assertTrue('url' in result)
        location_url = result['url']

        # location list
        response = self.client.get(reverse('locations'))
        self.assertTrue('location_list' in response.context)
        self.assertTrue('paginator' in response.context)
        first_location = response.context['location_list'][0]
        self.assertEqual(first_location.get_absolute_url(), location_url)

        # location detail
        response = self.client.get(result['url'])
        self.assertEqual(response.status_code, 200)
        self.assertTrue('location' in response.context)
        self.assertTrue('paginator' in response.context)
        self.assertTrue('back_link' in response.context)
        self.assertTrue('album_list' in response.context)

        # rename valid location, redirects
        result = self.ajax_post(reverse('location_rename', args=[1, ]), {'name': 'new location'})
        self.assertTrue('url' in result)

        # rename invalid location, display form again
        result = self.ajax_post(reverse('location_rename', args=[1, ]), {'name': ''})
        self.assertTrue('html' in result)

        # delete location
        result = self.ajax_post(reverse('location_delete', args=[1, ]), {'submit': True})
        self.assertTrue('url' in result)

    def test_person(self):
        """
        Test the following person workflow:
        - Create invalid person (fails).
        - Create a valid person.
        - View the person list and make sure it's there.
        - View the person.
        - Rename the person.
        - Delete the person.
        """
        # create invalid person, display form again
        result = self.ajax_post(reverse('person_create'), {'name': ''})

        # create valid person, redirects
        result = self.ajax_post(reverse('person_create'), {'name': 'test person'})
        self.assertTrue('url' in result)
        person_url = result['url']

        # person list
        response = self.client.get(reverse('people'))
        self.assertTrue('person_list' in response.context)
        self.assertTrue('paginator' in response.context)
        first_person = response.context['person_list'][0]
        self.assertEqual(first_person.get_absolute_url(), person_url)

        # person detail
        response = self.client.get(result['url'])
        self.assertEqual(response.status_code, 200)
        self.assertTrue('person' in response.context)
        self.assertTrue('paginator' in response.context)
        self.assertTrue('back_link' in response.context)
        self.assertTrue('photo_list' in response.context)

        # rename valid person, redirects
        result = self.ajax_post(reverse('person_rename', args=[1, ]), {'name': 'new person'})
        self.assertTrue('url' in result)

        # rename invalid person, display form again
        result = self.ajax_post(reverse('person_rename', args=[1, ]), {'name': ''})
        self.assertTrue('html' in result)

        # delete person
        result = self.ajax_post(reverse('person_delete', args=[1, ]), {'submit': True})
        self.assertTrue('url' in result)

    def test_album(self):
        """
        Test the following album workflow:
        - Create invalid album (fails).
        - Create a valid album.
        - View the album list and make sure it's there.
        - View the album.
        - Edit the album.
        - Delete the album.
        """
        # create invalid album, display form again
        result = self.ajax_post(reverse('album_create'), {'name': ''})

        # create valid album, redirects
        result = self.ajax_post(reverse('album_create'), {'name': 'test album'})
        self.assertTrue('url' in result)
        album_url = result['url']

        # album list
        response = self.client.get(reverse('albums'))
        self.assertTrue('album_list' in response.context)
        self.assertTrue('paginator' in response.context)
        first_album = response.context['album_list'][0]
        self.assertEqual(first_album.get_absolute_url(), album_url)

        # album detail
        response = self.client.get(result['url'])
        self.assertEqual(response.status_code, 200)
        self.assertTrue('album' in response.context)
        self.assertTrue('paginator' in response.context)
        self.assertTrue('back_link' in response.context)
        self.assertTrue('photo_list' in response.context)

        # edit valid album, redirects
        result = self.ajax_post(reverse('album_edit', args=[1, ]), {'name': 'new album'})
        self.assertTrue('url' in result)

        # edit invalid album, display form again
        result = self.ajax_post(reverse('album_edit', args=[1, ]), {'name': ''})
        self.assertTrue('html' in result)

        # delete album
        result = self.ajax_post(reverse('album_delete', args=[1, ]), {'submit': True})
        self.assertTrue('url' in result)
