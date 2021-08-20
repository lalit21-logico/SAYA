from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from Sah_User.models import *
from django.db.models import F
import random
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg, Max, Min, Sum
from rest_framework import viewsets
from .serializers import *

class sah_userViewSet(viewsets.ModelViewSet):
    queryset = sah_user.objects.all()
    serializer_class = sah_userSerializer

class sah_area_managerViewSet(viewsets.ModelViewSet):
    queryset = sah_area_manager.objects.all()
    serializer_class = sah_area_managerSerializer

class sah_service_providerViewSet(viewsets.ModelViewSet):
    queryset = sah_service_provider.objects.all()
    serializer_class = sah_service_providerSerializer

class user_walletViewSet(viewsets.ModelViewSet):
    queryset = user_wallet.objects.all()
    serializer_class = user_walletSerializer

class serviceViewSet(viewsets.ModelViewSet):
    queryset = service.objects.all()
    serializer_class = serviceSerializer

class cartlistViewSet(viewsets.ModelViewSet):
    queryset = cartlist.objects.all()
    serializer_class = cartlistSerializer

class transactionViewSet(viewsets.ModelViewSet):
    queryset = transaction.objects.all()
    serializer_class = transactionSerializer

class otp_authenticationViewSet(viewsets.ModelViewSet):
    queryset = otp_authentication.objects.all()
    serializer_class = otp_authenticationSerializer

class state_listViewSet(viewsets.ModelViewSet):
    queryset = state_list.objects.all()
    serializer_class = state_listSerializer

class district_listViewSet(viewsets.ModelViewSet):
    queryset = district_list.objects.all()
    serializer_class = district_listSerializer

class contact_usViewSet(viewsets.ModelViewSet):
    queryset = contact_us.objects.all()
    serializer_class = contact_usSerializer