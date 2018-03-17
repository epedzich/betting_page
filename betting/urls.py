from django.urls import path

from betting import views

app_name = 'betting'

urlpatterns = [
    path('bet_on/<int:event_participant_id>', views.BetCreateView.as_view(), name='create'),

]