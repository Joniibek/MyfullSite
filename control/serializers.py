from rest_framework import serializers
from control import models
from django.contrib.auth.hashers import make_password, check_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from control import models
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from .services.opertaion import OperationCreationHandler, OperationUpdateHandler
from .services.user import UserCreationHandler, UserUpdateHandler
from .services.token import TokenCreationHandle
from .services.profile import ProfileCreationHandler, ProfileUpdateHandler



class UserSerializer(serializers.Serializer):
    login = serializers.CharField(min_length=3)
    password = serializers.CharField(write_only=True, min_length=3)

    def create(self, validated_data: dict):
        # login = validated_data["login"]
        # password = validated_data["password"]
        handler = UserCreationHandler(**validated_data)
        self.user = handler.handle()
        return self.user
    
    def get_token(self) -> tuple:
        handler = TokenCreationHandle(self.user)
        return handler.handle()


class ChangeUserPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=3)
    login = serializers.CharField(required=False)
    
    def validate(self, attrs):
        password = attrs["password"]
        if attrs["login"]:
            raise serializers.ValidationError("Нельзя менять логин")
        return attrs

    def update(self, instance, validated_data):
        instance.password = validated_data.get("password", instance.password)
        return instance

    
class LogInSerializer(serializers.Serializer): ## Login Serialzier ?+
    login = serializers.CharField(min_length=3, max_length=20)
    password = serializers.CharField(min_length=3, max_length=15, write_only=True)
    def validate(self, attrs):
        login = attrs.get("login")
        password = attrs.get("password")
        user = models.User.objects.filter(login=login).first() ## Use first() and then check it. ?+
        if user:
            if not check_password(password, user.password):
                raise serializers.ValidationError("Неверный пароль")
            return user
        raise serializers.ValidationError("Неверный логин")
          

class LoginTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        login = attrs.get("login")
        password = attrs.get("password")
        user = models.User.objects.filter(login=login).first()
        if not user:
            raise AuthenticationFailed('Неверный логин')
        if not check_password(password, user.password):
            raise AuthenticationFailed('Неверный пароль')
        refresh = self.get_token(user)
        access = refresh.access_token
        return {
            'refresh': str(refresh),
            'access': str(access),
        }
    
    
class ProfileSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(min_length=3)
    avatar = serializers.CharField()
    currency_id = serializers.IntegerField(write_only=True)
    currency = serializers.SerializerMethodField(read_only=True)
    last_sign_in = serializers.DateTimeField(read_only=True)  
    user_id = serializers.IntegerField()
    
    def validate_name(self, value):
        if not value.isalpha():
            raise serializers.ValidationError("Поле не может иметь циры") 
        return value.lower().capitalize().strip()
        
    def create(self, validated_data):
        handler = ProfileCreationHandler(**validated_data)
        return handler.handle()
    
    def update(self, instance, validated_data):
        handler = ProfileUpdateHandler(instance, **validated_data)
        return handler.handle()
    
    def get_currency(self, obj):
        return obj.currency.name
    
    
class CategorySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    # parent_id = serializers.IntegerField()
    typ = serializers.BooleanField()
    profile_id = serializers.IntegerField()
    
    def validate(self, attrs):
        for i in attrs["name"].split(" "):
            if not i.strip().isalpha() or len(i) < 3:
                raise serializers.ValidationError("Поле не может иметь цифры или иметь менее 3 символов")
            return attrs
    
    def create(self, validated_data):
        return models.Category.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance
    
    
class OperationSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    profile_id = serializers.IntegerField(write_only=True)
    category_id = serializers.IntegerField(write_only=True)
    typ= serializers.IntegerField(source="category.typ", read_only=True) 
    category_name = serializers.CharField(source="category.name", read_only=True)
    amount = serializers.DecimalField(max_digits=20, decimal_places=2)
    date = serializers.DateTimeField(required=False)
    comment = serializers.CharField(max_length=50, required=False)

    def create(self, validated_data):
        # profile_id=self.context["profile_id"]
        # category_id=validated_data["category_id"]
        # amount=validated_data["amount"]
        # comment=validated_data.get("comment", "")
        # date=validated_data.get("date")

        # handler = Opera...
        # ...
        handler = OperationCreationHandler(**validated_data)
        handler.handle()

    def update(self, instance, validated_data):
        amount = validated_data.get("amount", instance.amount)
        comment = validated_data.get("comment", instance.comment)
        opertaion = OperationUpdateHandler(instance, new_amount=amount, new_comment=comment)
        opertaion.handle()

    
    # def to_representation(self, instance): ## FUck U and this method. Find another way or separate to more serializers ?-
    #     rep = super().to_representation(instance)
    #     # print(instance.category)
    #     if not instance.category:
    #         rep["category_name"] = "----"
    #         rep["typ"] = ""
    #     else:
    #         rep["category_name"] = instance.category.name
    #         rep["typ"] = instance.category.typ
    #     rep["currency"] = instance.profile.currency.name
    #     del rep["profile_id"]
    #     del rep["category_id"]
        
    #     return rep
    
