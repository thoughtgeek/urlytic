from django.shortcuts import render
from django.conf import settings
from django.db import IntegrityError
from datetime import timedelta
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect
from home.models import Document
from .models import UrlMap, DocProfile
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
        enabled = filesettings.enabled
        lifespan = filesettings.lifespan
        max_uses = filesettings.max_uses
        
        #Ensure enabled
        if not enabled:
            raise PermissionError("not authorized to create shortlinks")

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
                m = UrlMap(document=document, full_url=link, short_url=short, max_count=max_uses, date_expired=expiry_date)
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



#Settings class
class filesettings(object):
    def __init__(self, enabled, max_urls, max_concurrent,
                 lifespan, max_uses):
        self.enabled = enabled
        self.max_urls = max_urls
        self.max_concurrent = max_concurrent
        self.lifespan = lifespan
        self.max_uses = max_uses


def fileinfo(document):
    selectedfilemaps = UrlMap.objects.filter(document=document)
    domain = getattr(settings, 'DOMAIN_NAME', 'http://127.0.0.1:8000')
    for selectedfilemap in selectedfilemaps:
        selectedfilemap.short_url = domain + '/file/redirect/'+ selectedfilemap.short_url
        print(selectedfilemap.short_url)
    return selectedfilemaps


#Generate output map
class outputmap(object):
    def __init__(self, filename):
        selectedfiles = Document.objects.filter(upload=filename)
        
        for selectedfile in selectedfiles:
            self.document = selectedfile
            self.fileinfo = fileinfo(selectedfile)


    


# #File info class
# class fileinfo(object):
#     def __init__(self, document):
#         selectedfilemaps = UrlMap.objects.filter(document=document)
#         domain = getattr(settings, 'DOMAIN_NAME', 'http://127.0.0.1:8000')

#         for selectedfilemap in selectedfilemaps:
#             selectedfilemap.short_url = domain + '/file/redirect/'+ selectedfilemap.short_url
#             print(selectedfilemap.short_url)

#         return selectedfilemaps



#FileDetail  view
# def filedetail(request):
#     filename = request.GET.get('filename')
#     domain = getattr(settings, 'DOMAIN_NAME', 'http://127.0.0.1:8000')

#     selectedfiles = Document.objects.filter(upload=filename)

#     for selectedfile in selectedfiles:
#         selectedfilemaps = UrlMap.objects.filter(document=selectedfile)

#     # test = filesettings(True, -1, -1, -1, -1)

#     # for document in documents:
#     # 	uniqueurl = generate(document, test, document.upload.url)
#     # 	generatedurl = domain +'/file/redirect/'+ uniqueurl
#     # 	returnedurl = expand(request, uniqueurl)

    # return render(request, 'filedetail/filedetail.html', {
    #         'selectedfiles':selectedfiles,
    #         'selectedfilemaps':selectedfilemaps,
    #     })


def filedetail(request):
    filename = request.GET.get('filename')
    o = outputmap(filename)
    # print(str(o.document)+' '+str(o.short_url)+' '+str(o.full_url)+' '+str(o.lifespan)+' '+str(o.usage_count)+' '+str(o.date_expired))


    return render(request, 'filedetail/filedetail.html',{
                  'selectedfile':o,
        })
