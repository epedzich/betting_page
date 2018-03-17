from django.conf import settings
from django.db import models
from django.utils import timezone


class Operation(models.Model):
    date = models.DateTimeField(default=timezone.now)
    change = models.DecimalField(max_digits=15, decimal_places=5)
    wallet = models.ForeignKey('Wallet', on_delete=models.CASCADE, related_name='operations')
    bet = models.ForeignKey('betting.Bet', on_delete=models.CASCADE, related_name='operations')


class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
