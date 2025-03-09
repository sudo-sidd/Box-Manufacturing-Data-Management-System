from django.urls import path
from .views import add_inventory, inventory_overview, inventory_home, get_presets
from . import views

urlpatterns = [
    path("", inventory_home, name="inventory_home"),  # ✅ Home page route
    path("add/", add_inventory, name="add_inventory"),
    path("overview/", inventory_overview, name="inventory_overview"),
    path("get-presets/", get_presets, name="get_presets"),
    path('delete/<str:model_name>/<int:item_id>/', views.delete_inventory, name='delete_inventory'),
    path('edit/<str:model_name>/<int:item_id>/', views.edit_inventory, name='edit_inventory'),
]
