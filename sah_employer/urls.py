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

from django.urls import path
from . import views
from django.conf import settings 
from django.conf.urls.static import static

urlpatterns = [
    path('',views.home,name='home page'),
    path('login',views.login),
    path('logout',views.logout),
    path('contact',views.contact),
    path('livebids',views.bids),
    path('myearning',views.myearning),   
    path('myservices',views.myservices), 
    path('addService',views.addService), 
    path('serviceprofile',views.serviceprofile), 
    path('service_status',views.service_status),
    path('myorders',views.myorders,name='myorders'), 
    path('orderdetail',views.orderdetail,name ='orderdetail'), 
    path('completed',views.completed), 
    path('changestatus',views.changestatus), 
    
]

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)
