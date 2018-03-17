from time import sleep

from django.db import models
import requests
from django.db.models import Sum

from django.urls import reverse
from django.utils import timezone
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel


class EventsParticipant(models.Model):
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE)
    participant = models.ForeignKey('Participant', on_delete=models.CASCADE)
    is_winner = models.BooleanField(default=False)

    class Meta:
        unique_together = ['event', 'participant']


class Category(MPTTModel):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=255)
    parent = TreeForeignKey('self', related_name='children', db_index=True, null=True, blank=True,
                            on_delete=models.PROTECT)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('events:category_detail', args=[str(self.pk)])

    class Meta:
        verbose_name_plural = "categories"


class Event(models.Model):
    oh_pk = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    start = models.DateTimeField(default=timezone.now)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)

    Active = 'active'
    Finished = 'finished'
    Resolved = 'resolved'
    STATUS_CHOICES = (
        (Active, 'active'),
        (Finished, 'finished'),
        (Resolved, 'resolved'),
    )
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=Active)

    @classmethod
    def populate(cls):

        count = 0
        current_link = 'https://www.onehash.com/api/events/?limit=30'
        while count <= 6:
            r = requests.get(current_link)
            json_data = r.json()
            events_data = json_data['results']

            for event_data in events_data:
                cls.populate_inner(event_data)
            current_link = json_data['next'] if 'next' in json_data else None
            count += 1

            sleep(0.5)

    @classmethod
    def populate_inner(cls, event_data):
        prev_category = None
        for category_level in event_data['categories']:
            prev_category, created = Category.objects.get_or_create(
                slug=category_level['slug'],
                defaults=dict(parent=prev_category,
                              name=category_level['name']))

        event, created = Event.objects.get_or_create(
            oh_pk=event_data['pk'],
            defaults=dict(name=event_data['name'],
                          start=event_data['start'],
                          category=prev_category))

        for option in event_data['main_bet_type']['options']:
            participant, created = Participant.objects.update_or_create(
                participant_no=option['participant'],
                defaults=dict(name=option['name'],
                              image='https://www.onehash.com' + option['image'] if option['image'] else ''))
            EventsParticipant.objects.update_or_create(participant=participant, event=event)

    @classmethod
    def update_status(cls):
        changed_events = Event.objects.filter(start__lt=timezone.now(), status=Event.Active)
        for event in changed_events:
            r = requests.get(f'https://www.onehash.com/api/events/{event.oh_pk}')
            if r.status_code != 200:
                continue
            json_data = r.json()
            status = json_data['status']
            if status != 'active':
                event.status = 'finished'

            for option in json_data['main_bet_type']['options']:
                if option['won'] == True:
                    event.eventsparticipant_set.filter(participant__participant_no=option['participant']).update(
                        is_winner=True)

            lost_amount = event.eventsparticipant_set.filter(is_winner=False).aggregate(lost=Sum('bets__amount'))[
                'lost']

            winner = event.eventsparticipant_set.filter(is_winner=True).annotate(inbank=Sum('bets__amount')).first()
            if winner:
                event.status = 'resolved'
                for bet in winner.bets.all():
                    user = bet.user
                    wallet = user.wallet
                    wallet.operations.create(change=bet.amount+(bet.amount/winner.inbank)*lost_amount, bet=bet)

            event.save()
            sleep(0.5)

    def get_absolute_url(self):
        return reverse('events:detail', args=[str(self.pk)])


class Participant(models.Model):
    event = models.ManyToManyField('events.Event', through='EventsParticipant', related_name='participants')
    name = models.CharField(max_length=255)
    participant_no = models.IntegerField(unique=True, blank=True, null=True)
    image = models.CharField(max_length=400)

    class Meta:
        ordering = ['name']
