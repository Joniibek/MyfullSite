from rest_framework import serializers
from control import models
from django.contrib.auth.hashers import make_password, check_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from control import models
from rest_framework_simplejwt.exceptions import AuthenticationFailed



class UserSerializer(serializers.Serializer):
    login = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate_password(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Пароль слишком короткий")
        return value
    
    def validate_login(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Логин слишком короткий")
        elif models.User.objects.filter(login=value).exists():
            raise serializers.ValidationError("Данный логин уже существует придумайте другой")
        return value

    def create(self, validated_data):
        return models.User.objects.create_user(**validated_data)
    
    
class ChangeUserPasswordSerializer(serializers.Serializer):
    password = serializers.CharField()
    login = serializers.CharField(required=False)
    
    def validate(self, attrs):
        password = attrs["password"]
        if len(password) < 3:
            raise serializers.ValidationError("Пароль не может быть меньше 3 символов")
        if attrs["login"]:
            raise serializers.ValidationError("Нельзя менять логин")
        return attrs

    def update(self, instance, validated_data):
        instance.password = validated_data.get("password", instance.password)
        return instance
    
    # def to_representation(self, instance):
    #     rep = super().to_representation(instance) ## Dont need it. Replace by something else ?+
    #     del rep["password"]
    #     return rep
    
    
class LogInSerializer(serializers.Serializer): ## Login Serialzier ?+
    login = serializers.CharField(min_length=3, max_length=20)
    password = serializers.CharField(min_length=3, max_length=15, write_only=True)
    def validate(self, attrs):
        login = attrs.get("login")
        password = attrs.get("password")
        user = models.User.objects.filter(login=login).first() ## Use first() and then check it. ?+
        if user:
            if len(login) < 3:
                raise serializers.ValidationError("Короткий логин (менее 3 символов)")            
            if len(password) < 3:
                raise serializers.ValidationError("Короткий пароль (не менее 3 символов)")
            elif not check_password(password, user.password):
                print(password, user.password)
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
    name = serializers.CharField()
    avatar = serializers.CharField()
    currency_id = serializers.IntegerField(write_only=True)
    currency = serializers.SerializerMethodField(read_only=True)
    last_sign_in = serializers.DateTimeField(read_only=True)  
    user_id = serializers.IntegerField()
    
    def validate_currency_id(self, value):
        if int(value) > 5:
            raise serializers.ValidationError("Нет такой валюты")
        return value
    
    def validate_name(self, value):
        if not value.isalpha() or len(value) < 3:
            raise serializers.ValidationError("Поле не может иметь циры или менее 3 символов") 
        return value.lower().capitalize().strip()
        
    def create(self, validated_data):
        return models.Profile.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.name = validated_data.get('name', instance.name)
        instance.currency_id = validated_data.get('currency_id', instance.currency_id)
        instance.save()
        return instance
    
    def get_currency(self, obj):
        return obj.currency.name
    
    # def to_representation(self, instance): ## Dont use this method. Solve it by another way  ?-
    #     rep = super().to_representation(instance)
    #     rep["currency"] = instance.currency.name
    #     return rep
    
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
        return models.Operation.objects.create(
            profile_id=self.context["profile_id"],
            category_id=validated_data["category_id"],
            amount=validated_data["amount"],
            comment=validated_data.get("comment", ""),
            date=validated_data.get("date"),
        )

    def update(self, instance, validated_data):
        instance.amount = validated_data.get("amount", instance.amount)
        instance.comment = validated_data.get("comment", instance.comment)
        instance.save()
        return instance
    
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
    
