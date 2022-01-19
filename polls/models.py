from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

# Create your models here.
class Publicpoll(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)
    desc=models.TextField(default="")
    pub_date = models.DateTimeField(default=timezone.now)
    choice1 = models.CharField(max_length=500, default="")
    choice2 = models.CharField(max_length=500, default="")
    choice3 = models.CharField(max_length=500, default="")
    choice4 = models.CharField(max_length=500, default="")
    choice1_vote_count = models.IntegerField(default=0)
    choice2_vote_count = models.IntegerField(default=0)
    choice3_vote_count = models.IntegerField(default=0)
    choice4_vote_count = models.IntegerField(default=0)
    genre = models.CharField(max_length=100, default="General")
    endtime = models.DateTimeField()
    isActive = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Privatepoll(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)
    desc=models.TextField(default="")
    pub_date = models.DateTimeField(default=timezone.now)
    choice1 = models.CharField(max_length=500, default="")
    choice2 = models.CharField(max_length=500, default="")
    choice3 = models.CharField(max_length=500, default="")
    choice4 = models.CharField(max_length=500, default="")
    choice1_vote_count = models.IntegerField(default=0)
    choice2_vote_count = models.IntegerField(default=0)
    choice3_vote_count = models.IntegerField(default=0)
    choice4_vote_count = models.IntegerField(default=0)
    genre = models.CharField(max_length=100, default="General")
    endtime = models.DateTimeField()
    isActive = models.BooleanField(default=True)
    userAccess = models.TextField(default="")

    def __str__(self):
        return f'{self.title} by {self.owner}'


class Publicvote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poll = models.ForeignKey(Publicpoll, on_delete=models.CASCADE)
    choice = models.CharField(max_length=300, default="")

    def __str__(self):
        return f'{self.poll.title[:20]} - {self.user.username} voted for {self.choice}'

class Privatevote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poll = models.ForeignKey(Privatepoll, on_delete=models.CASCADE)
    choice = models.CharField(max_length=300, default="")

    def __str__(self):
        return f'{self.poll.title[:20]} - {self.user.username} voted for {self.choice}'

class Privateinvite(models.Model):
    userinvited = models.ForeignKey(User, on_delete=models.CASCADE)
    poll = models.ForeignKey(Privatepoll, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)
    expiry = models.DateTimeField()
    isActive = models.BooleanField(default=True)
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.poll.owner} invited {self.userinvited.username} to vote for {self.poll.title[:20]}'