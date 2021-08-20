from Sah_User.models import *
from rest_framework import serializers

class sah_userSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = sah_user
        fields = ('user_id', 'user_name', 'email', 'mobile', 'address', 'gender', 'district', 'wallet_id', 'password', 'email_verification', 'created_at')

class sah_area_managerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = sah_area_manager
        fields = ('manager_id', 'name', 'email', 'mobile', 'address', 'gender', 'district', 'email_verification', 'upi','created_at')

class sah_service_providerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = sah_service_provider
        fields = ('service_provider_id', 'name', 'shopname', 'image', 'email', 'mobile', 'address', 'salontype', 'district', 'verification_status', 'available_status', 'rating', 'float_rating', 'manager_id', 'manager_commision', 'created_at')

class user_walletSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = user_wallet
        fields = ('wallet_id', 'wallet_cash', 'user_id')

class serviceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = service
        fields = ('service_id', 'name_of_service', 'price', 'information', 'image', 'service_status', 'service_provider_id', 'created_at')

class cartlistSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = cartlist
        fields = ('temp_id', 'user_id', 'service_provider_id', 'service_id', 'created_at')

class transactionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = transaction
        fields = ('txn_id', 'txnid', 'amount_sah', 'amount_service', 'user_id', 'manager_id', 'order_data', 'order_rating', 'service_provider_id', 'payment_status', 'addedon', 'bank_ref_num', 'order_status', 'notify_mannager', 'notify_master', 'created_at')

class otp_authenticationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = otp_authentication
        fields = ('id', 'otp', 'category', 'user_id', 'created_at')

class state_listSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = state_list
        fields = ('id', 'state')

class district_listSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = district_list
        fields = ('id', 'district', 'state_id')
    
class contact_usSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = contact_us
        fields = ('id', 'subject', 'message', 'user_email', 'user_contact', 'resolve_status')