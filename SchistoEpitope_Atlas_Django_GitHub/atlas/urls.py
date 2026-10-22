from django.urls import path
from . import views

app_name = "atlas"
urlpatterns = [
    path("", views.home, name="home"),
    path("atlas/<slug:host>/", views.host_explorer, name="host_explorer"),
    path("atlas/rhesus/<slug:study>/", views.rhesus_explorer, name="rhesus_explorer"),
]
