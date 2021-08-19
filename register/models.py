from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True)
    firstname=models.CharField(max_length=150,default=' ')
    lastname=models.CharField(max_length=150,default=' ')
    bio=models.CharField(max_length=1000,default=' ')
    phone=models.IntegerField(default=0)
    head_shot=models.ImageField(upload_to='profile_images',blank=True)
    
    class Meta:
        ordering = ["user"]

    def __str__(self):
        return self.user.username

class Contact(models.Model):
    sno = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    phone=models.CharField(max_length=10, default=0)
    email = models.CharField(max_length=100)
    desc = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return 'Message from '+ self.email
