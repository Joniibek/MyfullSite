from django.shortcuts import render
from . import models
from django.db import models as django_model
from rest_framework.views import APIView
from rest_framework import status
from . import serializers
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.db.models import Sum 
from rest_framework.decorators import api_view
import traceback

user_id = None


class OperationAPIView(APIView):
    serializer_class = serializers.OperationSerializer
    
    def get(self, request):
        profile_id = request.GET.get("profile_id")
        # if not profile_id:
        #     return Response({"error": "profile_id обязателен"}, status=400)

        operations = models.Operation.objects.filter(profile_id=profile_id)

        filter_type = request.GET.get("filter_type")
        if filter_type == "income":
            operations = operations.filter(category__typ=True)
        elif filter_type == "expense":
            operations = operations.filter(category__typ=False)

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

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            validated = serializer.validated_data
            operation = models.Operation.objects.create(
                profile_id=validated['profile_id'],
                category_id=validated['category_id'],
                amount=validated['amount'],
                comment=validated.get('comment', '')
            )
            response_serializer = self.serializer_class(operation)
            return Response(response_serializer.data)
        return Response(serializer.errors, status=400)
    
    def delete(self, request):
        try:
            operation = models.Operation.objects.get(id=request.GET.get("id"))
            operation.delete()
            return Response({"message": "Операция успешно удалена"})
        except models.Operation.DoesNotExist:
            return Response({"message": "Операция не найдена"}, status=status.HTTP_404_NOT_FOUND)
            
    def put(self, request):
        operation_id = request.data.get("id")
        operation = models.Operation.objects.filter(id=operation_id).first()

        if not operation:
            return Response({"error": "Операция не найдена"}, status=404)

        amount = request.data.get("amount")
        category_id = request.data.get("category_id")
        comment = request.data.get("comment")  # может быть None

        if amount is not None:
            operation.amount = amount
        if category_id is not None:
            operation.category_id = category_id
        if "comment" in request.data:
            operation.comment = comment

        operation.save()

        serializer = self.serializer_class(operation)
        return Response(serializer.data)
        
    # def put(self, request):
    #     operation_id = request.data.get("id")
    #     operation = models.Operation.objects.filter(id=operation_id).first()
    #     serializer = serializers.OperationSerializer(operation, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=400)
    

@api_view(['GET'])
def get_balance(request):
    profile_id = request.GET["profile_id"]
    operations = models.Operation.objects.filter(profile_id=profile_id)
    # for i in operations:
    #     if i.category:
    #         positive_operations = operations.aggregate()
    try:
        if operations:
            positive_op = []
            negative_op = []
            for o in operations:
                if o.category != None:
                    if o.category.typ == True:
                        positive_op.append(o.amount)
                    else:
                        negative_op.append(o.amount)
                else:
                    return Response({"balance": "0 "})
            positive_balance = sum(positive_op)
            negative_balance = sum(negative_op)
            res = positive_balance - negative_balance
            return Response({"balance": res})   
    except Exception as e:
        return Response({"error": str(e)})
    return Response({"balance": "0 "})  


@api_view(['GET'])
def get_operation_by_id(request):
    op_id = request.GET["id"]
    operation = models.Operation.objects.get(id=op_id)
    serializer = serializers.OperationSerializer(operation)
    # print(serializer.data)
    return Response(serializer.data)
    

class CheckAccessAPIView(APIView):
    def post(self, request):
        data = request.data
        serializer = serializers.EnteringDataSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = models.User.objects.filter(login=data.get("login"))
        if user.exists() and check_password(data.get("password"), user.first().password):
            return Response({
            'message': True,
            'id': user.first().id,
            'login': user.first().login
        })
        return Response({"message": False})


class UserAPIView(APIView):
    serializer_class = serializers.UserSerializer
    def get(self, request):
        user_id = request.GET.get("user_id")
        user = models.User.objects.get(id=user_id)
        serializer = serializers.UserSerializer(user)
        return Response(serializer.data)
        
    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
    
        serializer.is_valid(raise_exception=True)

        user = serializer.create(serializer.validated_data)
        return Response({
            "message": True,
            "id": user.id,
            "login": user.login
        })
        
    def delete(self, request):
        user_id = request.GET["user_id"]
        user = models.User.objects.filter(id=user_id).first()
        if user:
            user.delete()
            return Response({"message": "Пользователь удален успешно"})
        return Response({"message": "Пользователь не найден"})
    
    def put(self, request):
        serializer = serializers.UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        
        
class ProfileAPIView(APIView):
    def post(self, request):
        try:
            serializer = serializers.ProfileSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)

        except Exception as e:
            traceback.print_exc()  
            return Response({"error": str(e)}, status=500)
    
    def get(self, request):
        user_id = request.GET.get("user_id")
        profile = models.Profile.objects.filter(user_id=user_id).first()
        if profile:
            serializer = serializers.ProfileSerializer(profile)
            return Response(serializer.data)
        return Response({"message": False})
    
    def put(self, request):
        try:
            profile_id = request.data.get("id")
            profile = models.Profile.objects.get(id=profile_id)
            serializer = serializers.ProfileSerializer(profile, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
        
class CategoryAPIView(APIView):
    def post(self, request):
        serializer = serializers.CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    # def post(self, request):
    #     serializer = serializers.CategorySerializer(data=request.data)
    #     if serializer.is_valid(raise_exception=True):
    #         cat = serializer.create(serializer.validated_data)
    #         serializer = serializers.CategorySerializer(cat)
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=400)
    
    def get(self, request):
        profile_id = request.GET.get('profile_id')
        if not profile_id:
            return Response({"error": "profile_id обязателен"}, status=400)
        q = django_model.Q(profile_id__isnull=True) | django_model.Q(profile_id=profile_id)
        cats = models.Category.objects.filter(q)
        serializer = serializers.CategorySerializer(cats, many=True)
        
        return Response(serializer.data)
    
    def delete(self, request):
        cat_id = request.GET.get("id")
        profile_id = request.GET.get("profile_id")
        print(request.GET)
        if models.Operation.objects.filter(category_id=cat_id, profile_id=profile_id).exists():
            return Response({"message": "Есть операции с этой категорией"})
        cat = models.Category.objects.filter(id=cat_id, profile_id__isnull=False).first()
        if cat:
            cat.delete()
            return Response({"message": "Категория удалена успешно"})
        return Response({"message": "Этy категории нельзя удалять"})
    
    def put(self, request):
        data = request.data
        instance = models.Category.objects.filter(id=data.get("id")).first()
        if not instance:
            return Response({"message": "Категория не найдена"}, status=404)

        serializer = serializers.CategorySerializer(instance, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()  # Использует update() внутри, всё правильно
        return Response(serializer.data)

    # def put(self, request):
    #     # print(request.data)
    #     data = request.data
    #     model = models.Category.objects.filter(id=request.data["id"]).first()
    #     serializer = serializers.CategorySerializer(data=data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.update(model, validated_data=serializer.data)
    #     return Response(serializer.data)
        