from django.conf import settings
from django.db import models


class Bet(models.Model):
    event_participant = models.ForeignKey('events.EventsParticipant', on_delete=models.CASCADE, related_name='bets')
    amount = models.DecimalField(decimal_places=5, max_digits=15, help_text='(How much do you bet)')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


