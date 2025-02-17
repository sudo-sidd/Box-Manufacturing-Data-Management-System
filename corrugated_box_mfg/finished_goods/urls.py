from django.urls import path
from .views import add_box_order

urlpatterns = [
    path('add/', add_box_order, name='add_box_order'),
]
