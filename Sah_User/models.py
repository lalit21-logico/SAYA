from django.db import models
from django.utils.timezone import now
from io import BytesIO
from PIL import Image
from django.core.files import File


def compress(image):
    im = Image.open(image)
    im_io = BytesIO() 
    im = im.convert('RGB')
    im = im.resize((400, 400))
    im.save(im_io, 'JPEG', quality=10)
    new_image = File(im_io, name=image.name)
    return new_image

# Create your models here.
class sah_user(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    mobile = models.CharField(max_length=50)
    address = models.CharField(max_length=200)
    gender = models.CharField(max_length=10)
    district = models.CharField(max_length=50)
    wallet_id = models.IntegerField(blank=True, null=True)
    password = models.CharField(max_length=50)
    email_verification = models.CharField(max_length=10, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "sah_user"

class user_wallet(models.Model):
    wallet_id = models.AutoField(primary_key=True)
    wallet_cash = models.CharField(max_length=50)
    user_id = models.ForeignKey(sah_user,null=True,blank=True,on_delete=models.RESTRICT)
    class Meta:
        db_table = "user_wallet"


class sah_area_manager(models.Model):
    manager_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    mobile = models.CharField(max_length=50)
    address = models.CharField(max_length=200)
    gender = models.CharField(max_length=10)
    district = models.CharField(max_length=50)
    email_verification = models.CharField(max_length=10, null=True)
    upi = models.CharField(max_length=50)
    password = models.CharField(max_length=50, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "sah_area_manager"

class sah_service_provider(models.Model):
    service_provider_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    shopname = models.CharField(max_length=50, null=True)
    image = models.ImageField(upload_to='images/master',null=True)
    email = models.CharField(max_length=50)
    mobile = models.CharField(max_length=50)
    address = models.CharField(max_length=200)
    salontype = models.CharField(max_length=10)
    district = models.CharField(max_length=50)
    verification_status = models.CharField(max_length=50)
    available_status = models.CharField(max_length=10,default='active')
    rating = models.IntegerField(blank=True, null=True)
    float_rating =models.FloatField(blank= True,null=True)
    manager_id = models.ForeignKey(sah_area_manager,null=True,blank=True,on_delete=models.CASCADE)
    password = models.CharField(max_length=50, null=True)
    manager_commision = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        new_image = compress(self.image)
        self.image = new_image
        super().save(*args, **kwargs)
        
    class Meta:
        db_table = "sah_service_provider"

class service(models.Model):
    service_id = models.AutoField(primary_key=True)
    name_of_service = models.CharField(max_length=80)
    price = models.IntegerField(blank=True, null=True)
    information = models.CharField(max_length=500)
    image = models.ImageField(upload_to='images/master/service')
    service_status = models.CharField(max_length=10,default='active')
    service_provider_id = models.ForeignKey(sah_service_provider,null=True,blank=True,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        new_image = compress(self.image)
        self.image = new_image
        super().save(*args, **kwargs)

    class Meta:
        db_table = "service"
    

class cartlist(models.Model):
    temp_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(blank=True, null=True)
    service_provider_id = models.IntegerField(blank=True, null=True)
    service_id = models.ForeignKey(service,null=True,blank=True,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "cartlist"

class transaction(models.Model):
    txn_id = models.AutoField(primary_key=True)
    txnid = models.CharField(max_length=50)
    amount_sah = models.IntegerField(null=False)
    amount_service = models.IntegerField(null=False)
    user_id = models.IntegerField(null=False)
    manager_id = models.IntegerField( null=False)
    order_data = models.TextField()
    order_rating =models.IntegerField(blank= True,null=True)
    service_provider_id = models.ForeignKey(sah_service_provider,null=True,blank=True,on_delete=models.RESTRICT)
    payment_status = models.CharField(max_length=10, null = False)
    addedon =models.DateTimeField(null =True)
    bank_ref_num = models.TextField(null=True)
    order_status = models.CharField(max_length=10, null = False)
    notify_mannager = models.CharField(max_length=10, null = True)
    notify_master = models.CharField(max_length=10, null = True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "transaction"



class otp_authentication(models.Model):
    id = models.AutoField(primary_key=True)
    otp = models.IntegerField(null=True)
    category = models.CharField(max_length=10, null = False)
    user_id = models.IntegerField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "otp_authentication"


class schedular_flag(models.Model):
    item_id = models.AutoField(primary_key=True)
    d = models.IntegerField(blank=True, null=True)
    m = models.IntegerField(blank=True, null=True)
    y = models.IntegerField(blank=True, null=True)
    class Meta:
        db_table = "schedular_flag"


class state_list(models.Model):
    id = models.AutoField(primary_key=True)
    state = models.CharField(max_length=50,unique = True)
    class Meta:
        db_table = "state_list"

class district_list(models.Model):
    id = models.AutoField(primary_key=True)
    district = models.CharField(max_length=50)
    state_id = models.ForeignKey(state_list,null=False,blank=True,on_delete=models.RESTRICT)
    class Meta:
        db_table = "district_list"

class contact_us(models.Model):
    id =models.AutoField(primary_key=True)
    subject = models.TextField(null=True)
    message = models.TextField(null=True)
    user_email = models.CharField(max_length=50)
    user_contact = models.CharField(max_length=20)
    resolve_status =models.CharField(max_length=10)
    class Meta:
        db_table = "contact_us"


################# admin - section


class sah_admin(models.Model):
    admin_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    mobile = models.CharField(max_length=50)
    key = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "sah_admin"