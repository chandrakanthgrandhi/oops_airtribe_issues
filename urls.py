from django.urls import path

from issues import views

urlpatterns = [
    path('api/reporters/', views.reporters, name='reporters'),
    path('api/issues/', views.issues, name='issues'),
]
