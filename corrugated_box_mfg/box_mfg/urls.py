from django.contrib import admin
from django.urls import path, include
from inventory.views import inventory_home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', inventory_home, name='home'),
    path('inventory/', include('inventory.urls')),
]
