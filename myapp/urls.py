from django.urls import path
from myapp import views
app_name = 'myapp'

urlpatterns = [
    path(r'index/', views.index, name='index'),
    path(r'about/', views.about, name='about'),
    path(r'detail/<top_no>', views.detail, name='detail'),
    path(r'courses/', views.courses, name='courses'),
    path(r'placeorder/', views.placeorder, name='placeorder'),
    path(r'courses/<int:cour_id>/', views.coursedetail, name='coursedetail'),
    path(r'myaccount', views.myaccount, name="myaccount"),
    path(r'login', views.user_login, name="user_login"),
    path(r'logout', views.user_logout, name="user_logout"),

]
