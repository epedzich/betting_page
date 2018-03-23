from django.db.models import Sum, Prefetch
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from accounts.models import Wallet, Operation
from . import forms


class SignUp(CreateView):
    form_class = forms.UserCreateForm
    success_url = reverse_lazy('login')
    template_name = 'accounts/signup.html'


class WalletInfo(TemplateView):
    template_name = 'accounts/wallet.html'

    def get_context_data(self, **kwargs):
        ctx = super(WalletInfo, self).get_context_data(**kwargs)
        ctx['wallet'] = Wallet.objects.annotate(balance=Sum('operations__change')).prefetch_related(
            Prefetch('operations', queryset=Operation.objects.all().order_by('-date').select_related(
                'bet__event_participant__participant', 'bet__event_participant__event'))).get(user=self.request.user)
        return ctx
