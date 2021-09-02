from django.contrib import messages
import datetime
from django.contrib.auth import authenticate
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.db.models.functions import Lower
from django.shortcuts import redirect, render
from .models import Publicpoll, Privatepoll, Publicvote, Privatevote, Privateinvite
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse
import os
import face_recognition
import cv2

# Create your views here.


@login_required
def pollshome(request):
    return redirect('publicpolls')


@login_required
def publicPolls(request):
    publicrefresh()
    allPublicPolls = Publicpoll.objects.filter(isActive=True)
    search_term = ''
    if 'name' in request.GET:
        allPublicPolls = allPublicPolls.order_by(Lower('title'))
    if 'mostrecent' in request.GET:
        allPublicPolls = allPublicPolls.order_by('-pub_date')
    if 'oldfirst' in request.GET:
        allPublicPolls = allPublicPolls.order_by('pub_date')
    if 'ending' in request.GET:
        allPublicPolls = allPublicPolls.order_by('endtime')
    if 'General' in request.GET:
        allPublicPolls = allPublicPolls.filter(genre="General")
    if 'Political' in request.GET:
        allPublicPolls = allPublicPolls.filter(genre="Political")
    if 'Entertainment' in request.GET:
        allPublicPolls = allPublicPolls.filter(genre="Entertainment")
    if 'Opinion' in request.GET:
        allPublicPolls = allPublicPolls.filter(genre="Opinion")
    if 'byyou' in request.GET:
        allPublicPolls = allPublicPolls.filter(owner=request.user)
    if 'search' in request.GET:
        search_term = request.GET['search']
        allPublicPollstitle = allPublicPolls.filter(
            title__icontains=search_term)
        allPublicPollsdesc = allPublicPolls.filter(desc__icontains=search_term)
        allPublicPolls = allPublicPollstitle.union(allPublicPollsdesc)
    paginated_publicpolls = Paginator(allPublicPolls, 10)
    page_number = request.GET.get('page')
    poll_page_obj = paginated_publicpolls.get_page(page_number)
    dict = {'allPublicPolls': poll_page_obj, 'search_term': search_term}
    return render(request, 'publicpolls.html', dict)


@login_required
def privatePolls(request):
    privaterefresh()
    allPrivatePolls = Privatepoll.objects.filter(owner=request.user, isActive=True)
    if allPrivatePolls is not None:
        search_term = ''
        if 'name' in request.GET:
            allPrivatePolls = allPrivatePolls.order_by(Lower('title'))
        if 'mostrecent' in request.GET:
            allPrivatePolls = allPrivatePolls.order_by('-pub_date')
        if 'oldfirst' in request.GET:
            allPrivatePolls = allPrivatePolls.order_by('pub_date')
        if 'ending' in request.GET:
            allPrivatePolls = allPrivatePolls.order_by('endtime')
        if 'General' in request.GET:
            allPrivatePolls = allPrivatePolls.filter(genre="General")
        if 'Political' in request.GET:
            allPrivatePolls = allPrivatePolls.filter(genre="Political")
        if 'Entertainment' in request.GET:
            allPrivatePolls = allPrivatePolls.filter(genre="Entertainment")
        if 'Opinion' in request.GET:
            allPrivatePolls = allPrivatePolls.filter(genre="Opinion")
        if 'search' in request.GET:
            search_term = request.GET['search']
            allPrivatePollstitle = allPrivatePolls.filter(
                title__icontains=search_term)
            allPrivatePollsdesc = allPrivatePolls.filter(
                desc__icontains=search_term)
            allPrivatePolls = allPrivatePollstitle.union(
                allPrivatePollsdesc)
        paginated_privatepolls = Paginator(allPrivatePolls, 5)
        page_number = request.GET.get('page')
        poll_page_obj = paginated_privatepolls.get_page(page_number)
        dict = {'allPrivatePolls': poll_page_obj,
                'search_term': search_term}
        return render(request, 'privatepolls.html', dict)
    else:
        messages.warning(request, 'You don\'t have any private polls!')
        return render(request, 'privatepolls.html')


@login_required
def votingHistory(request):
    publicrefresh()
    publicvote = Publicvote.objects.filter(user=request.user)
    votes = publicvote
    if 'private' in request.GET:
        privaterefresh()
        privatevote = Privatevote.objects.filter(user=request.user)
        votes = privatevote
    paginated_votes = Paginator(votes, 10)
    page_number = request.GET.get('page')
    vote_page_obj = paginated_votes.get_page(page_number)
    dict = {'votes': vote_page_obj}
    return render(request, 'votinghistory.html', dict)


