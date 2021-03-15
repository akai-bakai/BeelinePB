from django.urls import path
from .views import *

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('category/<str:slug>/', CategoryDetailView.as_view(), name='category'),
    path('person-detail/<int:pk>/', PersonDetailView.as_view(), name='detail'),
    path('add-person/', add_person, name='add-person'),
    path('update-person/<int:pk>/', update_person, name='update-person'),
    path('delete-person/<int:pk>/', DeletePersonView.as_view(), name='delete-person'),
]
