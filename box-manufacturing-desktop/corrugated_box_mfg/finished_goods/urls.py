from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'finished_goods'

urlpatterns = [
    # Base URL redirect
    path('', RedirectView.as_view(pattern_name='finished_goods:box-list'), name='index'),
    
    # Box template URLs
    path('boxes/', views.BoxListView.as_view(), name='box-list'),
    path('boxes/create/', views.BoxCreateView.as_view(), name='box-create'),
    path('boxes/<int:pk>/', views.BoxDetailView.as_view(), name='box-detail'),
    path('boxes/<int:pk>/update/', views.BoxUpdateView.as_view(), name='box-update'),
    path('boxes/search/', views.search_box_template, name='box-search'),
    
    # Order URLs
    path('orders/', views.BoxOrderListView.as_view(), name='order-list'),
    path('orders/create/', views.BoxOrderCreateView.as_view(), name='order-create'),
    path('orders/<int:pk>/', views.BoxOrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:order_id>/update-status/', views.update_order_status, name='update-order-status'),
    
    # API endpoints
    path('api/suggestions/', views.get_field_suggestions, name='field-suggestions'),
    path('calculations/', views.get_box_calculations, name='calculations'),
    path('calculate-requirements/', views.calculate_order_requirements, name='calculate-requirements'),
]