def publicrefresh():
    now = datetime.datetime.now()
    outdatedpoll = Publicpoll.objects.raw(
        "select * from polls_Publicpoll where endtime < %s and isActive = True", [now])
    outdatedpoll = list(outdatedpoll)
    for i in range(len(outdatedpoll)):
        outdatedpoll[i].isActive = False
        outdatedpoll[i].save()


def inviterefresh():
    now = datetime.datetime.now()
    invitations = Privateinvite.objects.raw(
        "select * from polls_Privateinvite where expiry < %s and isActive = True", [now])
    invitations = list(invitations)
    for i in range(len(invitations)):
        invitations[i].isActive = False
        invitations[i].save()


def privaterefresh():
    now = datetime.datetime.now()
    outdatedpoll = Privatepoll.objects.raw(
        "select * from polls_Privatepoll where endtime < %s and isActive = True", [now])
    outdatedpoll = list(outdatedpoll)
    for i in range(len(outdatedpoll)):
        outdatedpoll[i].isActive = False
        outdatedpoll[i].save()


@login_required
def createPolls(request):
    return render(request, 'createpolls.html')


@login_required
def createPublicPoll(request):
    if request.method == 'POST':
        # Get the post parameters
        owner = request.user
        title = request.POST['title']
        desc = request.POST['desc']
        choice1 = request.POST['choice1']
        choice2 = request.POST['choice2']
        genre = request.POST['genre']
        endtime = request.POST['endtime']
        now = datetime.datetime.now()
        if endtime < str(now):
            messages.error(
                request, 'Please enter a valid day to end the poll!')
            return render(request, 'createpolls.html')
        if len(title) > 50:
            messages.error(
                request, 'Your title must be under 50 characters!')
            return render(request, 'createpolls.html')
        if len(desc) > 1000:
            messages.error(
                request, 'Your description must be under 1000 characters!')
            return render(request, 'createpolls.html')
        if len(choice1) > 500:
            messages.error(request, 'Your 1st choice is too long!')
            return render(request, 'createpolls.html')
        if len(choice2) > 500:
            messages.error(request, 'Your 2nd choice is too long!')
            return render(request, 'createpolls.html')
        if Publicpoll.objects.filter(title=title, desc=desc, isActive=True).exists():
            messages.error(request, 'Be more creative!')
            return render(request, 'createpolls.html')
        publicpoll = Publicpoll(owner=owner, title=title, desc=desc, isActive=True,
                                endtime=endtime, choice1=choice1, choice2=choice2, genre=genre)
        publicpoll.save()
        messages.success(request, 'Your public poll has been created.')
        return redirect('publicpolls')
    else:
        messages.error(request, 'Error occurred!')
        return redirect('publicpolls')


@login_required
def createPrivatePoll(request):
    if request.method == 'POST':
        # Get the post parameters
        owner = request.user
        title = request.POST['title']
        desc = request.POST['desc']
        choice1 = request.POST['choice1']
        choice2 = request.POST['choice2']
        genre = request.POST['genre']
        endtime = request.POST['endtime']
        now = datetime.datetime.now()
        if endtime < str(now):
            messages.error(
                request, 'Please enter a valid day to end the poll!')
            return render(request, 'createpolls.html')
        if len(title) > 50:
            messages.error(
                request, 'Your title must be under 50 characters!')
            return render(request, 'createpolls.html')
        if len(desc) > 1000:
            messages.error(
                request, 'Your description must be under 1000 characters!')
            return render(request, 'createpolls.html')
        if len(choice1) > 500:
            messages.error(request, 'Your 1st choice is too long!')
            return render(request, 'createpolls.html')
        if len(choice2) > 500:
            messages.error(request, 'Your 2nd choice is too long!')
            return render(request, 'createpolls.html')
        privatepoll = Privatepoll(owner=owner, title=title, desc=desc, isActive=True,
                                  endtime=endtime, choice1=choice1, choice2=choice2, genre=genre)
        privatepoll.save()
        messages.success(request, 'Your private poll has been created.')
        return redirect('privatepolls')
    else:
        messages.error(request, 'Error occurred!')
        return redirect('privatepolls')


