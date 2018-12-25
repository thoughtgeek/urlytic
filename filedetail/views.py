from django.shortcuts import render
from django.conf import settings
from django.db import IntegrityError
from datetime import timedelta, datetime
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect
from home.models import Document
from .models import UrlMap, DocProfile
from django.views.decorators.csrf import csrf_exempt
import random

#Random generator
def get_random(tries=0):
    length = getattr(settings, 'SHORTENER_LENGTH', 5)
    length += tries
    # Removed l, I, 1
    dictionary = "ABCDEFGHJKLMNOPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz234567890"
    return ''.join(random.choice(dictionary) for _ in range(length))


#New link generator
def generate(document, filesettings, link):
        # store settings variables
        linkenabled = filesettings.enabled
        lifespan = filesettings.lifespan
        max_uses = filesettings.max_uses
      
        #Expiry date, -1 to disable
        if lifespan != -1:
            expiry_date = timezone.now() + timedelta(seconds=lifespan)
        else:
            expiry_date = timezone.make_aware(timezone.datetime.max, timezone.get_default_timezone())

        #Try up to three times to generate a random number without duplicates.
        #Each time increase the number of allowed characters
        for tries in range(3):
            try:
                short = get_random(tries)
                m = UrlMap(document=document, full_url=link, short_url=short, max_count=max_uses, date_expired=expiry_date, enabled=linkenabled, lifespan=lifespan)
                m.save()
                return m.short_url
            except IntegrityError:
                continue
        raise KeyError("Could not generate unique shortlink")



#Link expander
def expand(request, link):
    try:
        url = UrlMap.objects.get(short_url__exact=link)
    except UrlMap.DoesNotExist:
        raise KeyError("invalid shortlink")
    #Ensure enabled
    if url.enabled == 'False':
        raise PermissionError("shortlink disabled")
    # ensure we are within usage counts
    if url.max_count != -1:
        if url.max_count <= url.usage_count:
            raise PermissionError("max usages for link reached")
    # ensure we are within allowed datetime
    if timezone.now() > url.date_expired:
        raise PermissionError("shortlink expired")

    url.usage_count += 1
    url.save()
    return HttpResponseRedirect(url.full_url)


#FileInfo query function
def fileinfo(document):
    selectedfilemaps = UrlMap.objects.filter(document=document)
    domain = getattr(settings, 'DOMAIN_NAME', 'http://127.0.0.1:8000')
    for selectedfilemap in selectedfilemaps:
        selectedfilemap.short_url = domain + '/file/redirect/'+ selectedfilemap.short_url
        selectedfilemap.max_uses = selectedfilemap.max_count
        if selectedfilemap.lifespan == -1:
            selectedfilemap.date_expired = 'Never'
            selectedfilemap.lifespan = 'Infinite'
        if selectedfilemap.max_uses == -1:
            selectedfilemap.max_uses = 'Unlimited'    
    return selectedfilemaps


#Generate output map
class renderinfo(object):
    def __init__(self, filename):
        selectedfiles = Document.objects.filter(upload=filename)
        for selectedfile in selectedfiles:
            self.document = selectedfile
            self.fileinfo = fileinfo(selectedfile)



#FileSettings class
class link_settings(object):
    def __init__(self, enabled, lifespan, max_uses):
        self.enabled = enabled
        self.lifespan = lifespan
        self.max_uses = max_uses


#FileDetail View
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
    filedetails = renderinfo(filename)

    if gen_api_input == 'True':
        print('Generating new link..')
        default_file_settings = link_settings('True', -1, -1)
        uniqueurl = generate(filedetails.document, default_file_settings, filedetails.document.upload.url)

    return render(request, 'filedetail/filedetail.html',{
                  'selectedfile':filedetails,
        })
