from django.shortcuts import render
from django.urls import reverse
from django.views.generic import CreateView
from betting.models import Bet
from events.models import EventsParticipant


class BetCreateView(CreateView):
    model = Bet
    template_name = 'betting/create.html'
    fields = ['amount']

    def form_valid(self, form):
        user = self.request.user
        wallet = user.wallet
        self.object: Bet = form.save(commit=False)
        bet = self.object
        bet.user = user
        bet.event_participant_id = self.kwargs['event_participant_id']
        bet.save()
        wallet.operations.create(
            change=-bet.amount,
            bet=bet,
        )
        return super().form_valid(form)

    def get_success_url(self):
        ep = EventsParticipant.objects.get(pk=self.kwargs['event_participant_id'])
        return reverse('events:detail', kwargs=dict(pk=ep.event_id))
