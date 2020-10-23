from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from Sah_User.models import *
from django.db.models import F
import random
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg, Max, Min, Sum
# Create your views here.

def home(request):

    return render(request,'Mhome.html',{'home':'active'})

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        data = sah_area_manager.objects.filter(email= email)
        counts = sah_area_manager.objects.filter(email= email).count()
        if counts == 1:
            data=data[0]
            if data.password == request.POST['password']:
                request.session['Muser_id'] = data.manager_id
                request.session['Muser_email'] = data.email
                request.session['Muser_name'] = data.name
                return render(request, 'Mhome.html',{'home':'active'})
            else:
                msg = "email or Password invalid"
                return render(request, 'Mlogin.html',{'login':'active','msg':msg,'email':email})
        else:
            msg = "email or Password invalid"
            return render(request, 'Mlogin.html',{'login':'active','msg':msg,'email':email})
    else:
        return render(request,'Mlogin.html',{'login':'active'})



def logout(request):
    try:
        request.session['Muser_id'] = None
        request.session['Muser_email'] = None
        request.session['Muser_name'] = None
        print('del')
    except KeyError:
        pass
    return home(request)

def contact(request):
    if verification(request):
        return render(request,'Mlogin.html',{'Mlogin':'active'})
    return render(request,'Mcontact.html',{'contact':'active'})

def contact(request):
    if verification(request):
        return render(request,'Mlogin.html',{'login':'active'})
    if request.method == 'POST':
        user_id = request.session['Muser_id']
        user = sah_area_manager.objects.get(manager_id = user_id )
        email = user.email
        contact = user.mobile
        subject = request.POST['subject']
        message = request.POST['message']
        contact_us(subject=subject, message= message, user_email = email,user_contact=contact).save()
        msg = "compliment or complaint assigned succesfully"
        return render(request,'Mcontact.html',{'contact':'active','msg':msg})
    return render(request,'Mcontact.html',{'contact':'active'})

def myteam(request):
    if verification(request):
        return render(request,'Mlogin.html',{'login':'active'})
    manager_email = request.session.get('Muser_email')
    data = sah_service_provider.objects.filter(manager_id__email = manager_email).order_by('-service_provider_id')
    return render(request,'Mmyteam.html',{'data':data,'myteam':'active'})

