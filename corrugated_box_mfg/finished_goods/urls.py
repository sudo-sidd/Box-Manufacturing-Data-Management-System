from django.urls import path
from . import views

app_name = 'finished_goods'

urlpatterns = [
    # Box Template URLs
    path('', views.BoxListView.as_view(), name='box-list'),
    path('template/create/', views.BoxCreateView.as_view(), name='box-create'),
    path('template/<int:pk>/', views.BoxDetailView.as_view(), name='box-detail'),
    path('template/<int:pk>/edit/', views.BoxUpdateView.as_view(), name='box-update'),
    
    # Order URLs
    path('orders/', views.BoxOrderListView.as_view(), name='order-list'),
    path('orders/new/', views.BoxOrderCreateView.as_view(), name='order-create'),
    path('orders/<int:pk>/', views.BoxOrderDetailView.as_view(), name='order-detail'),
    
    # API URLs
    path('api/suggestions/', views.get_field_suggestions, name='field-suggestions'),
    path('api/calculations/', views.get_box_calculations, name='box-calculations'),
    path('api/order/calculate/', views.calculate_order_requirements, name='calculate-requirements'),
]
