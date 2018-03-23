from typing import List

from django.db.models import Q, Sum, Count, Prefetch
from django.db.models.functions import Coalesce
from django.views.generic import ListView, DetailView
from rest_framework import viewsets, permissions

from events.models import Event, Category, EventsParticipant
from events.permissions import IsOwnerOrReadOnly
from events.serializers import EventSerializer


class EventsListView(ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'all_events'

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.GET.get('archive', None) == 'true':
            return qs.filter(status__in=['finished', 'resolved'])
        else:
            return qs.filter(status='active')

    ordering = ['-start']


class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    queryset = Event.objects.annotate(
        inbank=Coalesce(Sum('eventsparticipant__bets__amount'), 0),
        bets_count=Count('eventsparticipant__bets')
    ).prefetch_related(
        Prefetch('eventsparticipant_set',
                 queryset=EventsParticipant.objects.annotate(
                     inbank=Coalesce(Sum('bets__amount'), 0),
                     bets_count=Count('bets')
                 ).select_related('participant'),
                 to_attr='options')
    ).select_related('category__parent__parent')


class CategoryListView(ListView):
    model = Category
    template_name = 'events/category_list.html'
    context_object_name = 'all_categories'


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'events/category_detail.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # w self.kwargs znajduja sie te argumenty z URLi
        pk = self.kwargs['pk']
        for_category_q = Q(category_id=pk) | Q(category__parent_id=pk) | Q(category__parent__parent_id=pk)
        ctx['events']: List[Event] = list(Event.objects.filter(
            for_category_q
        ))
        ctx['active_count'] = Event.objects.filter(
            for_category_q,
            status='active',
        ).count()
        ctx['finished_count'] = Event.objects.filter(
            for_category_q,
            status='finished',
        ).count()

        return ctx


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)
