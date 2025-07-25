from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from control import models
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from django.contrib.auth.hashers import make_password, check_password


# class LoginTokenObtainPairSerializer(TokenObtainPairSerializer):

#     def validate(self, attrs):
#         login = attrs.get("login")
#         password = attrs.get("password")
#         user = models.User.objects.filter(login=login).first()
        
#         if not user:
#             raise AuthenticationFailed('Неверный логин')

#         if not check_password(password, user.password):
#             raise AuthenticationFailed('Неверный пароль')
#         refresh = self.get_token(user)
#         access = refresh.access_token

#         return {
#             'refresh': str(refresh),
#             'access': str(access),
#         }
    

class RegisterTokenObtainPairSerializer(TokenObtainPairSerializer):
    
    def validate(self, attrs):
        user = models.User.objects.create(
            login=attrs['login'],
            password=make_password(attrs['password'])
        )
        refresh = self.get_token(user)
        access = refresh.access_token

        return {
            'refresh': str(refresh),
            'access': str(access),
        }
    