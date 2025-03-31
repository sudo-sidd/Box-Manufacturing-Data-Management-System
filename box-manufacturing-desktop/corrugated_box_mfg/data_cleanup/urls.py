from django.urls import path
from . import views

app_name = 'data_cleanup'

urlpatterns = [
    path('', views.cleanup_dashboard, name='dashboard'),
    path('clear-inventory/', views.clear_inventory, name='clear_inventory'),
    path('clear-orders/', views.clear_orders, name='clear_orders'),
    path('clear-templates/', views.clear_templates, name='clear_templates'),
    path('clear-all/', views.clear_all, name='clear_all'),
]