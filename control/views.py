from django.shortcuts import render
from . import models
from django.db import models as django_model
from rest_framework.views import APIView
from rest_framework import status
from . import serializers
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.db.models import Sum, F, When, Case, DecimalField
from django.db.models.functions import Coalesce
from rest_framework.decorators import api_view, permission_classes
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework.permissions import IsAuthenticated
from decimal import Decimal
import django_filters
from .serializers import LoginTokenObtainPairSerializer  
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model


User = get_user_model()

channel_layer = get_channel_layer()
print("каналл", channel_layer)

# user_id = None ## REMOVE ?+

 
def index(request):
    return render(request, "index.html")


class OperationFilter(django_filters.FilterSet):
    typ = django_filters.NumberFilter(field_name="category__typ")


class OperationAPIView(APIView):
    serializer_class = serializers.OperationSerializer
    
    def get(self, request):           ## Use django filters ?-
        profile_id = request.GET.get("profile_id")
        operations = models.Operation.objects.filter(profile_id=profile_id)

        # filter_type = request.GET.get("filter_type")
        # if filter_type == "income":
        #     operations = operations.filter(category__typ=True)
        # elif filter_type == "expense":
        #     operations = operations.filter(category__typ=False)

        ## Resolve filtering and sorting correctly  ?-
        filter_date = request.GET.get("filter_date")
        if filter_date == "asc":
            operations = operations.order_by("date")
        elif filter_date == "desc":
            operations = operations.order_by("-date")

        sort_by = request.GET.get("sort_by")
        if sort_by in ["amount", "date"]:
            operations = operations.order_by(sort_by)

        serializer = self.serializer_class(operations, many=True)
        return Response(serializer.data)

        ## Dont use if/elif many  ?-


    def post(self, request):
        profile_id = request.data.get("profile_id")
        global channel_layer
        channel_name = f'user_{profile_id}'
        async_to_sync(channel_layer.group_send)(channel_name, 
                {
                "type": "send_message",
                "message": "Ураа! новая операция добавлена"
                })
        
        serializer = serializers.OperationSerializer(data=request.data, context={"profile_id": profile_id})
        # serializer = self.serializer_class(data=request.data) ## To serializer ?+
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def delete(self, request):
        op_id = request.GET.get("id")
        operation = models.Operation.objects.get(id=op_id)
        if operation:
            operation.delete()
            return Response({"message": "Операция успешно удалена"})
        return Response({"message": "Операция не найдена"}, status=status.HTTP_404_NOT_FOUND)
            
    def put(self, request):
        operation_id = request.data["id"] # TO SERIALIZER ?+
        operation = models.Operation.objects.filter(id=operation_id).first()
        if operation:
            serializer = self.serializer_class(operation,data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response("Operation not found", status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_balance(request):
    profile_id = request.GET["profile_id"]
    if profile_id:
        res = models.Operation.objects.filter(profile_id=profile_id).aggregate(
            total=Coalesce(
                Sum(
                    Case(
                        When(category__typ=True, then=F("amount")),
                        When(category__typ=False, then=-F("amount")),
                        output_field=DecimalField(),
                    )
                ),
                0,
                output_field=DecimalField(),
            ),
        ).get("total")
        global channel_layer        
        channel_name = f'user_{profile_id}'
        if res < -100:
            async_to_sync(channel_layer.group_send)(channel_name, 
                {
                "type": "send_message",
                "message": "Ваш долг больше 100 сомони"
                })
        elif res > 1000:
            async_to_sync(channel_layer.group_send)(channel_name,
                {
                    "type": "send_message",
                    "message": "Ураа, денег заебись"
                }
            )
        elif res == -20:
            async_to_sync(channel_layer.group_send)(channel_name,
            {
                "type": "send_message",
                "message": "Ваш долг равен 20йцукенг"                
            })
        return Response(res, status=status.HTTP_200_OK)
    return Response("Профиль не найден", status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_operation_by_id(request):
    op_id = request.GET["id"] ## Make sure that object exists. Else, return 404 ?+
    operation = models.Operation.objects.get(id=op_id)
    if operation:
        serializer = serializers.OperationSerializer(operation)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response("Операция не найдена", status=status.HTTP_404_NOT_FOUND)


# class LogInAPIView(TokenObtainPairView): ## Login api view ?+
#     serializer_class = serializers.LoginTokenObtainPairSerializer
#     def post(self, request):
#         data = request.data
#         tokens_serializer = self.serializer_class(data=data)
#         tokens_serializer.is_valid(raise_exception=True)
#         # serializer = serializers.LogInSerializer(data=data)
#         # serializer.is_valid(raise_exception=True)
#         # user = models.User.objects.filter(login=data.get("login")).first() ## Use first one time. Ensure that it is not None and continue ?+
#         # if user and check_password(data.get("password"), user.password):
#             # return Response("Доступ предоставлен", status=status.HTTP_200_OK)
#         return Response(tokens_serializer, status=status.HTTP_200_OK)
#         return Response("Пользователь не найден", status=status.HTTP_404_NOT_FOUND)

class LogInAPIView(APIView):
    serializer_class = serializers.LogInSerializer
    # print("qwertyu")
    # permission_classes = [IsAuthenticated]
    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        print(serializer.validated_data)
        refresh = RefreshToken.for_user(serializer.validated_data)
        access = refresh.access_token
        return Response({'refresh': str(refresh),'access': str(access)}, status=status.HTTP_200_OK)
        # return Response("Пользователь не найден", status=status.HTTP_404_NOT_FOUND)
    
    # def post(self, request):
    #     data = request.data
    #     serializer = self.serializer_class(data=data)
    #     serializer.is_valid(raise_exception=True)
    #     tokens = serializer.validated_data
    #     return Response(tokens, status=status.HTTP_200_OK)


class UserAPIView(APIView):
    serializer_class = serializers.UserSerializer
    def get(self, request):
        user_id = request.GET.get("user_id")
        user = models.User.objects.filter(id=user_id).first() ## Use .first() to avoid exception if not found ?+
        if user:
            serializer = serializers.UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response("Пользователь не найден", status=status.HTTP_404_NOT_FOUND)
        
    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    def delete(self, request):
        user_id = request.GET["user_id"]
        user = models.User.objects.filter(id=user_id).first()
        if user:
            user.delete()
            return Response({"message": "Пользователь удален успешно"}, status=status.HTTP_201_CREATED)
        return Response({"message": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request): ## Update the object using the serializer ?+
        user_id = request.data["id"]
        instance_user = models.User.objects.filter(id=user_id).first()
        if instance_user:
            serializer = serializers.ChangeUserPasswordSerializer(data=request.data, instance=instance_user)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response("Пользователь не найден", status=status.HTTP_404_NOT_FOUND)
    


    
        
class ProfileAPIView(APIView):
    def post(self, request): ## Remake the method without 'traceback' and 'print_exc' and try\except ?+
        data = request.data
        serializer = serializers.ProfileSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request):
        user_id = request.GET.get("user_id")
        profile = models.Profile.objects.filter(user_id=user_id).first()
        if profile:
            serializer = serializers.ProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response("Профиль не найден", status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request): ## Dont use try\except here. ?+
            profile_id = request.data.get("id")
            profile = models.Profile.objects.get(id=profile_id)
            if profile:
                serializer = serializers.ProfileSerializer(profile, data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
            return Response("Профиль не найден",  status=status.HTTP_404_NOT_FOUND)
        
        
class CategoryAPIView(APIView):
    def post(self, request):
        serializer = serializers.CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def get(self, request):
        profile_id = request.user.profile_id
        if not profile_id:
            return Response({"error": "profile_id обязателен"}, status=400)
        q = django_model.Q(profile_id__isnull=True) | django_model.Q(profile_id=profile_id)
        cats = models.Category.objects.filter(q)
        serializer = serializers.CategorySerializer(cats, many=True)
        return Response(serializer.data)
    
    def delete(self, request):
        cat_id = request.GET.get("id")
        profile_id = request.GET.get("profile_id") ## Replace all profile_id with request.user.profile_id ?-
        if profile_id:
            if models.Operation.objects.filter(category_id=cat_id, profile_id=profile_id).exists():
                return Response("Есть операции с этой категорией", status=status.HTTP_400_BAD_REQUEST)
            cat = models.Category.objects.filter(id=cat_id, profile_id__isnull=False).first() ## Add checks for not found ?+
            if cat:
                cat.delete()
                return Response("Категория удалена успешно", status=status.HTTP_200_OK)
            return Response("Этy категории нельзя удалять", status=status.HTTP_400_BAD_REQUEST)
        return Response("Профиль не найден", status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request):
        data = request.data         ## update on serializer ?+
        instance = models.Category.objects.filter(id=data.get("id")).first()
        if instance:
            serializer = serializers.CategorySerializer(instance, data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()   # Использует update() внутри, всё правильно ?+
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"message": "Категория не найдена"}, status=status.HTTP_404_NOT_FOUND)