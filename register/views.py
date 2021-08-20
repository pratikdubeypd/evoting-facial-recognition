from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile, Contact
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
import os
import face_recognition
import cv2

# Create your views here.


def home(request):
    return render(request, 'home.html')


def userLogin(request):
    if request.method == 'POST':
        # Get the post parameters
        loginusername = request.POST['loginusername']
        password = request.POST['password']
        next = request.POST['next']
        # Check the user
        user = authenticate(username=loginusername, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You have successfully logged in!')
            if next:
                return redirect(next)
            return redirect('home')
        else:
            messages.error(request, 'Invalid Credentials!')
            return redirect('login')
    return render(request, 'registration/login.html')


def signup(request):
    if request.method == 'POST':
        # Get the post parameters
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        phone = request.POST['phone']
        username = request.POST['username']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        image = request.FILES.get('image')
        bio = request.POST['bio']
        # Check for errorneous inputs
        if len(username) > 40:
            messages.error(
                request, 'Your username must be under 40 characters')
            return redirect('signup')
        if not username.isalnum():
            messages.error(request, 'Your username must be alphanumeric')
            return redirect('signup')
        if pass1 != pass2:
            messages.error(request, 'Passwords do not match')
            return redirect('signup')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('signup')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered!')
            return redirect('signup')
        if UserProfile.objects.filter(phone=phone).exists():
            messages.error(request, 'Phone number already used!')
            return redirect('signup')
        # Create the user
        myuser = User.objects.create_user(username, email, pass1)
        myuser.save()
        useradd = UserProfile(user=myuser, firstname=fname,
                              lastname=lname, phone=phone, head_shot=image, bio=bio)
        useradd.save()
        messages.success(
            request, 'Your account has been successfully created! Please login to continue.')
        return redirect('login')
    return render(request, 'registration/signup.html')


@login_required
def profile(request):
    return render(request, 'profile.html')


@login_required
def editprofile(request):
    if request.method == 'POST':
        password = request.POST['password']
        user = authenticate(username=request.user, password=password)
        if user is not None:
            fname = request.POST['fname']
            lname = request.POST['lname']
            email = request.POST['email']
            phone = request.POST['phone']
            image = request.FILES.get('image')
            bio = request.POST['bio']
            # Check for errorneous inputs
            if request.user.email == email:
                messages.error(request, 'You already have that email associated with your account!')
                return redirect('editprofile')
            if f'{request.user.userprofile.phone}' == f'{phone}':
                messages.error(request, 'You already have that phone number associated with your account!')
                return redirect('editprofile')
            if request.user.userprofile.firstname == fname:
                messages.error(request, 'No change in your first name was detected!')
                return redirect('editprofile')
            if request.user.userprofile.lastname == lname:
                messages.error(request, 'No change in your last name was detected!')
                return redirect('editprofile')
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already registered!')
                return redirect('editprofile')
            try:
                if UserProfile.objects.filter(phone=phone).exists():
                    messages.error(request, 'Phone number already used!')
                    return redirect('editprofile')
            except:
                pass
            user = User.objects.filter(username = request.user).first()
            userprofile = UserProfile.objects.filter(user=user).first()
            if email != '':
                user.email = email
                user.save()
            if fname != '':
                userprofile.firstname = fname 
            if lname != '':
                userprofile.lastname = lname
            if phone != '':
                userprofile.phone = phone
            if image is not None:
                userprofile.head_shot = image
            if bio != '':
                userprofile.bio = bio
            userprofile.save()
            messages.success(request, 'Changes saved successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Invalid Credentials!')
            return redirect('editprofile')
    else:
        return render(request, 'editprofile.html')


@login_required
def userprofile(request, username):
    currentuser = User.objects.filter(username=username).first()
    if request.user == currentuser:
        return redirect('profile')
    return render(request, 'userprofile.html', {'currentuser': currentuser})


def about(request):
    return render(request, 'about.html')


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        desc = request.POST.get('desc', '')
        if len(name) < 2 or len(email) < 3 or len(desc) < 5:
            messages.error(request, 'Please fill the form correctly!')
            return redirect('contact')
        else:
            contact = Contact(name=name, email=email, phone=phone, desc=desc)
            contact.save()
            messages.success(request, 'Your form has been submitted :)')
    return render(request, 'contact.html')


def logoutHandler(request):
    logout(request)
    messages.success(request, 'You have successfully logged out!')
    return redirect('home')


@login_required
def testface(request):
    user = request.user
    if facedetect(user.userprofile.head_shot.url):
        messages.success(request, 'Facial authentication test was successful!')
        return redirect('profile')
    else:
        messages.error(
            request, 'Facial authentication test failed, please try again.')
        messages.warning(
            request, 'Possible Reasons:\n1. Maybe the lighting is dull.\n2. Maybe you need to update your profile image.\n3. Maybe you are pretending to be the logged user.')
        return redirect('profile')


def facedetect(img):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MEDIA_ROOT = os.path.join(BASE_DIR, 'register')

    img = (str(MEDIA_ROOT)+img)
    save_path = (str(MEDIA_ROOT)+'\\media\\userrecog\\userimage.png')

    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
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
