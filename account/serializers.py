from rest_framework import serializers
from django.contrib.auth.models import User

from account.models import MemberDetails


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}, }

        def create(self, validated_data):
            user = User.objects.create_user(**validated_data)
            return user    


class ShowUserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='first_name')

    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'email'] 


class MemberDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberDetails
        fields = '__all__'

        def create(self, validated_data):
            memberDetail = MemberDetails.objects.create(**validated_data)
            return memberDetail
   

class UpdateMemberDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberDetails
        fields = ['issuedBook', 'bookLimit']

        def update(self, instance, validated_data):
            instance.issuedBook = validated_data.get('issuedBook', instance.issuedBook)
            instance.bookLimit = validated_data.get('bookLimit', instance.bookLimit)
            return instance
