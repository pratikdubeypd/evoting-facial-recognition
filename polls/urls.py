from django.urls import path
from . import views

urlpatterns = [
    path('',views.pollshome,name='pollshome'),
    path('createpolls/',views.createPolls,name='createpolls'),
    path('createpublicpoll/',views.createPublicPoll,name='createpublicpoll'),
    path('createprivatepoll/',views.createPrivatePoll,name='createprivatepoll'),
    path('privateinvite/<int:poll_id>',views.privateinvite,name='privateinvite'),
    path('privateinvite/<int:poll_id>/deleteinvite',views.deleteinvite,name='deleteinvite'),
    path('publicpolls/',views.publicPolls,name='publicpolls'),
    path("polldetails/<int:poll_id>", views.publicpolldetails, name="polldetails"),
    path("polldetails/<int:poll_id>/deletepublicpoll", views.deletepublicpoll, name="deletepublicpoll"),
    path("privatepolldetails/<int:poll_id>/deleteprivatepoll", views.deleteprivatepoll, name="deleteprivatepoll"),
    path('privatepolls/',views.privatePolls,name='privatepolls'),
    path("privatepolldetails/<int:poll_id>", views.privatepolldetails, name="privatepolldetails"),
    path('polldetails/<int:poll_id>/vote/', views.public_vote, name='publicvote'),
    path('polldetails/<int:poll_id>/results/', views.public_results, name='publicresults'),
    path('privatepolldetails/<int:poll_id>/vote/', views.private_vote, name='privatevote'),
    path('privatepolldetails/<int:poll_id>/userinvite/', views.private_userinvite, name='privateuserinvite'),
    path('invitations/', views.privateinvitations, name='privateinvitations'),
    path('invitations/acceptedinvites', views.acceptedinvites, name='acceptedinvites'),
    path('invitations/<int:poll_id>/invitechoice', views.invitechoice, name='invitechoice'),
    path('privatepolldetails/<int:poll_id>/results/', views.private_results, name='privateresults'),
]