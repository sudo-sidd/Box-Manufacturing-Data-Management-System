from django.urls import path
from .views import add_inventory, inventory_overview, inventory_home,get_presets

urlpatterns = [
    path("", inventory_home, name="inventory_home"),  # ✅ Home page route
    path("add/", add_inventory, name="add_inventory"),
    path("overview/", inventory_overview, name="inventory_overview"),
    path("get-presets/", get_presets, name="get_presets")

]
