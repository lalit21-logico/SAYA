from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse
from Sah_User.models import *
import random
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg, Max, Min, Sum
from django.core.mail import send_mail
from SAH.settings import EMAIL_HOST_USER


#payment gateway
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
# Import Payu from Paywix
from paywix.payu import Payu

payu_config = settings.PAYU_CONFIG
merchant_key = payu_config.get('merchant_key')
merchant_salt = payu_config.get('merchant_salt')
surl = payu_config.get('success_url')
furl = payu_config.get('failure_url')
mode = payu_config.get('mode')
payu = Payu(merchant_key, merchant_salt, surl, furl, mode)

# Payu checkout page
@csrf_exempt
def payu_checkout(request):
    if verification(request):
        return render(request,'login.html',{'login':'active'})
    user_id = request.session['user_id']
    user_data = sah_user.objects.filter(user_id = user_id)
    user_data = user_data[0]
    cartlist_data = cartlist.objects.filter(user_id = user_id)
    totalprice = 0
    cart_details = ''
    order_data =''
    for d in cartlist_data:
        totalprice = totalprice + d.service_id.price
        cart_details += 'services-'+str(d.service_id.name_of_service)+' '
        order_data += str(d.service_id.name_of_service)+' at price'+str(d.service_id.price)+',\n'
        service_provider_id = d.service_provider_id
    paynow = int((totalprice/100)*30)
    paylater = int((totalprice/100)*70)
    wallet_data  = user_wallet.objects.get(user_id__user_id = user_id)
    if int(wallet_data.wallet_cash) >= 200:
        paynow = 1
    cartlist_data = cartlist_data[0]
    service_provider_id = cartlist_data.service_provider_id
    count = sah_service_provider.objects.filter(service_provider_id = service_provider_id ,verification_status='active',available_status='active').count()
    if count == 0:
        return render(request, 'UMasterstatus.html')

    data = { 'amount': str(paynow), 'firstname': user_data.user_name,
        'email': user_data.email,
        'phone': user_data.mobile, 'productinfo': cart_details,
        'lastname': 'service_provider_id'+str(service_provider_id), 'address1': user_data.address,
        'address2': 'test', 'city': user_data.district,
        'state': 'test', 'country': 'test',
        'zipcode': 'test', 'udf1': '',
        'udf2': '', 'udf3': '', 'udf4': '', 'udf5': ''
        }

        # No Transactio ID's, Create new with paywix, it's not mandatory
        # Create your own
        # Create transaction Id with payu and verify with table it's not existed
    txnid = str(random.randint(999,100000))+'us'+str(user_id)+'ct'+str(cartlist_data.temp_id)+'Sp'+str(service_provider_id)+'rd'+str(random.randint(999,100000))
    service_provider_data = sah_service_provider.objects.get(service_provider_id = service_provider_id)
    manger_id = service_provider_data.manager_id.manager_id
    transaction(txnid = txnid,amount_sah = paynow,amount_service= paylater,user_id=user_id,service_provider_id=service_provider_data,manager_id=manger_id,order_data=order_data,payment_status='initiate').save()
    data.update({"txnid": txnid})
    payu_data = payu.transaction(**data)
    return render(request, 'payu_checkout.html', {"posted": payu_data})

@csrf_exempt
def payu_success(request):
    data = {k: v[0] for k, v in dict(request.POST).items()}
    response = payu.verify_transaction(data)
    return_data = response["return_data"]
    amount = return_data["amount"]
    status = return_data["status"]
    txnid = return_data["txnid"]
    bank_ref_num = return_data["bank_ref_num"]
    phone = return_data["phone"]
    addedon = return_data["addedon"]

    print(amount)
    print(status)
    print(txnid)
    print(bank_ref_num)
    print(phone)
    print(addedon)
    order_status = models.CharField(max_length=10, null = False)
    transaction.objects.filter( txnid = txnid).update(payment_status = status ,bank_ref_num = str(bank_ref_num),addedon=addedon,order_status = "initiated")
    data = transaction.objects.get(txnid= txnid)
    user_id = data.user_id
    Euser_id = data.service_provider_id.service_provider_id
    #mail master
    subject = 'Order Recived .'
    message = 'Reciving new order check details on SAYA.'
    recepient = str(data.service_provider_id.email)
    send_mail(subject,message, EMAIL_HOST_USER, [recepient], fail_silently = False)
    wallet_data  = user_wallet.objects.get(user_id__user_id = user_id)
    if int(wallet_data.wallet_cash) >= 200:
        user_wallet.objects.filter(user_id__user_id = user_id).update(wallet_cash = 0)
        sah_service_provider.objects.filter(service_provider_id = Euser_id).update(manager_commision = 0)
    else:
        fmanager = sah_service_provider.objects.get(service_provider_id = Euser_id)
        manager_comission = fmanager.manager_commision
        if manager_comission == None:
            manager_comission = 0
        manager_comission = int(manager_comission)+int((float(amount)*4)/30)
        sah_service_provider.objects.filter(service_provider_id = Euser_id).update(manager_commision =manager_comission)
    #mail manager
    subject = 'Order Recived to your member .'
    message = 'Reciving new order to member ' +str(data.service_provider_id.name) + ' check details on SAYA.'
    recepient = str(data.service_provider_id.manager_id.email)
    send_mail(subject,message, EMAIL_HOST_USER, [recepient], fail_silently = False)
    data = transaction.objects.filter(user_id= user_id).exclude(payment_status = 'initiate').order_by('-txn_id')
    return render(request, 'Uorder_status.html', {"order_status": 'active','flashS': 'Payment-Success','data':data,'trans':'trans'})

