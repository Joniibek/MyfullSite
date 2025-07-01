from django.urls import path
from  . import views 

# router = routers.DefaultRouter()
# router.register(r'user', views.UserViewSet)

urlpatterns = [
    # path("api/user/<int:user_id>/", views.get_user),
    # path('enter/', views.entering_page),
    # path('check_access/', views.check_access),
    # path('registration/', views.registration),
    # path('operations/<int:user_id>/<int:id>', views.OperationAPIView.as_view()),
    path('profile/', views.ProfileAPIView.as_view()),
    path('category/', views.CategoryAPIView.as_view()),
    path('user/', views.UserAPIView.as_view()),
    path('check_access/', views.CheckAccessAPIView.as_view()),
    path('operation/', views.get_operation_by_id),
    path('operations/', views.OperationAPIView.as_view()),
    path('get_balance/', views.get_balance),
]