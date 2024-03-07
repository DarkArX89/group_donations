from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views

from .views import PaymentViewSet, CollectViewSet

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register('collects', CollectViewSet, basename='collects')
router_v1.register(r'collects/(?P<collect_id>\d+)/payments', PaymentViewSet,
                   basename='payments')

urlpatterns = [
    path('v1/get-token/', views.obtain_auth_token),
    path('v1/', include(router_v1.urls))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
