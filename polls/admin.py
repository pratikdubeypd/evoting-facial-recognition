from django.contrib import admin
from .models import Publicpoll, Privatepoll, Publicvote, Privatevote, Privateinvite

# Register your models here.
admin.site.register(Publicpoll)
admin.site.register(Privatepoll)
admin.site.register(Publicvote)
admin.site.register(Privatevote)
admin.site.register(Privateinvite)