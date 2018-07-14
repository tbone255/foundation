from django.contrib import admin
from django.urls import path, include

from rest_framework import routers

from inputter.views import InputterViewSet

router = routers.DefaultRouter()
router.register(r'inputtest', InputterViewSet)

urlpatterns = [
	path(r'api/', include(router.urls)),
    path('admin/', admin.site.urls),
]