@login_required
def editpublicpoll(request, poll_id):
    if request.method == 'POST':
        # Get the post parameters
        password = request.POST['password']
        user = authenticate(username=request.user, password=password)
        if user is not None:
            publicpoll = Publicpoll.objects.filter(owner=request.user, id=poll_id, isActive=True).first()
            if publicpoll is not None:
                title = request.POST['title']
                desc = request.POST['desc']
                choice1 = request.POST['choice1']
                choice2 = request.POST['choice2']
                genre = request.POST['genre']
                endtime = request.POST['endtime']
                if publicpoll.title == title:
                    messages.error(request, 'No change in the title was detected!')
                    return redirect('editpublicpoll', poll_id=poll_id)
                if publicpoll.choice1 == choice1:
                    messages.error(request, 'No change in the 1st choice was detected!')
                    return redirect('editpublicpoll', poll_id=poll_id)
                if publicpoll.choice2 == choice2:
                    messages.error(request, 'No change in the 2nd choice was detected!')
                    return redirect('editpublicpoll', poll_id=poll_id)
                if publicpoll.genre == genre:
                    messages.error(request, 'No change in the genre was detected!')
                    return redirect('editpublicpoll', poll_id=poll_id)
                if publicpoll.endtime == endtime:
                    messages.error(request, 'No change in the expiration date was detected!')
                    return redirect('editpublicpoll', poll_id=poll_id)
                if len(title) > 400:
                    messages.error(
                        request, 'Your title must be under 400 characters!')
                    return redirect('editpublicpoll', poll_id=poll_id)
                if len(desc) > 1000:
                    messages.error(
                        request, 'Your description must be under 1000 characters!')
                    return redirect('editpublicpoll', poll_id=poll_id)
                if len(choice1) > 500:
                    messages.error(request, 'Your 1st choice is too long!')
                    return redirect('editpublicpoll', poll_id=poll_id)
                if len(choice2) > 500:
                    messages.error(request, 'Your 2nd choice is too long!')
                    return redirect('editpublicpoll', poll_id=poll_id)
                if Publicpoll.objects.filter(title=title, desc=desc, isActive=True).exists():
                    messages.error(request, 'Be more creative!')
                    return redirect('editpublicpoll', poll_id=poll_id)
                if title != '':
                    publicpoll.title = title 
                if choice1 != '':
                    publicpoll.choice1 = choice1
                if choice2 != '':
                    publicpoll.choice2 = choice2
                if desc != '':
                    publicpoll.desc == desc
                if genre != '':
                    publicpoll.genre == genre
                if endtime != '':
                    publicpoll.endtime = endtime
                publicpoll.save()
                messages.success(request, 'Changes saved successfully!')
                return redirect('polldetails', poll_id=poll_id)
            else:
                messages.error(request, 'You cannot edit this public poll!')
                return redirect('publicpolls')
        else:
            messages.error(request, 'Invalid Credentials!')
            return redirect('editpublicpoll', poll_id=poll_id)
    else:
        publicrefresh()
        publicpoll = Publicpoll.objects.filter(id=poll_id).first()
        if publicpoll is not None:
            if publicpoll.owner == request.user:
                if publicpoll.isActive:
                    return render(request, 'editpublicpoll.html',{'publicpoll': publicpoll})
                else:
                    messages.error(request, 'The poll is not active anymore :(')
                    return redirect('publicpolls')
            else:
                messages.error(request, 'You cannot edit this public poll!')
                return redirect('publicpolls')
        else:
            messages.error(request, 'No such poll exists :(')
            return redirect('publicpolls')