def addmember(request):
    if verification(request):
        return render(request,'Mlogin.html',{'login':'active'})
    district_data = district_list.objects.all().order_by('district')
    if request.method == 'POST':
        user_name = request.POST['user_name']
        shopname = request.POST['shopname']
        email = request.POST['email']
        mobile = request.POST['mobile']
        address = request.POST['address']
        salontype = request.POST['salontype']
        district = request.POST['district']
        password = request.POST['password']
        if user_name == None:
            msg = 'blank name invalid'
            return render(request,'Maddmember.html',{'msg':msg,'myteam':'active','user_name':user_name, 'shopname':shopname,'email':email,'mobile':mobile,'address':address,'salontype':salontype,'district':district,'district_list':district_data})
        if shopname == None:
            msg = 'blank Shop name invalid'
            return render(request,'Maddmember.html',{'msg':msg,'myteam':'active','user_name':user_name, 'shopname':shopname,'email':email,'mobile':mobile,'address':address,'salontype':salontype,'district':district,'district_list':district_data})
        if email == None:
            msg = 'blank email invalid'
            return render(request,'Maddmember.html',{'msg':msg,'myteam':'active','user_name':user_name, 'shopname':shopname,'email':email,'mobile':mobile,'address':address,'salontype':salontype,'district':district,'district_list':district_data})
        if mobile == None:
            msg = 'blank mobile number invalid'
            return render(request,'Maddmember.html',{'msg':msg,'myteam':'active','user_name':user_name, 'shopname':shopname,'email':email,'mobile':mobile,'address':address,'salontype':salontype,'district':district,'district_list':district_data})
        if address == None:
            msg = ' address invalid'
            return render(request,'Maddmember.html',{'msg':msg,'myteam':'active','user_name':user_name, 'shopname':shopname,'email':email,'mobile':mobile,'address':address,'salontype':salontype,'district':district,'district_list':district_data})
        if salontype == None:
            msg = 'select salontype'
            return render(request,'Maddmember.html',{'msg':msg,'myteam':'active','user_name':user_name, 'shopname': shopname,'email':email,'mobile':mobile,'address':address,'salontype':salontype,'district':district,'district_list':district_data})
        if district == None:
            msg = 'select district'
            return render(request,'Maddmember.html',{'msg':msg,'myteam':'active','user_name':user_name, 'shopname':shopname,'email':email,'mobile':mobile,'address':address,'salontype':salontype,'district':district,'district_list':district_data})
        if len(mobile) <= 9:
            msg = 'Mobile number not valid'
            return render(request,'Maddmember.html',{'msg':msg,'myteam':'active','user_name':user_name, 'shopname':shopname,'email':email,'mobile':mobile,'address':address,'salontype':salontype,'district':district,'district_list':district_data})
        if len(password) <=  7:
            msg = 'Password too short!'
            return render(request,'Maddmember.html',{'msg':msg,'myteam':'active','user_name':user_name, 'shopname':shopname,'email':email,'mobile':mobile,'address':address,'salontype':salontype,'district':district,'district_list':district_data})
        if password != request.POST['re_password']:
            msg = 'Password not match!'
            return render(request,'Maddmember.html',{'msg':msg,'myteam':'active','user_name':user_name, 'shopname':shopname,'email':email,'mobile':mobile,'address':address,'salontype':salontype,'district':district,'district_list':district_data})
        emailcounts = sah_service_provider.objects.filter(email= email).count()
        mobilecount = sah_service_provider.objects.filter(mobile= mobile).count()
        if emailcounts == 1:
            msg = 'Email already exisit with other account!'
            return render(request,'Maddmember.html',{'msg':msg,'signup':'active','user_name':user_name, 'shopname':shopname,'email':email,'mobile':mobile,'address':address,'salontype':salontype,'district':district,'district_list':district_data})
        if mobilecount == 1:
            msg = 'Mobile number already exisit with other account!'
            return render(request,'Maddmember.html',{'msg':msg,'signup':'active','user_name':user_name, 'shopname':shopname,'email':email,'mobile':mobile,'address':address,'salontype':salontype,'district':district,'district_list':district_data})
        x = random.randint(999,10000)
        files = request.FILES['myfile']
        files.name = 'img'+str(x)+files.name
        image = files
        manager_ob = sah_area_manager.objects.get(email = request.session.get('Muser_email'))
        sah_service_provider(name = user_name,shopname = shopname, image = image, email = email, mobile = mobile, address = address,salontype = salontype,district = district ,rating = None, manager_id = manager_ob, password = password, verification_status = 'active' ).save()
        msg = 'add member succesfull'
        manager_email = request.session.get('Muser_email')
        data = sah_service_provider.objects.filter(manager_id__email = manager_email).order_by('-service_provider_id')
        return render(request, 'Mmyteam.html',{'msg':msg, 'data':data, 'myteam':'active','district_list':district_data})
    else:
        return render(request,'Maddmember.html',{'myteam':'active','district_list':district_data})


def masterprofile(request):
    if verification(request):
        return render(request,'Mlogin.html',{'login':'active'})
    if request.method == 'GET':
        profile_id = request.GET['id']
        manager_email =  request.session.get('Muser_email')
        data = sah_service_provider.objects.filter( service_provider_id = profile_id, manager_id__email = manager_email)
        return render(request,'Mmasterprofile.html',{'data':data,'myteam':'active'})
    else:
        return HttpResponse("<h1>404 -- Not Found </h1>")

