from register.forms import UserPasswordResetForm
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

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
    # reset password form
    path('resetpassword/',auth_views.PasswordResetView.as_view(template_name="registration/password_reset.html", form_class=UserPasswordResetForm),name='reset_password'),
    # notify to check email
    path('resetpasswordsent/',auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_sent.html"),name='password_reset_done'),
    # link where the user can reset
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset.html"),name='password_reset_confirm'),
    # reset password complete
    path('resetpasswordcomplete/',auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"),name='password_reset_complete'),
]