@login_required
def editprivatepoll(request, poll_id):
    if request.method == 'POST':
        # Get the post parameters
        password = request.POST['password']
        user = authenticate(username=request.user, password=password)
        if user is not None:
            privatepoll = Privatepoll.objects.filter(owner=request.user, id=poll_id, isActive=True).first()
            if privatepoll is not None:
                if facedetect(request):
                    title = request.POST['title']
                    desc = request.POST['desc']
                    choice1 = request.POST['choice1']
                    choice2 = request.POST['choice2']
                    genre = request.POST['genre']
                    endtime = request.POST['endtime']
                    if privatepoll.title == title:
                        messages.error(request, 'No change in the title was detected!')
                        return redirect('editprivatepoll', poll_id=poll_id)
                    if privatepoll.choice1 == choice1:
                        messages.error(request, 'No change in the 1st choice was detected!')
                        return redirect('editprivatepoll', poll_id=poll_id)
                    if privatepoll.choice2 == choice2:
                        messages.error(request, 'No change in the 2nd choice was detected!')
                        return redirect('editprivatepoll', poll_id=poll_id)
                    if privatepoll.genre == genre:
                        messages.error(request, 'No change in the genre was detected!')
                        return redirect('editprivatepoll', poll_id=poll_id)
                    if privatepoll.endtime == endtime:
                        messages.error(request, 'No change in the expiration date was detected!')
                        return redirect('editprivatepoll', poll_id=poll_id)
                    if len(title) > 400:
                        messages.error(
                            request, 'Your title must be under 400 characters!')
                        return redirect('editprivatepoll', poll_id=poll_id)
                    if len(desc) > 1000:
                        messages.error(
                            request, 'Your description must be under 1000 characters!')
                        return redirect('editprivatepoll', poll_id=poll_id)
                    if len(choice1) > 500:
                        messages.error(request, 'Your 1st choice is too long!')
                        return redirect('editprivatepoll', poll_id=poll_id)
                    if len(choice2) > 500:
                        messages.error(request, 'Your 2nd choice is too long!')
                        return redirect('editprivatepoll', poll_id=poll_id)
                    if Privatepoll.objects.filter(title=title, desc=desc, isActive=True).exists():
                        messages.error(request, 'Be more creative!')
                        return redirect('editprivatepoll', poll_id=poll_id)
                    if title != '':
                        privatepoll.title = title 
                    if choice1 != '':
                        privatepoll.choice1 = choice1
                    if choice2 != '':
                        privatepoll.choice2 = choice2
                    if desc != '':
                        privatepoll.desc == desc
                    if genre != '':
                        privatepoll.genre == genre
                    if endtime != '':
                        privatepoll.endtime = endtime
                    privatepoll.save()
                    messages.success(request, 'Changes saved successfully!')
                    return redirect('privatepolldetails', poll_id=poll_id)
                else:
                    messages.error(request, 'Facial authentication failed, please try again.')
                    messages.warning(request, 'Possible Reasons:\n1. Maybe the lighting is dull.\n2. Maybe you need to update your profile image.\n3. Maybe you are pretending to be the logged user!')
                    return redirect('editprivatepoll', poll_id=poll_id)
            else:
                messages.error(request, 'You cannot edit this private poll!')
                return redirect('privatepolls')
        else:
            messages.error(request, 'Invalid Credentials!')
            return redirect('editprivatepoll', poll_id=poll_id)
    else:
        privaterefresh()
        privatepoll = Privatepoll.objects.filter(id=poll_id).first()
        if privatepoll is not None:
            if privatepoll.owner == request.user:
                if privatepoll.isActive:
                    return render(request, 'editprivatepoll.html',{'privatepoll': privatepoll})
                else:
                    messages.error(request, 'The poll is not active anymore :(')
                    return redirect('privatepolls')
            else:
                messages.error(request, 'You cannot edit this private poll!')
                return redirect('privatepolls')
        else:
            messages.error(request, 'No such poll exists :(')
            return redirect('privatepolls')


@login_required
def deletepublicpoll(request, poll_id):
    if request.method == 'POST':
        delete = request.POST['delete']
        if delete == "delete":
            publicrefresh()
            publicpoll = Publicpoll.objects.filter(id=poll_id, isActive=True).first()
            if publicpoll is not None:
                if request.user == publicpoll.owner:
                    publicpoll.isActive = False
                    publicpoll.save()
                    messages.success(
                        request, 'The public poll is deleted successfully!')
                else:
                    messages.error(request, 'You are not the owner of this poll, so you cannot delete it!')
                return redirect('publicpolls')
            else:
                messages.error(request, 'No such poll exists :(')
                return redirect('publicpolls')
        else:
            messages.error(request, 'Invalid choice!')
            return redirect('publicpolls')
    else:
        messages.error(request, 'Error occurred!')
        return redirect('publicpolls')


