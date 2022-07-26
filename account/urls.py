from django.urls import path

from account import views

from knox import views as knox_views
from knox import views as knox_views

urlpatterns = [
    path('signup/', views.RegisterAPI.as_view()),
    path('login/', views.LoginView.as_view()),
    path('logout/', knox_views.LogoutView.as_view(), name='knox_logout'),
    path('logoutall/', knox_views.LogoutAllView.as_view(), name='knox_logoutall'),
    path('members/', views.MemberDetailView.as_view()),
    path('users/', views.ShowUserView.as_view()),
]