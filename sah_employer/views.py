from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse
from Sah_User.models import *
from django.db.models import F
import random
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg, Max, Min, Sum


# Create your views here.

def home(request):

    return render(request,'Ehome.html',{'home':'active'})

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        data = sah_service_provider.objects.filter(email= email)
        counts = sah_service_provider.objects.filter(email= email).count()
        if counts == 1:
            data=data[0]
            if data.verification_status == 'disable':
                return render(request, 'Edisable.html',{'home':'active'})
            if data.password == request.POST['password']:
                request.session['Euser_id'] = data.service_provider_id
                request.session['Euser_email'] = data.email
                request.session['Euser_name'] = data.name
                return render(request, 'Ehome.html',{'home':'active'})
            else:
                msg = "email or Password invalid"
                return render(request, 'Elogin.html',{'login':'active','msg':msg,'email':email})
        else:
            msg = "email or Password invalid"
            return render(request, 'Elogin.html',{'login':'active','msg':msg,'email':email})
    else:
        return render(request,'Elogin.html',{'login':'active'})

def logout(request):
    try:
        request.session['Euser_id'] = None
        request.session['Euser_email'] = None
        request.session['Euser_name'] = None
        print('del')
    except KeyError:
        pass
    return home(request)

def contact(request):
    if verification(request):
        return render(request,'Elogin.html',{'login':'active'})
    if request.method == 'POST':
        user_id = request.session['Euser_id']
        user = sah_service_provider.objects.get(service_provider_id = user_id )
        email = user.email
        contact = user.mobile
        subject = request.POST['subject']
        message = request.POST['message']
        contact_us(subject=subject, message= message, user_email = email,user_contact=contact).save()
        msg = "compliment or complaint assigned succesfully"
        return render(request,'Econtact.html',{'contact':'active','msg':msg})
    return render(request,'Econtact.html',{'contact':'active'})


def myservices(request):
    if verification(request):
        return render(request,'Elogin.html',{'login':'active'})
    if request.method == 'POST':
       #this is farziiiii start
        email = request.POST['email']
        data = sah_service_provider.objects.filter(email= email)
        counts = sah_service_provider.objects.filter(email= email).count()
        #this is farziiiii end
    else:
        Euser_id = request.session['Euser_id']
        Euser_email = request.session['Euser_email']
        data1 = sah_service_provider.objects.get(service_provider_id=Euser_id)
        Estatus = data1.available_status
        data = service.objects.filter(service_provider_id__service_provider_id = Euser_id,service_provider_id__email = Euser_email).order_by('-service_id')
        return render(request,'Eservices.html',{'myservices':'active','data':data,'available_status':Estatus})

def addService(request):
    if verification(request):
        return render(request,'Elogin.html',{'login':'active'})
    if request.method == 'POST':
        service_name = request.POST['service_name']
        price = request.POST['price']
        information = request.POST['information']
        if service_name == None:
            msg = 'blank  service name invalid'
            return render(request,'Eaddservices.html',{'msg':msg,'myservices':'active','service_name':service_name,'price':price,'information':information})
        if price == None:
            msg = 'blank service price invalid'
            return render(request,'Eaddservices.html',{'msg':msg,'myservices':'active','service_name':service_name,'price':price,'information':information})
        if information == None:
            msg = 'blank discription number invalid'
            return render(request,'Eaddservices.html',{'msg':msg,'myservices':'active','service_name':service_name,'price':price,'information':information})
        x = random.randint(999,10000)
        try:
            files = request.FILES['myfile']
            files.name = 'img'+str(x)+files.name
            image = files
        except KeyError:
            image = None
        service_prov_ob = sah_service_provider.objects.get(email = request.session.get('Euser_email'))
        service(name_of_service = service_name,price = price, image = image, information = information, service_status = 'active', service_provider_id = service_prov_ob ).save()
        msg = 'add service succesfull'
        data = service.objects.filter(service_provider_id__email = request.session.get('Euser_email')).order_by('-service_id')
        return render(request,'Eservices.html',{'myservices':'active','data':data,'msg':msg})
    else:
        return render(request,'Eaddservices.html',{'myservices':'active'})

def serviceprofile(request):
    if verification(request):
        return render(request,'Elogin.html',{'login':'active'})
    if request.method == 'GET':
        service_id = request.GET['id']
        service_prov_email =  request.session.get('Euser_email')
        data = service.objects.filter( service_id = service_id, service_provider_id__email = service_prov_email)
        return render(request,'Eserviceprofile.html',{'data':data,'myservices':'active'})
    else:
        return HttpResponse("<h1>404 -- Not Found </h1>")

def service_status(request):
    if verification(request):
        return render(request,'Elogin.html',{'login':'active'})
    if request.method == 'GET':
        service_id = request.GET['id']
        E_email =  request.session.get('Euser_email')
        data = service.objects.get( service_id = service_id, service_provider_id__email = E_email)
        if data.service_status == 'active':
            service.objects.filter( service_id = service_id, service_provider_id__email = E_email).update(service_status = 'disable')
            msg = 'service deativated'
        if data.service_status == 'disable':
            service.objects.filter( service_id = service_id, service_provider_id__email = E_email).update(service_status = 'active')
            msg = 'service Activated'
        data = service.objects.filter( service_id = service_id, service_provider_id__email = E_email)
        return render(request,'Eserviceprofile.html',{'data':data,'msg':msg,'myservices':'active'})
    else:
        return HttpResponse("<h1>404 -- Not Found </h1>")