@login_required
def deleteprivatepoll(request, poll_id):
    if request.method == 'POST':
        delete = request.POST['delete']
        if delete == "delete":
            privaterefresh()
            privatepoll = Privatepoll.objects.filter(id=poll_id, isActive=True).first()
            if privatepoll is not None:
                if request.user == privatepoll.owner:
                    if facedetect(request):
                        privatepoll.isActive = False
                        privatepoll.save()
                        messages.success(request, 'The private poll is deleted successfully!')
                        return redirect('privatepolls')
                    else:
                        messages.error(request, 'Facial authentication failed, please try again.')
                        messages.warning(request, 'Possible Reasons:\n1. Maybe the lighting is dull.\n2. Maybe you need to update your profile image.\n3. Maybe you are pretending to be the logged user!')
                        return redirect('privatepolldetails', poll_id=poll_id)
                else:
                    messages.success(request, 'You are not the owner of this poll, so you cannot delete it!')
                    return redirect('privatepolls')
            else:
                messages.error(request, 'No such poll exists :(')
                return redirect('privatepolls')
        else:
            messages.error(request, 'Invalid choice!')
            return redirect('privatepolls')
    else:
        messages.error(request, 'Error occurred!')
        return redirect('privatepolls')


@login_required
def privateinvite(request, poll_id):
    if request.method == 'POST':
        deleteinvite = request.POST['deleteinvite']
        if deleteinvite == "revoke":
            privaterefresh()
            privatepoll = Privatepoll.objects.filter(id=poll_id, isActive=True).first()
            if privatepoll is not None:
                if request.user == privatepoll.owner:
                    userrevoked = request.POST['userrevoked']
                    reuser = User.objects.filter(username=userrevoked).first()
                    inviterefresh()
                    privateinvite = Privateinvite.objects.filter(userinvited=reuser, poll=privatepoll, isActive=True, is_accepted=False).first()
                    privateinvite.isActive = False
                    privateinvite.save()
                    messages.success(request, 'Invitation revoked!')
                    return redirect('privateinvite', poll_id=poll_id)
                else:
                    messages.error(request, 'You do not have access to revoke invitation for this poll!')
                    return redirect('privatepolls')
            else:
                messages.error(request, 'No such poll exists :(')
                return redirect('privatepolls')
        else:
            messages.error(request, 'Invalid choice!')
            return redirect('privateinvite', poll_id=poll_id)
    else:
        usernames = json.dumps(list(User.objects.values('username')))
        privatepoll = Privatepoll.objects.filter(id=poll_id).first()
        if privatepoll is not None:
            if privatepoll.owner == request.user:
                if privatepoll.isActive:
                    inviterefresh()
                    privateinvites = Privateinvite.objects.filter(poll=privatepoll)
                    dict = {'usernames': usernames, 'privatepoll': privatepoll, 'privateinvites': privateinvites}
                    return render(request, 'privateinvite.html', dict)
                else:
                    messages.error(request, 'The poll is not active anymore :(')
                    return redirect('privatepolls')
            else:
                messages.error(request, 'You do not have access to invite people to this poll.')
                return redirect('privatepolls')
        else:
            messages.error(request, 'No such poll exists :(')
            return redirect('privatepolls')


@login_required
def publicpolldetails(request, poll_id):
    publicrefresh()
    publicpoll = Publicpoll.objects.filter(id=poll_id).first()
    if publicpoll is not None:
        if publicpoll.isActive:
            publicvote = Publicvote.objects.filter(user=request.user, poll=publicpoll).first()
            hasVoted = Publicvote.objects.filter(user=request.user, poll=publicpoll).exists()
            dict = {'publicvote': publicvote, 'poll': publicpoll, 'hasVoted': hasVoted}
            return render(request, 'polldetails.html', dict)
        else:
            messages.error(request, 'The poll is not active anymore :(')
            return redirect('publicpolls')
    else:
        messages.error(request, 'No such poll exists :(')
        return redirect('publicpolls')


@login_required
def privatepolldetails(request, poll_id):
    privaterefresh()
    privatepoll = Privatepoll.objects.filter(id=poll_id).first()
    if privatepoll is not None:
        if f'{request.user}' in privatepoll.userAccess:
            hasAccess = True
        else:
            hasAccess = False
        if privatepoll.owner == request.user or hasAccess == True:
            if privatepoll.isActive:
                privatevote = Privatevote.objects.filter(user=request.user, poll=privatepoll).first()
                hasVoted = Privatevote.objects.filter(user=request.user, poll=privatepoll).exists()
                dict = {'privatevote': privatevote, 'poll': privatepoll, 'hasVoted': hasVoted}
                return render(request, 'privatepolldetails.html', dict)
            else:
                messages.error(
                    request, 'The poll is not active anymore :(')
                return redirect('privatepolls')
        else:
            messages.error(request, 'You do not have access to this poll.')
            return redirect('privatepolls')

    else:
        messages.error(request, 'No such poll exists :(')
        return redirect('privatepolls')


