from rest_framework import serializers
from control import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password



class UserSerializer(serializers.Serializer):
    login = serializers.CharField()
    password = serializers.CharField()
    
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
        validated_data["password"] = make_password(validated_data["password"])
        return models.User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.get('password', instance.password)
        login = validated_data.get('login', instance.login)
        instance.password = validated_data.get(password)
        return instance
    
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        del rep["password"]
        return rep
    
    
class EnteringDataSerializer(serializers.Serializer):
    login = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        login = attrs.get("login")
        password = attrs.get("password")
        
        user = models.User.objects.filter(login=login)
        
        if len(login) < 3:
            raise serializers.ValidationError("Короткий логин (менее 3 символов)")
        elif not user.exists():
            raise serializers.ValidationError("Неверный логин")
        
        if len(password) < 3:
            raise serializers.ValidationError("Короткий пароль (не менее 3 символов)")
        elif not check_password(password, user.first().password):
            raise serializers.ValidationError("Неверный пароль")
        return attrs

    
    
class ProfileSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    avatar = serializers.CharField()
    last_sign_in = serializers.DateTimeField(read_only=True)  
    currency_id = serializers.IntegerField()
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
    
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["currency"] = instance.currency.name
        return rep    
    
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
        # print(validated_data)
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance
    
    
class OperationSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    profile_id = serializers.IntegerField()
    category_id = serializers.IntegerField(required=False)
    amount = serializers.DecimalField(max_digits=20, decimal_places=2)
    date = serializers.DateTimeField(required=False)
    comment = serializers.CharField(max_length=50, required=False)
    
    def validate(self, attrs):
        return attrs
    
    def create(self, validated_data):
        return models.Operation.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.amount = validated_data.get('amount', instance.amount)
        instance.comment = validated_data.get('comment', instance.comment)
        instance.save()
        return instance
    
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        # print(instance.category)
        if not instance.category:
            rep["category_name"] = "----"
            rep["typ"] = ""
            # print("efsmpfm")
        else:
            rep["category_name"] = instance.category.name
            rep["typ"] = instance.category.typ
        rep["currency"] = instance.profile.currency.name
        del rep["profile_id"]
        del rep["category_id"]
        
        return rep
    