@csrf_exempt
def payu_failure(request):
    data = {k: v[0] for k, v in dict(request.POST).items()}
    response = payu.verify_transaction(data)
    return_data = response["return_data"]
    amount = return_data["amount"]
    status = return_data["status"]
    txnid = return_data["txnid"]
    bank_ref_num = return_data["bank_ref_num"]
    phone = return_data["phone"]
    addedon = return_data["addedon"]
    print(amount)
    print(status)
    print(txnid)
    print(bank_ref_num)
    print(phone)
    print(addedon)
    transaction.objects.filter( txnid = txnid).update(payment_status = status ,bank_ref_num = str(bank_ref_num),addedon=addedon,order_status = "Payment failed")
    data = transaction.objects.get(txnid= txnid)
    user_id = data.user_id
    data = transaction.objects.filter(user_id= user_id).exclude(payment_status = 'initiate').order_by('-txn_id')
    return render(request, 'Uorder_status.html', {'order_status': 'active','flashF': 'Payment-failed','data':data,'trans':'trans'})

#############################

# Create your views here.


def home(request):
    if request.session.get('salon_type') != None:
        request.session['salon_type'] = None
    return render(request,'Uhome.html',{'home':'active'})

def Enotify(request):
    if request.session.get('Euser_id') == None:
        return JsonResponse({'data':0})
    Euser_id = request.session['Euser_id']
    count = transaction.objects.filter(service_provider_id__service_provider_id = Euser_id,payment_status= 'success' ,notify_master = None).count()
    if count >= 1:
        transaction.objects.filter(service_provider_id__service_provider_id = Euser_id,payment_status= 'success' ,notify_master = None).update(notify_master = 'yes')
        request.session['Enotification'] = count
    data = count
    return JsonResponse({'data':data})


def Mnotify(request):
    if request.session.get('Muser_id') == None:
        return JsonResponse({'data':0})
    Muser_id = request.session['Muser_id']
    count = transaction.objects.filter(service_provider_id__manager_id__manager_id= Muser_id, payment_status= 'success', order_status='initiated' ,notify_mannager = None).count()
    if count >= 1:
        transaction.objects.filter(service_provider_id__manager_id__manager_id = Muser_id, payment_status= 'success', order_status='initiated' ,notify_mannager = None).update(notify_mannager = 'yes')
        request.session['notification'] = count
    data = count
    return JsonResponse({'data':data})


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        data = sah_user.objects.filter(email= email)
        counts = sah_user.objects.filter(email= email).count()
        if counts == 1:
            data=data[0]
            if data.password == request.POST['password']:
                request.session['user_id'] = data.user_id
                request.session['user_email'] = data.email
                request.session['user_name'] = data.user_name
                return render(request, 'Uhome.html',{'home':'active'})
            else:
                msg = "email or Password invalid"
                return render(request, 'login.html',{'login':'active','msg':msg,'email':email})
        else:
            msg = "email or Password invalid"
            return render(request, 'login.html',{'login':'active','msg':msg,'email':email})
    else:
        return render(request,'login.html',{'login':'active'})

