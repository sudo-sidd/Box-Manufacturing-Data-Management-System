from django.urls import path
from . import views

app_name = 'finished_goods'

urlpatterns = [
    path('', views.BoxListView.as_view(), name='box-list'),
    path('create/', views.BoxCreateView.as_view(), name='box-create'),
    path('<int:pk>/', views.BoxDetailView.as_view(), name='box-detail'),
    path('<int:pk>/edit/', views.BoxUpdateView.as_view(), name='box-update'),
    path('api/suggestions/', views.get_field_suggestions, name='field-suggestions'),
    path('calculations/', views.get_box_calculations, name='box-calculations'),
]