def changestatus(request):
    if verification(request):
        return render(request,'Elogin.html',{'login':'active'})
    Euser_id =  request.session.get('Euser_id')
    data = sah_service_provider.objects.get( service_provider_id = Euser_id)
    if data.available_status == 'active':
        sah_service_provider.objects.filter( service_provider_id = Euser_id).update(available_status = 'disable')
        msg1 = 'service deativated'
    if data.available_status == 'disable':
        sah_service_provider.objects.filter( service_provider_id = Euser_id).update(available_status = 'active')
        msg1 = 'service Activated'
    Euser_id = request.session['Euser_id']
    Euser_email = request.session['Euser_email']
    data1 = sah_service_provider.objects.get(service_provider_id=Euser_id)
    Estatus = data1.available_status
    data = service.objects.filter(service_provider_id__service_provider_id = Euser_id,service_provider_id__email = Euser_email).order_by('-service_id')
    return render(request,'Eservices.html',{'myservices':'active','data':data,'available_status':Estatus,'msg1':msg1})


def bids(request):
    if verification(request):
        return render(request,'Elogin.html',{'login':'active'})
    return render(request,'Elivebid.html')

def myorders(request):
    if verification(request):
        return render(request,'Elogin.html',{'login':'active'})
    if request.method == 'POST':
        data = transaction.objects.filter(service_provider_id = request.session['Euser_id'],payment_status='success').order_by('-txn_id')
        data =list(data.values())
        return JsonResponse({'data':data})
    data = transaction.objects.filter(service_provider_id = request.session['Euser_id'],payment_status='success').order_by('-txn_id')
    if request.session.get('Enotification') != None:
        request.session['Enotification'] = None
    return render(request,'Emyorders.html',{'myorders':'active','data':data})
   #implementation of my order here

def orderdetail(request):
    if verification(request):
        return render(request,'Elogin.html',{'login':'active'})
    if request.method == 'GET':
        txnid = request.GET['id']
        data = transaction.objects.filter(txnid =txnid)
        user = data[0]
        user_id = user.user_id
        user_data = sah_user.objects.filter(user_id = user_id)
        if data.count() == 1:
            return render(request, 'Eorderdetail.html', {'order_status': 'active','data': data,'user_data':user_data})

def completed(request):
    if verification(request):
        return render(request,'Elogin.html',{'login':'active'})
    if request.method == 'POST':
        txnid= request.POST['txnid']
        service_provider_id = request.session['Euser_id']
        check  = transaction.objects.get(txnid = txnid)
        if check.order_status == 'initiated':
            transaction.objects.filter(txnid = txnid,service_provider_id__service_provider_id = service_provider_id).update(order_status = 'completed')
            data = transaction.objects.filter(txnid =txnid)
            user = data[0]
            user_id = user.user_id
            wallet_data = user_wallet.objects.get(user_id__user_id= user_id)
            wallet_cash = wallet_data.wallet_cash
            if wallet_cash == None:
                wallet_cash = 0
            wallet_amount = int(user.amount_sah/3)+int(wallet_cash)
            user_wallet.objects.filter(user_id__user_id = user_id).update(wallet_cash=wallet_amount)
            user_data = sah_user.objects.filter(user_id = user_id)
            if data.count() == 1:
                return render(request, 'Eorderdetail.html', {'order_status': 'active','data': data,'user_data':user_data})

def myearning(request):
    if verification(request):
        return render(request,'Elogin.html',{'login':'active'})
    Euser_id = request.session['Euser_id']
    email = request.session['Euser_email']
    Earntoday = transaction.objects.filter(service_provider_id__service_provider_id = Euser_id,order_status='completed', payment_status='success', created_at__gte=timezone.now() - timedelta(1)).aggregate(Sum('amount_service'))
    Earnmonth = transaction.objects.filter(service_provider_id__service_provider_id = Euser_id,order_status='completed', payment_status='success', created_at__gte=timezone.now() - timedelta(29)).aggregate(Sum('amount_service'))
    Earnyear = transaction.objects.filter(service_provider_id__service_provider_id = Euser_id,order_status='completed', payment_status='success', created_at__gte=timezone.now() - timedelta(364)).aggregate(Sum('amount_service'))
    Earntotal = transaction.objects.filter(service_provider_id__service_provider_id = Euser_id,order_status='completed', payment_status='success').aggregate(Sum('amount_service'))
    Earntoday =Earntoday.get('amount_service__sum')
    Earnmonth =Earnmonth.get('amount_service__sum')
    Earntotal =Earntotal.get('amount_service__sum')
    Earnyear =Earnyear.get('amount_service__sum')
    if Earntoday == None:
         Earntoday = 0
    if Earnmonth == None:
         Earnmonth = 0
    if Earntotal == None:
         Earntotal = 0
    if Earnyear == None:
         Earnyear = 0
    return render(request,'Emyearning.html',{'myearning':'active','Earntoday':Earntoday,'Earnmonth':Earnmonth ,'Earntotal':Earntotal,'Earnyear':Earnyear})
  #set

def verification(request):
    if request.session.get('Euser_id') != None:
        Euser_id = request.session['Euser_id']
        email = request.session['Euser_email']
        if Euser_id == None:
            return render(request, 'Elogin.html',{'login':'active'})
        data = sah_service_provider.objects.get(service_provider_id = Euser_id)
        if data.verification_status == 'disable':
            return logout(request)
        if data.email == email:
            return False
    else:
        return True
