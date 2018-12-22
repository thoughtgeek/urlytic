from django.shortcuts import render
from django.conf import settings
from django.db import IntegrityError
from datetime import timedelta
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect
from home.models import Document
from .models import UrlMap, DocProfile
import random

# if not settings.configured:
#     print('notset')

# def get_random(tries):
#     chars='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijnopqrstuvwxyz1234567890'
#     short= ''.join((random.choice(chars)) for x in range(tries))
#     return(short)

def get_random(tries=0):
    length = getattr(settings, 'SHORTENER_LENGTH', 5)
    length += tries

    # Removed l, I, 1
    dictionary = "ABCDEFGHJKLMNOPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz234567890"
    return ''.join(random.choice(dictionary) for _ in range(length))


#New link generator
def generate(document, settings, link):
        # store settings variables
        enabled = settings.enabled
        max_urls = settings.max_urls
        max_concurrent = settings.max_concurrent
        lifespan = settings.lifespan
        max_uses = settings.max_uses
        
        # Ensure enabled
        if not enabled:
            raise PermissionError("not authorized to create shortlinks")

        # Expiry date, -1 to disable
        if lifespan != -1:
            expiry_date = timezone.now() + timedelta(seconds=lifespan)
        else:
            expiry_date = timezone.make_aware(timezone.datetime.max, timezone.get_default_timezone())

        # Ensure user has not met max_urls quota
        # if max_urls != -1:
        #     if UrlMap.objects.filter(user=user).count() >= max_urls:
        #         raise PermissionError("url quota exceeded")

        # Ensure user has not met concurrent urls quota
        # if max_concurrent != -1:
        #     if UrlMap.objects.filter(user=user, date_expired__gt=timezone.now()).count() >= max_concurrent:
        #         raise PermissionError("concurrent quota exceeded")

        # Try up to three times to generate a random number without duplicates.
        # Each time increase the number of allowed characters
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



#FileDetail  view
def filedetail(request):
    filename = request.GET.get('filename')
    domain = getattr(settings, 'DOMAIN_NAME')
    print(domain)

    documents = Document.objects.filter(upload=filename)
    test = filesettings(True, -1, -1, -1, -1)

    for document in documents:
    	uniqueurl = generate(document, test, document.upload.url)
    	generatedurl = domain +'/file/redirect/'+uniqueurl
    	returnedurl = expand(request, uniqueurl)

    return render(request, 'filedetail/filedetail.html', {
            'documents':documents,
            'filename':filename,
            'generatedurl':generatedurl,
            'returnedurl':returnedurl,
        })


