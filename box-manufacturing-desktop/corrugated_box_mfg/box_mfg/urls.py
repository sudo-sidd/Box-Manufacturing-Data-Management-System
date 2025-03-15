from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from inventory.views import inventory_home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', inventory_home, name='home'),
    path('inventory/', include('inventory.urls')),
    path('finished-goods/', include('finished_goods.urls', namespace='finished_goods')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