@login_required
def public_vote(request, poll_id):
    if request.method == 'POST':
        publicrefresh()
        publicpoll = Publicpoll.objects.filter(id=poll_id).first()
        if publicpoll is not None:
            if Publicvote.objects.filter(user=request.user, poll=publicpoll).exists():
                messages.warning(request, 'You have already voted for this poll!')
            else:
                choice = request.POST['choice']
                publicvote = Publicvote(user=request.user, poll=publicpoll, choice=choice)
                publicvote.save()
                if choice == publicpoll.choice1:
                    publicpoll.choice1_vote_count += 1
                elif choice == publicpoll.choice2:
                    publicpoll.choice2_vote_count += 1
                publicpoll.save()
                messages.success(request, 'Successfully voted!')
            return redirect('publicresults', poll_id=poll_id)
        else:
            messages.error(request, 'No such poll exists :(')
            return redirect('publicpolls')
    else:
        messages.error(request, 'Error occurred!')
        return redirect('publicpolls')


@login_required
def private_vote(request, poll_id):
    if request.method == 'POST':
        privaterefresh()
        privatepoll = Privatepoll.objects.filter(id=poll_id).first()
        if privatepoll is not None:
            if facedetect(request):
                if Privatevote.objects.filter(user=request.user, poll=privatepoll).exists():
                    messages.warning(
                        request, 'You have already voted for this poll!')
                else:
                    choice = request.POST['choice']
                    privatevote = Privatevote(
                        user=request.user, poll=privatepoll, choice=choice)
                    privatevote.save()
                    if choice == privatepoll.choice1:
                        privatepoll.choice1_vote_count += 1
                    elif choice == privatepoll.choice2:
                        privatepoll.choice2_vote_count += 1
                    privatepoll.save()
                    messages.success(
                        request, 'Facial authentication was successful and you have successfully voted!')
                return redirect('privateresults', poll_id=poll_id)
            else:
                messages.error(
                    request, 'Facial authentication failed, please try again.')
                messages.warning(
                    request, 'Possible Reasons:\n1. Maybe the lighting is dull.\n2. Maybe you need to update your profile image.\n3. Maybe you are pretending to be the logged user.')
                return redirect('privatepolldetails', poll_id=poll_id)
        else:
            messages.error(request, 'No such poll exists :(')
            return redirect('privatepolls')
    else:
        messages.error(request, 'Error occurred!')
        return redirect('privatepolls')


@login_required
def private_userinvite(request, poll_id):
    if request.method == 'POST':
        privaterefresh()
        privatepoll = Privatepoll.objects.filter(id=poll_id).first()
        if privatepoll is not None:
            if privatepoll.owner == request.user:
                if privatepoll.isActive:
                    userinvited = request.POST['userinvited']
                    userin = User.objects.filter(username=userinvited).first()
                    if request.user == userin:
                        messages.warning(
                            request, 'You cannot invite yourself!')
                        return redirect('privateinvite', poll_id=poll_id)
                    inviterefresh()
                    if Privateinvite.objects.filter(userinvited=userin, poll=privatepoll, isActive=True).exists():
                        messages.warning(
                            request, 'This user is already invited!')
                    elif Privateinvite.objects.filter(userinvited=userin, poll=privatepoll, is_accepted=True).exists():
                        messages.warning(
                            request, 'This user has already accepted the invitivation!')
                    else:
                        expiry = datetime.datetime.now() + datetime.timedelta(days=7)
                        privateinvite = Privateinvite(
                            userinvited=userin, poll=privatepoll, expiry=expiry)
                        privateinvite.save()
                        # send userin some notification
                        messages.success(
                            request, 'Invitation sent successfully!')
                        messages.warning(
                            request, 'Note: 1. This invitation will be revoked after 7 days. 2. Once the user accepts the invitation, it can\'t be revoked.')
                    return redirect('privateinvite', poll_id=poll_id)
                else:
                    messages.error(request, 'The poll is not active anymore :(')
                    return redirect('privatepolls')
            else:
                messages.error(
                    request, 'You do not have the permission to invite anyone to this poll!')
                return redirect('privatepolls')
        else:
            messages.error(request, 'No such poll exists :(')
            return redirect('privatepolls')
    else:
        messages.error(request, 'Error occurred!')
        return redirect('privatepolls')