def signup(request):
    district_data = district_list.objects.all().order_by('district')
    if request.method == 'POST':
        user_name = request.POST['user_name']
        email = request.POST['email']
        mobile = request.POST['mobile']
        address = request.POST['address']
        gender = request.POST['gender']
        district = request.POST['district']
        password = request.POST['password']
        if user_name == None:
            msg = 'blank name invalid'
            return render(request,'signup.html',{'msg':msg,'signup':'active','user_name':user_name,'email':email,'mobile':mobile,'address':address,'gender':gender,'district':district, 'district_list':district_data})
        if email == None:
            msg = 'blank email invalid'
            return render(request,'signup.html',{'msg':msg,'signup':'active','user_name':user_name,'email':email,'mobile':mobile,'address':address,'gender':gender,'district':district, 'district_list':district_data})
        if mobile == None:
            msg = 'blank mobile number invalid'
            return render(request,'signup.html',{'msg':msg,'signup':'active','user_name':user_name,'email':email,'mobile':mobile,'address':address,'gender':gender,'district':district, 'district_list':district_data})
        if address == None:
            msg = ' address invalid'
            return render(request,'signup.html',{'msg':msg,'signup':'active','user_name':user_name,'email':email,'mobile':mobile,'address':address,'gender':gender,'district':district, 'district_list':district_data})
        if gender == None:
            msg = 'select gender'
            return render(request,'signup.html',{'msg':msg,'signup':'active','user_name':user_name,'email':email,'mobile':mobile,'address':address,'gender':gender,'district':district, 'district_list':district_data})
        if district == None:
            msg = 'select district'
            return render(request,'signup.html',{'msg':msg,'signup':'active','user_name':user_name,'email':email,'mobile':mobile,'address':address,'gender':gender,'district':district, 'district_list':district_data})
        if len(mobile) <= 9:
            msg = 'Mobile number not valid'
            return render(request,'signup.html',{'msg':msg,'signup':'active','user_name':user_name,'email':email,'mobile':mobile,'address':address,'gender':gender,'district':district, 'district_list':district_data})
        if len(password) <=  7:
            msg = 'Password too short!'
            return render(request,'signup.html',{'msg':msg,'signup':'active','user_name':user_name,'email':email,'mobile':mobile,'address':address,'gender':gender,'district':district, 'district_list':district_data})
        if password != request.POST['re_password']:
            msg = 'Password not match!'
            return render(request,'signup.html',{'msg':msg,'signup':'active','user_name':user_name,'email':email,'mobile':mobile,'address':address,'gender':gender,'district':district, 'district_list':district_data})
        emailcounts = sah_user.objects.filter(email= email).count()
        mobilecount = sah_user.objects.filter(mobile= mobile).count()
        if emailcounts == 1:
            msg = 'Email already exisit with other account!'
            return render(request,'signup.html',{'msg':msg,'signup':'active','user_name':user_name,'email':email,'mobile':mobile,'address':address,'gender':gender,'district':district, 'district_list':district_data})
        if mobilecount == 1:
            msg = 'Mobile number already exisit with other account!'
            return render(request,'signup.html',{'msg':msg,'signup':'active','user_name':user_name,'email':email,'mobile':mobile,'address':address,'gender':gender,'district':district, 'district_list':district_data})
        sah_user(user_name = user_name, email = email, mobile = mobile, address = address,gender = gender,district = district , password = password,wallet_id=None,email_verification=None).save()
        user_ob = sah_user.objects.get(email = email)
        user_wallet(wallet_cash = 0,user_id=user_ob).save()
        data = user_wallet.objects.get(user_id__email = email )
        sah_user.objects.filter(email = email).update(wallet_id = data.wallet_id)
        # subject = 'Welcome '+str(user_name)
        # message = 'Dear '+user_name+', we welcomes you get connect with us.'
        # recepient = str(email)
        # send_mail(subject,message, EMAIL_HOST_USER, [recepient], fail_silently = False)
        msg = 'Account created succesfully Now log in '
        return render(request, 'login.html',{'msg':msg,'login':'active', 'district_list':district_data})
    else:
        return render(request,'signup.html',{'signup':'active', 'district_list':district_data})

def logout(request):
    try:
        request.session['user_id'] = None
        request.session['user_email'] = None
        request.session['user_name'] = None
        request.session['salon_type'] = None
        print('del')
    except KeyError:
        pass
    return home(request)

def contact(request):
    if verification(request):
        return render(request,'login.html',{'login':'active'})
    if request.method == 'POST':
        user_id = request.session['user_id']
        user = sah_user.objects.get(user_id = request.session['user_id'] )
        email = user.email
        contact = user.mobile
        subject = request.POST['subject']
        message = request.POST['message']
        contact_us(subject=subject, message= message, user_email = email,user_contact=contact).save()
        msg = "compliment or complaint assigned succesfully"
        return render(request,'Ucontact.html',{'contact':'active','msg':msg})
    return render(request,'Ucontact.html',{'contact':'active'})

def salon(request):
    if verification(request):
        return render(request,'login.html',{'login':'active'})
    user = sah_user.objects.get(email = request.session['user_email'] )
    district = user.district
    if request.session.get('salon_type') == 'Male':
        data = sah_service_provider.objects.filter(verification_status='active',available_status='active',district = district).exclude(salontype = 'Female').order_by('?')
    if request.session.get('salon_type') == 'Female':
        data = sah_service_provider.objects.filter(verification_status='active',available_status='active',district = district).exclude(salontype = 'Male').order_by('?')
    if request.session.get('salon_type') == 'MehArt':
        data = sah_service_provider.objects.filter(verification_status='active',available_status='active',district = district, salontype='MehArt').order_by('?')
    if request.session.get('salon_type') == None:
        data = sah_service_provider.objects.filter(verification_status='active',available_status='active',district = district).order_by('?')
    return render(request,'Uservice.html',{'salon':'active','data':data})

def type_salon(request):
    if request.method == 'GET':
        salon_type = request.GET['id']
        request.session['salon_type'] = salon_type
        return salon(request)
    return salon(request)

def wallet(request):
    if verification(request):
        return render(request,'login.html',{'login':'active'})
    user_id = request.session['user_id']
    email = request.session['user_email']
    user_ob = sah_user.objects.get(email = email)
    if 1 == user_wallet.objects.filter(user_id =user_ob ).count():
        data = user_wallet.objects.get(user_id__user_id = user_id, user_id__email = email)
        wallet_cash = data.wallet_cash
        return render(request,'Uwallet.html',{'wallet':'active','wallet_cash':wallet_cash})
    else:
        return HttpResponse("<h1>404 -- Not exsist </h1>")

