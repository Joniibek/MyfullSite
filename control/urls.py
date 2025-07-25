from django.urls import path
from  . import views 

# router = routers.DefaultRouter()
# router.register(r'user', views.UserViewSet)

urlpatterns = [
    path("", views.index),
    path('profile/', views.ProfileAPIView.as_view()),
    path('category/', views.CategoryAPIView.as_view()),
    path('user/', views.UserAPIView.as_view()),
    path('check_access/', views.LogInAPIView.as_view()),
    path('operation/', views.get_operation_by_id),
    path('operations/', views.OperationAPIView.as_view()),
    path('get_balance/', views.get_balance),
]
