from django.contrib import admin
from django.urls import path
from walletapp import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', views.home, name='home'),
    path('signup', views.signup, name='signup'),
    path('login', views.user_login, name='login'),
    path('logout_user', views.logout_user, name='logout_user'), 
    path('wallet', views.wallet, name='wallet'),
    path('sendMoney', views.sendMoney, name='sendMoney'),
    path('requestMoney', views.requestMoney, name='requestMoney'),
    path('receivedRequest', views.receivedRequest, name='receivedRequest'),
    path('acceptRequest <int:transaction_id>', views.acceptRequest, name='acceptRequest'),
    path('rejectRequest <int:transaction_id>', views.rejectRequest, name='rejectRequest'),
]
