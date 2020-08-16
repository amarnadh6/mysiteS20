from django.conf import settings
from django.urls import path
from django.views.static import serve
from django.contrib.auth import views as auth_views
from myapp import views
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView

app_name = 'myapp'

urlpatterns = [
    path(r'index/', views.index, name='index'),
    path(r'about/', views.about, name='about'),
    path(r'detail/<top_no>', views.detail, name='detail'),
    path(r'courses/', views.courses, name='courses'),
    path(r'placeorder/', views.placeorder, name='placeorder'),
    path(r'courses/<int:cour_id>/', views.coursedetail, name='coursedetail'),
    path(r'register', views.register, name="register"),
    path(r'myaccount', views.myaccount, name="myaccount"),
    path(r'login', views.user_login, name="user_login"),
    path(r'logout', views.user_logout, name="user_logout"),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path(r'media/', serve, {'document_root': settings.MEDIA_ROOT}),


]
