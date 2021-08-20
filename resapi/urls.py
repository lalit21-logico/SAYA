"""demo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'sah_user', views.sah_userViewSet)
router.register(r'sah_area_manager', views.sah_area_managerViewSet)
router.register(r'sah_service_provider', views.sah_service_providerViewSet)
router.register(r'user_wallet', views.user_walletViewSet)
router.register(r'service', views.serviceViewSet)
router.register(r'cartlist', views.cartlistViewSet)
router.register(r'transaction', views.transactionViewSet)
router.register(r'otp_authentication', views.otp_authenticationViewSet)
router.register(r'state_list', views.state_listViewSet)
router.register(r'district_list', views.district_listViewSet)
router.register(r'contact_us', views.contact_usViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
    

]