@login_required
def privateinvitations(request):
    if request.method == 'POST':
        deletenotif = request.POST['deletenotif']
        poll_id = request.POST['poll_id']
        if deletenotif == "deletenotif":
            privaterefresh()
            privatepoll = Privatepoll.objects.filter(id=poll_id, isActive=True).first()
            if privatepoll is not None:
                inviterefresh()
                if Privateinvite.objects.filter(userinvited=request.user, poll=privatepoll, isActive=True).exists():
                    privateinvite = Privateinvite.objects.filter(
                        userinvited=request.user, poll=privatepoll, isActive=True).first()
                    privateinvite.isActive = False
                    privateinvite.save()
                    messages.success(request, 'Notification deleted!')
                else:
                    messages.error(request, 'No such invite exists :(')
                return redirect('privateinvitations')
            else:
                messages.error(request, 'No such poll exists :(')
                return redirect('privatepolls')
        else:
            messages.error(request, 'Invalid choice!')
            return redirect('privateinvitations')
    else:
        privaterefresh()
        inviterefresh()
        invitations = Privateinvite.objects.filter(userinvited=request.user, isActive=True)
        if 'latest' in request.GET:
            invitations = invitations.order_by('-created')
        if 'oldest' in request.GET:
            invitations = invitations.order_by('created')
        if 'name' in request.GET:
            invitations = invitations.order_by(-Lower('poll'))
        if 'accepted' in request.GET:
            invitations = invitations.filter(is_accepted = True)
        if 'noaction' in request.GET:
            invitations = invitations.filter(is_accepted = False)
        paginated_invitations = Paginator(invitations, 5)
        page_number = request.GET.get('page')
        invitation_page_obj = paginated_invitations.get_page(page_number)
        return render(request, 'invitations.html', {'invitations': invitation_page_obj})


@login_required
def acceptedinvites(request):
    inviterefresh()
    invitations = Privateinvite.objects.filter(userinvited=request.user)
    if 'latest' in request.GET:
        invitations = invitations.order_by('-created')
    if 'oldest' in request.GET:
        invitations = invitations.order_by('created')
    if 'name' in request.GET:
        invitations = invitations.order_by(-Lower('poll'))
    paginated_invitations = Paginator(invitations, 5)
    page_number = request.GET.get('page')
    invitation_page_obj = paginated_invitations.get_page(page_number)
    return render(request, 'acceptedinvites.html', {'invitations': invitation_page_obj})


@login_required
def invitechoice(request, poll_id):
    if request.method == 'POST':
        invitechoice = request.POST['invitechoice']
        privaterefresh()
        privatepoll = Privatepoll.objects.filter(id=poll_id, isActive=True).first()
        if privatepoll is not None:
            inviterefresh()
            if invitechoice == "accept":
                if Privateinvite.objects.filter(userinvited=request.user, poll=privatepoll, is_accepted=True, isActive=True).exists():
                    messages.warning(request, 'You have already accepted this invite!')
                    return redirect('privateinvitations')
                elif Privateinvite.objects.filter(userinvited=request.user, poll=privatepoll, is_accepted=False, isActive=True).exists():
                    privateinvite = Privateinvite.objects.filter(
                        userinvited=request.user, poll=privatepoll, is_accepted=False, isActive=True).first()
                    privateinvite.is_accepted = True
                    privateinvite.save()
                    privatepoll.userAccess += f' {request.user}'
                    privatepoll.save()
                    messages.success(request, 'Invitation accepted!')
                    return redirect('acceptedinvites')
                else:
                    messages.error(request, 'No such invite exists :(')
                    return redirect('privateinvitations')
            elif invitechoice == "reject":
                if Privateinvite.objects.filter(userinvited=request.user, poll=privatepoll, is_accepted=True, isActive=True).exists():
                    messages.warning(request, 'You have already accepted this invite!')
                    return redirect('privateinvitations')
                elif Privateinvite.objects.filter(userinvited=request.user, poll=privatepoll, is_accepted=False, isActive=True).exists():
                    privateinvite = Privateinvite.objects.filter(
                        userinvited=request.user, poll=privatepoll, is_accepted=False, isActive=True).first()
                    privateinvite.isActive = False
                    privateinvite.save()
                    messages.success(request, 'Invitation rejected!')
                    return redirect('privateinvitations')
                else:
                    messages.error(request, 'No such invite exists :(')
                    return redirect('privateinvitations')
            else:
                messages.success(request, 'Invalid choice!')
                return redirect('privateinvitations')
        else:
            messages.error(request, 'No such poll exists :(')
            return redirect('privateinvitations')
    else:
        messages.error(request, 'Error occurred!')
        return redirect('privateinvitations')