def rating(request):
    if verification(request):
        return render(request,'login.html',{'login':'active'})
    if request.method == 'GET':
        rating = request.GET['id']
        user = sah_user.objects.get(email = request.session['user_email'] )
        district = user.district
        if rating == '0':
            if request.session.get('salon_type') == 'Male':
                data = sah_service_provider.objects.filter(verification_status='active',available_status='active',district = district).exclude(salontype = 'Female').order_by('?')
            if request.session.get('salon_type') == 'Female':
                data = sah_service_provider.objects.filter(verification_status='active',available_status='active',district = district).exclude(salontype = 'Male').order_by('?')
            if request.session.get('salon_type') == None:
                data = sah_service_provider.objects.filter(verification_status='active',available_status='active',district = district).order_by('?')
            data = list(data.values('service_provider_id', 'name','shopname','image','rating'))
            return JsonResponse({'data':data})
        if request.session.get('salon_type') == 'Male':
            data = sah_service_provider.objects.filter(verification_status='active',available_status='active',rating = rating,district = district).exclude(salontype = 'Female').order_by('?')
        if request.session.get('salon_type') == 'Female':
            data = sah_service_provider.objects.filter(verification_status='active',available_status='active',rating = rating,district = district).exclude(salontype = 'Male').order_by('?')
        if request.session.get('salon_type') == None:
            data = sah_service_provider.objects.filter(verification_status='active',available_status='active',rating = rating,district = district).order_by('?')
        data = list(data.values('service_provider_id', 'name','shopname','image','rating'))
        return JsonResponse({'data':data})
    if request.method == 'POST':
        temp= request.POST['id']
        x = temp.split(",")
        rating = x[0]
        txnid = x[1]
        transaction.objects.filter(txnid = txnid).update(order_rating=rating)
        data = transaction.objects.filter(txnid = txnid)
        data = data[0]
        float_rating = data.service_provider_id.float_rating
        if float_rating == None:
            float_rating = 0.0
        update_rating = float(float(data.order_rating)+float(float_rating))/2.0
        rating=int(update_rating + 0.5)
        sah_service_provider.objects.filter(service_provider_id =data.service_provider_id.service_provider_id).update(float_rating= update_rating,rating=rating)
        data = transaction.objects.filter(txnid = txnid)
        data = list(data.values('order_rating'))
        return JsonResponse({'data':data})



def getservice(request):
    if verification(request):
        return render(request,'login.html',{'login':'active'})
    if request.method == 'GET':
        service_man_id = request.GET['id']
        data = service.objects.filter(service_provider_id__service_provider_id=service_man_id,service_status = 'active')
        data1 = cartlist.objects.filter(user_id = request.session['user_id'] ,service_provider_id = service_man_id)
        if data1.count() == 0:
            cartitem = 'empty'
        else:
            cartitem = 'full'
    return render(request, 'Ugetservice.html',{'data':data,'data1':data1,'cartitem':cartitem})

def cartlistr(request):
    if verification(request):
        return render(request,'login.html',{'login':'active'})
    if request.method == 'POST':
        temp= request.POST['id']
        x = temp.split("a")
        service_id = x[0]
        service_prov_id =x[1]
        print(service_id)
        print(service_prov_id)
        user = sah_user.objects.filter(email = request.session['user_email'] )
        user = user[0]
        dat = cartlist.objects.filter(user_id = user.user_id).exclude(service_provider_id = service_prov_id )
        if dat.count() !=0:
            cartlist.objects.filter(user_id = user.user_id).exclude(service_provider_id = service_prov_id ).delete()
        service_ob =service.objects.get(service_id = service_id)
        count = cartlist.objects.filter(service_id__service_id=service_id,user_id=user.user_id).count()
        if count == 0:
            cartlist(user_id = user.user_id,service_provider_id = service_prov_id, service_id =service_ob).save()
        data = cartlist.objects.filter(user_id = user.user_id,service_provider_id = service_prov_id)
        data = list(data.values('temp_id','service_id__service_id','service_id__name_of_service', 'service_id__price','service_provider_id','service_id__image'))
    return JsonResponse({'data':data})


def cartlistrRemove(request):
    if verification(request):
        return render(request,'login.html',{'login':'active'})
    if request.method == 'POST':
        user_id = request.session['user_id']
        temp_id = request.POST['id']
        cartlist.objects.filter(user_id = user_id,temp_id = temp_id).delete()
        data = cartlist.objects.filter(user_id = user_id)
        if data.count() == 0:
            cartitem = 'empty'
        else:
            cartitem = 'full'
        data = list(data.values('temp_id','service_id__service_id','service_id__name_of_service', 'service_id__price','service_provider_id','service_id__image'))
    return JsonResponse({'data':data,'cartitem':cartitem})

