from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('login/',views.userLogin,name='login'),
    path('signup/',views.signup,name='signup'),
    path('logout/',views.logoutHandler,name='logout'),
    path('profile/',views.profile,name='profile'),
    path('profile/editprofile/',views.editprofile,name='editprofile'),
    path('userprofile/<str:username>', views.userprofile, name='userprofile'),
    path('contact/',views.contact,name='contact'),
    path('about/',views.about,name='about'),
    path('profile/testface/',views.testface,name='testface'),
]