def verification_status(request):
    if verification(request):
        return render(request,'Mlogin.html',{'login':'active'})
    if request.method == 'GET':
        profile_id = request.GET['id']
        manager_email =  request.session.get('Muser_email')
        data = sah_service_provider.objects.get( service_provider_id = profile_id, manager_id__email = manager_email)
        if data.verification_status == 'active':
            sah_service_provider.objects.filter( service_provider_id = profile_id, manager_id__email = manager_email).update(verification_status = 'disable')
            msg = 'Member deativated'
            data = sah_service_provider.objects.filter( service_provider_id = profile_id, manager_id__email = manager_email)
            return render(request,'Mmasterprofile.html',{'data':data,'msg':msg,'myteam':'active'})
        if data.verification_status == 'disable':
            sah_service_provider.objects.filter( service_provider_id = profile_id, manager_id__email = manager_email).update(verification_status = 'active')
            msg = 'Member Activated'
            data = sah_service_provider.objects.filter( service_provider_id = profile_id, manager_id__email = manager_email)
            return render(request,'Mmasterprofile.html',{'data':data,'msg':msg,'myteam':'active'})
    else:
        return HttpResponse("<h1>404 -- Not Found </h1>")

def myearning(request):
    if verification(request):
        return render(request,'Mlogin.html',{'login':'active'})
    Muser_id = request.session['Muser_id']
    Earntoday = transaction.objects.filter(manager_id = Muser_id,order_status='completed', payment_status='success', created_at__gte=timezone.now() - timedelta(1)).aggregate(Sum('amount_sah'))
    Earnmonth = transaction.objects.filter(manager_id = Muser_id,order_status='completed', payment_status='success', amount_sah__gte = 2, created_at__gte=timezone.now() - timedelta(29)).aggregate(Sum('amount_sah'))
    Earnyear = transaction.objects.filter(manager_id = Muser_id,order_status='completed', payment_status='success',amount_sah__gte = '2' , created_at__gte=timezone.now() - timedelta(364)).aggregate(Sum('amount_sah'))
    Earntotal = transaction.objects.filter(manager_id = Muser_id,order_status='completed',amount_sah__gte = '2' , payment_status='success').aggregate(Sum('amount_sah'))
    Earntoday = Earntoday.get('amount_sah__sum')
    Earnmonth = Earnmonth.get('amount_sah__sum')
    Earntotal = Earntotal.get('amount_sah__sum')
    Earnyear = Earnyear.get('amount_sah__sum')
    if Earntoday == None:
         Earntoday = 0
    if Earnmonth == None:
         Earnmonth = 0
    if Earntotal == None:
         Earntotal = 0
    if Earnyear == None:
         Earnyear = 0
    Earntoday = int(int(int(Earntoday)*4)/30)
    Earnmonth = int(int(int(Earnmonth)*4)/30)
    Earntotal = int(int(int(Earntotal)*4)/30)
    Earnyear =  int(int(int(Earnyear)*4)/30)
    return render(request,'Mmyearning.html',{'myearning':'active','Earntoday':Earntoday,'Earnmonth':Earnmonth ,'Earntotal':Earntotal,'Earnyear':Earnyear})
  #set
def ongoing(request):
    if verification(request):
        return render(request,'Mlogin.html',{'login':'active'})
    if request.session.get('notification') != None:
        request.session['notification'] = None
    Muser_id = request.session['Muser_id']
    data = transaction.objects.filter(manager_id = Muser_id, payment_status='success',order_status='initiated')
    return render(request,'Mongoing.html',{'data':data,'ongoing':'active'})




def verification(request):
    if request.session.get('Muser_id') != None:
        Muser_id = request.session['Muser_id']
        email = request.session['Muser_email']
        if Muser_id == None:
            return render(request, 'Elogin.html',{'login':'active'})
        data = sah_area_manager.objects.get(manager_id = Muser_id)
        if data.email == email:
            return False
    else:
        return True
