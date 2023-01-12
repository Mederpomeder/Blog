from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('', views.UserViewSet)

urlpatterns = [
    # path('', views.UserListView.as_view()),  # accounts/
    # path('<int:pk>/', views.UserDetailView.as_view()),  # accounts/<id>/
    path('login/', views.CustomLoginView.as_view()),
    path('logout/', views.CustomLogoutView.as_view()),
    path('register/', views.UserRegisterView.as_view()),  # accounts/register/
    path('followers/', views.FollowersApiView.as_view()),
    path('followings/', views.FollowingsApiView.as_view()),
    path('', include(router.urls)),
]