def placeorder(request):
    if verification(request):
        return render(request,'login.html',{'login':'active'})
    user_id = request.session['user_id']
    data = cartlist.objects.filter(user_id = user_id)
    data = data[0]
    service_provider_id = data.service_provider_id
    count = sah_service_provider.objects.filter(service_provider_id = service_provider_id ,verification_status='active',available_status='active').count()
    if count == 0:
        return render(request, 'UMasterstatus.html')
    data = cartlist.objects.filter(user_id = user_id)
    data1 = sah_user.objects.filter(user_id = user_id)
    totalprice = 0
    for d in data:
        totalprice = totalprice + d.service_id.price
    paynow = int((totalprice/100)*30)
    paylater = int((totalprice/100)*70)
    wallet_data  = user_wallet.objects.get(user_id__user_id = user_id)
    flashP = ''
    if int(wallet_data.wallet_cash) >= 200:
        paynow = 1
        flashP = 'yes'
    return render(request, 'Uplaceorder.html',{'data':data,'data1':data1,'totalprice':totalprice,'paynow':paynow,'paylater':paylater,'flashP':flashP})


def orderList(request):
    if verification(request):
        return render(request,'login.html',{'login':'active'})
    user_id = request.session['user_id']
    data = transaction.objects.filter(user_id= user_id).exclude(payment_status = 'initiate').order_by('-txn_id')
    return render(request, 'Uorder_status.html', {'order_status': 'active','data': data})

def orderdetail(request):
    if verification(request):
        return render(request,'login.html',{'login':'active'})
    if request.method == 'GET':
        txnid = request.GET['id']
        data = transaction.objects.filter(txnid =txnid)
        if data.count() == 1:
            return render(request, 'Uorderdetail.html', {'order_status': 'active','data': data})

def verification(request):
    if request.session.get('user_id') != None:
        user_id = request.session['user_id']
        email = request.session['user_email']
        if user_id == None:
            return render(request, 'login.html',{'login':'active'})
        data = sah_user.objects.get(user_id = user_id)
        if data.email == email:
            return False
    else:
        return True



##common methods

def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        category = request.POST['category']
        if category == 'User':
            data = sah_user.objects.filter(email = email)
            count = data.count()
            if count == 1:
                data = data[0]
                request.session['fp'] = email
                request.session['ct'] = category
                otp = str(random.randint(100000,999999))
                otp_authentication(user_id= data.user_id, otp = otp,category= category).save()
                subject = 'OTP'
                message = 'Dear '+data.user_name+' otp for your Password reset is '+str(otp)+' This is only valid for 5 Minutes.'
                recepient = str(email)
                send_mail(subject,message, EMAIL_HOST_USER, [recepient], fail_silently = False)
                return render(request, 'getotp.html',{'email':email})
            else:
                msg = 'Email not exsist'
                return render(request, 'forgotpassword.html',{'msg':msg})

        if category == 'Master':
            data = sah_service_provider.objects.filter(email = email)
            count = data.count()
            if count == 1:
                data = data[0]
                request.session['fp'] = email
                request.session['ct'] = category
                otp = str(random.randint(100000,999999))
                otp_authentication(user_id= data.service_provider_id, otp = otp,category= category).save()
                subject = 'OTP'
                message = 'Dear '+data.name+' otp for your Password reset is '+str(otp)+' This is only valid for 5 Minutes.'
                recepient = str(email)
                send_mail(subject,message, EMAIL_HOST_USER, [recepient], fail_silently = False)
                return render(request, 'getotp.html',{'email':email})
            else:
                msg = 'Email not exsist'
                return render(request, 'forgotpassword.html',{'msg':msg})

        if category == 'Manager':
            data = sah_area_manager.objects.filter(email = email)
            count = data.count()
            if count == 1:
                data = data[0]
                request.session['fp'] = email
                request.session['ct'] = category
                otp = str(random.randint(100000,999999))
                otp_authentication(user_id= data.manager_id, otp = otp,category= category).save()
                subject = 'OTP'
                message = 'Dear '+data.name+' otp for your Password reset is'+str(otp)+' This is only valid for 5 Minutes.'
                recepient = str(email)
                send_mail(subject,message, EMAIL_HOST_USER, [recepient], fail_silently = False)
                return render(request, 'getotp.html',{'email':email})
            else:
                msg = 'Email not exsist'
                return render(request, 'forgotpassword.html',{'msg':msg})
    return render(request, 'forgotpassword.html')