# results

@login_required
def public_results(request, poll_id):
    publicrefresh()
    publicpoll = Publicpoll.objects.filter(id=poll_id).first()
    if publicpoll is not None:
        if publicpoll.isActive:
            hasVoted = Publicvote.objects.filter(user=request.user, poll=publicpoll).exists()
            if hasVoted:
                publicvote = Publicvote.objects.filter(user=request.user, poll=publicpoll).first()
                dict = {'publicpoll': publicpoll, 'publicvote': publicvote}
                return render(request, 'publicresults.html', dict)
            else:
                messages.error(request, 'Please cast your vote first to see the results!')
                return redirect('polldetails', poll_id=poll_id)
        else:
            messages.error(request, 'The poll is not active anymore :(')
            return redirect('publicpolls')
    else:
        messages.error(request, 'No such poll exists :(')
        return redirect('publicpolls')


@login_required
def private_results(request, poll_id):
    privaterefresh()
    privatepoll = Privatepoll.objects.filter(id=poll_id).first()
    if privatepoll is not None:
        if f'{request.user}' in privatepoll.userAccess:
            hasAccess = True
        else:
            hasAccess = False
        if privatepoll.owner == request.user or hasAccess == True:
            if privatepoll.isActive:
                hasVoted = Privatevote.objects.filter(user=request.user, poll=privatepoll).exists()
                if hasVoted:
                    privatevote = Privatevote.objects.filter(user=request.user, poll=privatepoll).first()
                    dict = {'privatepoll': privatepoll, 'privatevote': privatevote}
                    return render(request, 'privateresults.html', dict)
                else:
                    messages.error(request, 'Please cast your vote first to see the results!')
                    return redirect('privatepolldetails', poll_id=poll_id)
            else:
                messages.error(request, 'The poll is not active anymore :(')
                return redirect('privatepolls')
        else:
            messages.error(request, 'You do not have access to this poll.')
            return redirect('privatepolls')
    else:
        messages.error(request, 'No such poll exists :(')
        return redirect('privatepolls')


# charts api
@login_required
def publicResultData(request, poll_id):
    publicrefresh()
    publicpoll = Publicpoll.objects.filter(id=poll_id).first()
    if publicpoll is not None:
        choices = [{publicpoll.choice1 : publicpoll.choice1_vote_count}, {publicpoll.choice2 : publicpoll.choice2_vote_count}]
        return JsonResponse(choices, safe=False)
    else:
        messages.error(request, 'No such poll exists :(')
        return redirect('publicpolls')


@login_required
def privateResultData(request, poll_id):
    privaterefresh()
    privatepoll = Privatepoll.objects.filter(id=poll_id).first()
    if privatepoll is not None:
        choices = [{privatepoll.choice1 : privatepoll.choice1_vote_count}, {privatepoll.choice2 : privatepoll.choice2_vote_count}]
        return JsonResponse(choices, safe=False)
    else:
        messages.error(request, 'No such poll exists :(')
        return redirect('privatepolls')


# facial authentication

@login_required
def facedetect(request):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MEDIA_ROOT = os.path.join(BASE_DIR, 'register')

    img = (str(MEDIA_ROOT)+request.user.userprofile.head_shot.url)
    save_path = (str(MEDIA_ROOT)+f'\\media\\userrecog\\{request.user}.png')

    camera = cv2.VideoCapture(0)
    i = 0
    while i < 1:
        return_value, image = camera.read()
        cv2.imwrite(save_path, image)
        i += 1
    del(camera)
    cv2.destroyAllWindows()

    picture_of_user = face_recognition.load_image_file(img)
    my_face_encoding = face_recognition.face_encodings(picture_of_user)[0]

    try:
        unknown_picture = face_recognition.load_image_file(save_path)
        unknown_face_encoding = face_recognition.face_encodings(unknown_picture)[
            0]
    except:
        return False
    else:
        results = face_recognition.compare_faces(
            [my_face_encoding], unknown_face_encoding)

        if results[0] == True:
            return True
        else:
            return False
