from django.conf.urls import url
from django.urls import include
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view

from events import views

router = DefaultRouter()
router.register(r'events', views.EventViewSet)

schema_view = get_schema_view(title='Betting Page API')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^schema/$', schema_view),
]