def getotp(request):
    if request.method == 'POST':
        otp = request.POST['otp']
        password = request.POST['password']
        otp_authentication.objects.filter(created_at__lte = timezone.now() - timedelta(minutes=5)).delete()
        if len(password) <=  7:
            msg = 'Password too short!'
            return render(request,'getotp.html',{'msg':msg})
        email = request.session['fp']
        category = request.session['ct']
        if category == 'User':
            data = sah_user.objects.get(email = email)
            user_id = data.user_id
            otpdata = otp_authentication.objects.filter(user_id= user_id,category=category).order_by('-id')
            if otpdata.count() >= 1:
                otpdata = otpdata[0]
                if str(otp) == str(otpdata.otp):
                    sah_user.objects.filter(email = email).update(password = password)
                    msg = 'Password  changed succesfully'
                    try:
                        request.session['fp'] = None
                        request.session['ct'] = None
                        print('del')
                    except KeyError:
                        pass
                    return render(request, 'login.html',{'login':'active','msg':msg})
                msg = 'otp not matched'
                print('user')
                print(otp)
                print(otpdata.otp)
                return render(request, 'getotp.html',{'email':email,'msg':msg})
        if category == 'Master':
            data = sah_service_provider.objects.get(email = email)
            service_provider_id = data.service_provider_id
            otpdata = otp_authentication.objects.filter(user_id= service_provider_id,category=category).order_by('-id')
            if otpdata.count() >= 1:
                otpdata = otpdata[0]
                if str(otp) == str(otpdata.otp):
                    sah_service_provider.objects.filter(email = email).update(password = password)
                    msg = 'Password  changed succesfully'
                    try:
                        request.session['fp'] = None
                        request.session['ct'] = None
                        print('del')
                    except KeyError:
                        pass
                    return render(request, 'Elogin.html',{'login':'active','msg':msg})
                print('Euser')
                msg = 'otp not matched'
                return render(request, 'getotp.html',{'email':email,'msg':msg})
        if category == 'Manager':
            data = sah_area_manager.objects.get(email = email)
            print(data)
            manager_id = data.manager_id
            otpdata = otp_authentication.objects.filter(user_id = manager_id,category=category).order_by('-id')
            if otpdata.count() >= 1:
                otpdata = otpdata[0]
                if str(otp) == str(otpdata.otp):
                    sah_area_manager.objects.filter(email = email).update(password = password)
                    msg = 'Password  changed succesfully'
                    try:
                        request.session['fp'] = None
                        request.session['ct'] = None
                        print('del')
                    except KeyError:
                        pass
                    return render(request, 'Mlogin.html',{'login':'active','msg':msg})
                print('Muser')
                msg = 'otp not matched'
                return render(request, 'getotp.html',{'email':email,'msg':msg})



################## admin area

def admin_home(request):
    if admin_verification(request):
        return render(request,'login.html')
    ###upper dash data
    user_count = sah_user.objects.all().count()
    master_count = sah_service_provider.objects.all().count()
    manager_count = sah_area_manager.objects.all().count()
    succesfull_order_count = transaction.objects.filter(payment_status='success',order_status='completed').count()

    #lower dash data
    previous = transaction.objects.filter(payment_status='success' ,created_at__gte = timezone.now() - timedelta(60),created_at__lt =timezone.now() - timedelta(30)).count()
    latest = transaction.objects.filter(payment_status='success' ,created_at__gte = timezone.now() - timedelta(30),created_at__lt =timezone.now() - timedelta(00)).count()
    if previous == 0:
        change = int( ((latest + previous)/(previous+1))*100)
    else:
        change = int( ((latest + previous)/previous)*100)
    total = transaction.objects.filter(payment_status='success' ,created_at__gte = timezone.now() - timedelta(30),created_at__lt =timezone.now() - timedelta(1)).count()
    completed = transaction.objects.filter(payment_status='success', order_status='completed', created_at__gte = timezone.now() - timedelta(30),created_at__lt =timezone.now() - timedelta(1)).count()
    if completed != 0:
        last_30_conv = int ((completed/total)*100)
    else:
        last_30_conv = 0
    total = transaction.objects.filter(payment_status='success').count()
    completed = transaction.objects.filter(payment_status='success', order_status='completed').count()
    if completed != 0:
        total_conv =int( (completed/total)*100 )
    else:
        total_conv = 0
    total = transaction.objects.filter(payment_status='success' ,created_at__gte = timezone.now() - timedelta(2),created_at__lt =timezone.now() - timedelta(1)).count()
    completed = transaction.objects.filter(payment_status='success', order_status='initiated', created_at__gte = timezone.now() - timedelta(2),created_at__lt =timezone.now() - timedelta(1)).count()
    if completed != 0:
        last_day = int((completed/total)*100)
    else:
        last_day = 0


    data={'user_count':user_count, 'master_count':master_count,
        'manager_count':manager_count, 'succesfull_order_count':succesfull_order_count,
        'change':change, 'last_30_conv':last_30_conv, 'total_conv':total_conv,
        'last_day':last_day
        }
    return render(request,'ahome.html',{'data':data, 'admin_home':'active'})

def adminWidgets(request):
    if admin_verification(request):
        return render(request,'login.html')
    return render(request,'admin_widgets.html',{'data':'data', 'adminWidgets':'active'})

def adminPanel(request):
    if admin_verification(request):
        return render(request,'login.html')
    try:
        table = request.GET['id']
        if table == 'managerlist':
            data = sah_area_manager.objects.all().order_by('district' , 'name')
        if table == 'masterlist':
            data = sah_service_provider.objects.all().order_by('district' , 'name')
        if table == 'userlist':
            data = sah_user.objects.all().order_by('district' , 'user_name')
        if table == 'transaction':
            data = transaction.objects.all().order_by('-created_at')
        return render(request,'admin_panels.html',{'data':data, 'adminPanel':'active','table':table})
    except KeyError:
        return render(request,'admin_panels.html',{'data':'data', 'adminPanel':'active'})
    return render(request,'admin_panels.html',{'data':'data', 'adminPanel':'active'})

