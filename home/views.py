import random
from django.http import QueryDict
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .models import Document
from .forms import DocumentForm, UserRegistrationForm


def home(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/accounts/login')

    if request.user.is_authenticated:
        if request.method == 'POST':
            form = DocumentForm(request.POST, request.FILES)
            if form.is_valid():
                documentform_unsaved  = form.save(commit=False)
                documentform_unsaved.uploader = request.user
                documentform_unsaved.save()
                # return redirect('home:home')
                response = render(request, 'home/home.html', {'form': form,})
                response.set_cookie('message', "uploaded") 
                return response
        else:
            form = DocumentForm()

        return render(request, 'home/home.html', {
            'form': form,
        })


@login_required
@csrf_exempt
def filelist(request):
    documents = Document.objects.all()
    if request.method == 'DELETE':
        delFile = str(QueryDict(request.body).get('delFile'))
        try:
            delFile = str(QueryDict(request.body).get('delFile'))
            Document.objects.filter(upload=delFile).delete()
            default_storage.delete(delFile)
            print('File deleted successfully!')
        except:
            print('Error in file deletion!')
    return render(request, 'home/filelist.html', {
        'documents':documents,
        'user_email':request.user.email,
    })


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            userObj = form.cleaned_data
            email =  userObj['email']
            auth_token = token_generator()
            while User.objects.filter(username=auth_token).exists():
                auth_token = token_generator()
            if not User.objects.filter(email=email).exists():
                User.objects.create_user(auth_token, email, auth_token)
                return render(request, 'home/register_success.html',
                              {'auth_token' : auth_token})
            else:
                raise forms.ValidationError('Looks like a user with that email already exists')
    else:
        form = UserRegistrationForm()
    return render(request, 'home/register.html', {
        'form' : form,
        'user_email':request.user.email,
    })


def log_out(request):
    logout(request)
    return render(request, 'registration/logout.html')

def token_generator():
    chars='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijnopqrstuvwxyz1234567890'
    auth_token= ''.join((random.choice(chars)) for x in range(10))
    return(auth_token)