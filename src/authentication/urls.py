from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('activate/<uidb64>/<token>/', views.ActivateAccountView.as_view(), name='activate'),
    path('login/', view=views.LoginView.as_view(), name='login'),
    path('token/refresh/', view=views.TokenRefreshView.as_view(), name='refresh-token'),
    path('logout/', view=views.UserLogoutView.as_view(), name='logout')
]