from django.contrib import admin

# Register your models here.
from Sah_User.models import *

readonly_fields = ('date',)

# Register your models here.
admin.site.register(sah_user)
admin.site.register(user_wallet)
admin.site.register(sah_area_manager)
admin.site.register(sah_service_provider)
admin.site.register(service)
admin.site.register(transaction)
admin.site.register(otp_authentication)
admin.site.register(schedular_flag)
admin.site.register(cartlist)
admin.site.register(state_list)
admin.site.register(district_list)
admin.site.register(contact_us)
################ admin tables
admin.site.register(sah_admin)