def addManager(request):
    if admin_verification(request):
        return render(request,'login.html')
    district_data = district_list.objects.all().order_by('district')
    if request.method == 'POST':
        user_name = request.POST['user_name']
        email = request.POST['email']
        mobile = request.POST['mobile']
        address = request.POST['address']
        gender = request.POST['gender']
        upi = request.POST['upi']
        district = request.POST['district']
        password = request.POST['password']
        if user_name == None:
            msg = 'blank name invalid'
            return render(request,'admin_addmanager.html',{'msg':msg,'addManager':'active','user_name':user_name,'email':email,'mobile':mobile,'address':address,'gender':gender,'upi':upi,'district':district,'district_list':district_data})
        if email == None:
            msg = 'blank email invalid'
            return render(request,'admin_addmanager.html',{'msg':msg,'addManager':'active','user_name':user_name,'email':email,'mobile':mobile,'address':address,'gender':gender,'upi':upi,'district':district, 'district_list':district_data})
        if mobile == None:
            msg = 'blank mobile number invalid'
            return render(request,'admin_addmanager.html',{'msg':msg,'addManager':'active','user_name':user_name,'email':email,'mobile':mobile,'address':address,'gender':gender,'upi':upi,'district':district, 'district_list':district_data})
        if address == None:
            msg = ' address invalid'
            return render(request,'admin_addmanager.html',{'msg':msg,'addManager':'active','user_name':user_name,'email':email,'mobile':mobile,'address':address,'gender':gender,'upi':upi,'district':district, 'district_list':district_data})
        if gender == None:
            msg = 'select gender'
            return render(request,'admin_addmanager.html',{'msg':msg,'addManager':'active','user_name':user_name,'email':email,'mobile':mobile,'address':address,'gender':gender,'upi':upi,'district':district, 'district_list':district_data})
        if district == None:
            msg = 'select district'
            return render(request,'admin_addmanager.html',{'msg':msg,'addManager':'active','user_name':user_name,'email':email,'mobile':mobile,'address':address,'gender':gender,'upi':upi,'district':district, 'district_list':district_data})
        if upi == None:
            msg = 'Upi not blank'
            return render(request,'admin_addmanager.html',{'msg':msg,'addManager':'active','user_name':user_name,'email':email,'mobile':mobile,'address':address,'gender':gender,'upi':upi,'district':district, 'district_list':district_data})
        if len(mobile) <= 9:
            msg = 'Mobile number not valid'
            return render(request,'admin_addmanager.html',{'msg':msg,'addManager':'active','user_name':user_name,'email':email,'mobile':mobile,'address':address,'gender':gender,'upi':upi,'district':district, 'district_list':district_data})
        if len(password) <=  7:
            msg = 'Password too short!'
            return render(request,'admin_addmanager.html',{'msg':msg,'addManager':'active','user_name':user_name,'email':email,'mobile':mobile,'address':address,'gender':gender,'upi':upi,'district':district, 'district_list':district_data})
        if password != request.POST['re_password']:
            msg = 'Password not match!'
            return render(request,'admin_addmanager.html',{'msg':msg,'addManager':'active','user_name':user_name,'email':email,'mobile':mobile,'address':address,'gender':gender,'upi':upi,'district':district, 'district_list':district_data})
        emailcounts = sah_area_manager.objects.filter(email= email).count()
        mobilecount = sah_area_manager.objects.filter(mobile= mobile).count()
        if emailcounts == 1:
            msg = 'Email already exisit with other account!'
            return render(request,'admin_addmanager.html',{'msg':msg,'addManager':'active','user_name':user_name,'email':email,'mobile':mobile,'address':address,'gender':gender,'upi':upi,'district':district, 'district_list':district_data})
        if mobilecount == 1:
            msg = 'Mobile number already exisit with other account!'
            return render(request,'admin_addmanager.html',{'msg':msg,'addManager':'active','user_name':user_name,'email':email,'mobile':mobile,'address':address,'gender':gender,'upi':upi,'district':district,'district_list':district_data})
        sah_area_manager(name = user_name, email = email, mobile = mobile, address = address,gender = gender,district = district , password = password,email_verification=None, upi= upi).save()
        msg = 'Account created succesfully '
        return render(request, 'admin_addmanager.html',{'msg1':msg,'addManager':'active', 'district_list':district_data})
    else:
        return render(request,'admin_addmanager.html',{'addManager':'active', 'district_list':district_data})
    return render(request,'admin_addmanager.html',{'data':'data', 'addManager':'active', 'district_list':district_data})

