import requests
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, QueryDict
from .forms import DocumentForm, UserRegistrationForm
from .models import Document, UrlMap
from .forms import CustomLinkForm
from django.urls import reverse
from .utilities import *


#Link expander view
def expand(request, link):
    try:
        url = UrlMap.objects.get(short_url__exact=link)
    except UrlMap.DoesNotExist:
        return render(request, 'filedetail/access_error.html',{
                      'error':"Invalid shortlink",
            })
    #Ensure enabled
    if url.enabled == 'False':
        return render(request, 'filedetail/access_error.html',{
                      'error':"Shortlink disabled",
            })
    # ensure we are within usage counts
    if url.max_count != -1:
        if url.max_count <= url.usage_count:
            return render(request, 'filedetail/access_error.html',{
                          'error':"Max usages for link reached",
                })
    # ensure we are within allowed datetime if lifespan not -1
    if url.lifespan != -1:
        if timezone.now() > url.date_expired:
            return render(request, 'filedetail/access_error.html',{
                          'error':"Shortlink expired",
                })
    
    url.usage_count += 1

    data = {
            'document':url.document.upload.name,
            'shortlink':url.short_url,
            'usage_count':url.usage_count,
            'max_count':url.max_count,
    }

    if url.webhook is not None:
        response = requests.post(url.webhook, json=data)
        print('Webhook triggered. Returned status code:'+str(response.status_code))
    
    url.save()
    return HttpResponseRedirect(url.full_url)


#FileDetail View
@login_required
@csrf_exempt
def filedetail(request):
    if request.method == 'POST':
        enabled = request.POST.get('enabled')
        link = request.POST.get('link')
        file = request.POST.get('file')
        domain = getattr(settings, 'DOMAIN_NAME', 'http://127.0.0.1:8000')
        str_len = len(domain +'/file/redirect/')
        short = link[str_len:]
        file_urlmap = UrlMap.objects.get(short_url__exact=short)
        file_urlmap.enabled = enabled
        file_urlmap.save()

    filename = request.GET.get('filename')
    gen_api_input = request.GET.get('gen')
    filedetails = RenderInfo(filename)

    if gen_api_input == 'True':
        print('Generating new link..')
        default_file_settings = LinkSettings('True', -1, -1)
        uniqueurl = generate(filedetails.document, default_file_settings, filedetails.document.upload.url)

    request.session['current_doc_name'] = filedetails.document.upload.name  
    return render(request, 'filedetail/filedetail.html',{
                  'selectedfile':filedetails,
        })


#CustomLink View
@login_required
def customlink(request):
    if request.method == 'POST':
        form = CustomLinkForm(request.POST)
        documents = Document.objects.filter(upload=request.session['current_doc_name'])
        if form.is_valid():
            expires_on = form.data.get('expires_on')+':00'
            max_uses = form.data.get('max_uses')
            lifespan = form.data.get('lifespan')
            webhook = form.data.get('webhook')

            custom_settings = LinkSettings('True', lifespan, max_uses)
            for document in documents:
                if webhook == '':
                    generated_url = generate(document, custom_settings, document.upload.url, expiry_date=expires_on)
                else:
                    generated_url = generate(document, custom_settings, document.upload.url, expiry_date=expires_on, webhook=webhook)
                        
                doc_name = document.upload.name
            return HttpResponseRedirect(reverse('filedetail_home')+'?filename='+doc_name)
    else:
        form = CustomLinkForm()

    return render(request, 'filedetail/customlink.html',{
                  'form':form,
                  'doc_name':request.session['current_doc_name'],
                  })        

#Homepage view
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
                response = render(request, 'home/home.html', {'form': form,})
                response.set_cookie('message', "uploaded") 
                return response
        else:
            form = DocumentForm()

        return render(request, 'home/home.html', {
            'form': form,
        })

#Filelist view
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

#Registration view
@login_required
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

#LogOut view
@login_required
def log_out(request):
    logout(request)
    return render(request, 'registration/logout.html')
