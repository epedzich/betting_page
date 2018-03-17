import requests
from django.test import TestCase

from .models import Event


class MyTests(TestCase):

    def test1(self):
        r = requests.get('https://www.onehash.com/api/events/?limit=30')
        json_data = r.json()
        events_data = json_data['results']

        for event in events_data:
            Event.objects.create(oh_pk=event['pk'], name=event['name'])
        print(Event.objects.all().values())