def addDistrict(request):
    if admin_verification(request):
        return render(request,'login.html')
    if request.method == 'POST':
        state = request.POST['state']
        district = request.POST['district']
        state_ob = state_list.objects.get(state = state)
        data = state_list.objects.all().order_by('state')
        count  = district_list.objects.filter(district=district,state_id= state_ob).count()
        if count != 0:
            msg = 'District already exsist'
            data = state_list.objects.all().order_by('state')
            district_data = district_list.objects.all().order_by('state_id__state')
            return render(request,'admin_add_district.html',{'data':data, 'district_data':district_data, 'addDistrict':'active','msg':msg})
        district_list(district= district ,state_id= state_ob).save()
        msg =  str(district)+' is succesfully added for state '+state+'.'
        data = state_list.objects.all().order_by('state')
        district_data = district_list.objects.all().order_by('state_id__state')
        return render(request,'admin_add_district.html',{'data':data,'district_data':district_data, 'addDistrict':'active','msg1':msg})
    data = state_list.objects.all().order_by('state')
    district_data = district_list.objects.all().order_by('state_id__state')
    return render(request,'admin_add_district.html',{'data':data, 'district_data':district_data, 'addDistrict':'active'})


def ongoingOrders(request):
    if admin_verification(request):
        return render(request,'login.html')
    if request.method == 'POST':
        data = transaction.objects.filter(payment_status = 'success',order_status='initiated', created_at__gte = timezone.now() - timedelta(hours = 2)).order_by('-created_at')
        data = list(data.values('service_provider_id__name','service_provider_id__service_provider_id',
            'service_provider_id__manager_id__name','service_provider_id__manager_id__manager_id',
            'service_provider_id__manager_id__mobile', 'order_status',
            'amount_sah','amount_service','created_at'))
        return JsonResponse({'data':data})
    ongoing_order_data = transaction.objects.filter(payment_status = 'success',order_status='initiated',created_at__gte = timezone.now() - timedelta(hours = 2)).order_by('-created_at')
    return render(request,'admin_ongoing_order_data.html',{'data':ongoing_order_data, 'ongoingOrders':'active'})

def alogin(request):
    if request.method == 'POST':
        email = request.POST['email']
        key = request.POST['key']
        data = sah_admin.objects.filter(email= email,key = key)
        counts = sah_admin.objects.filter(email= email,key = key).count()
        if counts == 1:
            data=data[0]
            if data.password == request.POST['password']:
                request.session['admin_id'] = data.admin_id
                request.session['admin_email'] = data.email
                request.session['admin_key'] = data.key

                return admin_home(request)
            else:
                msg = "email or Password or key is invalid"
                return render(request, 'alogin.html',{'msg':msg})
        else:
            msg = "email or Password or key is invalid"
            return render(request, 'alogin.html',{'msg':msg})
    else:
        return render(request,'alogin.html')

def alogout(request):
    try:
        request.session['admin_id'] = None
        request.session['admin_email'] = None
        request.session['admin_key'] = None
        print('del')
    except KeyError:
        pass
    return admin_home(request)

def admin_verification(request):
    if request.session.get('admin_id') != None:
        admin_id = request.session['admin_id']
        email = request.session['admin_email']
        key = request.session['admin_key']
        if admin_id == None:
            return render(request, 'alogin.html')
        data = sah_admin.objects.get(admin_id = admin_id)
        if data.email == email and data.key == key:
            return False
    else:
        return True


#### admin - live data
def admin_get_live_data(request):
    if admin_verification(request):
        return render(request,'alogin.html')
    if request.session.get('admin_id') == None:
        return JsonResponse({'data':0})


    o6 = transaction.objects.filter(payment_status='success' ,created_at__gte = timezone.now() - timedelta(minutes = 10)).count()
    o5 = transaction.objects.filter(payment_status='success' ,created_at__gte = timezone.now() - timedelta(minutes = 20),created_at__lt =timezone.now() - timedelta(minutes = 10)).count()
    o4 = transaction.objects.filter(payment_status='success' ,created_at__gte = timezone.now() - timedelta(minutes = 30),created_at__lt =timezone.now() - timedelta(minutes = 20)).count()
    o3 = transaction.objects.filter(payment_status='success' ,created_at__gte = timezone.now() - timedelta(minutes = 40),created_at__lt =timezone.now() - timedelta(minutes = 30)).count()
    o2 = transaction.objects.filter(payment_status='success' ,created_at__gte = timezone.now() - timedelta(minutes = 50),created_at__lt =timezone.now() - timedelta(minutes = 40)).count()
    o1 = transaction.objects.filter(payment_status='success' ,created_at__gte = timezone.now() - timedelta(minutes= 60),created_at__lt =timezone.now() - timedelta(minutes = 50)).count()

    data ={'o1':o1, 'o2':o2, 'o3':o3,'o4':o4,'o5':o5,'o6':o6 }
    return JsonResponse({'data':data})

def userCount(request):
    if admin_verification(request):
        return render(request,'alogin.html')
    if request.session.get('admin_id') == None:
        return JsonResponse({'data':0})
    user_count = sah_user.objects.all().count()
    master_count = sah_service_provider.objects.all().count()
    manager_count = sah_area_manager.objects.all().count()
    succesfull_order_count = transaction.objects.filter(payment_status='success',order_status='completed').count()

    data ={'user_count':user_count, 'master_count':master_count, 'manager_count':manager_count,'succesfull_order_count':succesfull_order_count}
    return JsonResponse({'data':data})



########################### Custom Error handler
def handler404(request, exception):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)