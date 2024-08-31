from rest_framework import serializers
from .models import User


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name','last_name','username', 'date_of_birth','gender','password')

        extra_kwargs = {
            'first_name': {'required':True},
            'last_name' : {'required':True},
            'username' : {'required':True},
            'date_of_birth' : {'required':True},
            'gender' : {'required':True ,'allow_blank':False},
            'password' : {'required':True ,'allow_blank':False,'min_length':8, 'write_only': True}
        }

class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')