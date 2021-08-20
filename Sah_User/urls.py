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

urlpatterns = [
    path('',views.home,name='home page'),
    path('login',views.login),
    path('Enotify',views.Enotify,name='Enotify'),
    path('Mnotify',views.Mnotify,name='Mnotify'),
    path('signup',views.signup),
    path('logout',views.logout),
    path('contact',views.contact),
    path('salon',views.salon),
    path('wallet',views.wallet),
    path('rating',views.rating,name='rating'),
    path('getservice',views.getservice),
    path('cartlistr',views.cartlistr,name='cartlistr'),
    path('cartlistrRemove',views.cartlistrRemove,name='cartlistrRemove'),
    path('placeorder',views.placeorder),
    path('orderdetail',views.orderdetail),
    path('pinset',views.pinset),
    path('order_status',views.orderList),
    path('type_salon',views.type_salon),
    path('payu_checkout',views.payu_checkout,name='payu_checkout'),
    path('payu_success',views.payu_success,name='payu_success'),
    path('payu_failure',views.payu_failure,name='payu_failure'),
    path('forgotPassword',views.forgotPassword,name='forgotPassword'),
    path('getotp',views.getotp,name='getotp'),
    ############### admin area
    path('alogin',views.alogin),
    path('alogout',views.alogout),
    path('admin_home',views.admin_home,name='admin_home'),
    path('adminWidgets',views.adminWidgets,name='adminWidgets'),
    path('adminPanel',views.adminPanel,name='adminPanel'),
    path('addManager',views.addManager,name='addManager'),
    path('admin_get_live_data',views.admin_get_live_data,name='admin_get_live_data'),
    path('addDistrict',views.addDistrict,name='addDistrict'),
    path('ongoingOrders',views.ongoingOrders,name='ongoingOrders'),
    path('userCount',views.userCount,name='userCount'),
    ############ android urls.
    path('hash_genrator',views.hash_genrator,name='hash_genrator'),
    path('hash_response',views.hash_response,name='hash_response'),
    path('cartlistAdd',views.cartlistAdd,name='cartlistAdd'),
    path('cartlistRemove',views.cartlistRemove,name='cartlistRemove'),
    path('signupAndroid',views.signupAndroid,name='signupAndroid'),
    path('loginAndroid',views.loginAndroid,name='loginAndroid'),
    path('logoutAndroid',views.logoutAndroid,name='logoutAndroid'),
    path('forgotPasswordAndroid',views.forgotPasswordAndroid,name='forgotPasswordAndroid'),
    path('otpAndroid',views.otpAndroid,name='otpAndroid'),
    path('contactAndroid',views.contactAndroid,name='contactAndroid'),
    path('walletAndroid',views.walletAndroid,name='walletAndroid'),
    path('orderListAndroid',views.orderListAndroid,name='orderListAndroid'),
    path('getserviceAndroid',views.getserviceAndroid,name='getserviceAndroid'),
    path('orderdetailAndroid',views.orderdetailAndroid,name='orderdetailAndroid'),
    path('getcartAndroid',views.getcartAndroid,name='getcartAndroid'),
    path('ratingAndroid',views.ratingAndroid,name='ratingAndroid'),
    path('getSalonAndroid',views.getSalonAndroid,name='getSalonAndroid'),

]

handler404 = views.handler404
handler500 = views.handler500