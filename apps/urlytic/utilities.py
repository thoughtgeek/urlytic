import random
import pytz
from datetime import timedelta, datetime
from django.utils import timezone
from django.conf import settings
from .models import Document, UrlMap


#Random generator function
def get_random(tries=0):
    length = getattr(settings, 'SHORTENER_LENGTH', 5)
    length += tries
    # Removed l, I, 1
    dictionary = "ABCDEFGHJKLMNOPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz234567890"
    return ''.join(random.choice(dictionary) for _ in range(length))


#New link generator function
def generate(document, filesettings, link, expiry_date=None, webhook=None):
        # store settings variables
        linkenabled = filesettings.enabled
        max_uses = filesettings.max_uses
        lifespan = filesettings.lifespan
      
        #Expiry date, -1 to disable
        if lifespan != '':
            if lifespan != -1:
                expiry_date = timezone.now() + timedelta(seconds=int(lifespan))
            else:
                expiry_date = timezone.make_aware(timezone.datetime.max, timezone.get_default_timezone())
        else:
            expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d %H:%M:%S')
            expiry_date = pytz.utc.localize(expiry_date)
            lifespan = expiry_date - timezone.now()
            lifespan = int(lifespan.total_seconds())
        #Try up to three times to generate a random number without duplicates.
        #Each time increase the number of allowed characters
        for tries in range(3):
            try:
                short = get_random(tries)
                m = UrlMap(document=document, full_url=link, short_url=short, max_count=max_uses, date_expired=expiry_date, enabled=linkenabled, lifespan=lifespan, webhook=webhook)
                m.save()
                return m.short_url
            except IntegrityError:
                continue
        raise KeyError("Could not generate unique shortlink")


#Token generator function
def token_generator():
    chars='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijnopqrstuvwxyz1234567890'
    auth_token= ''.join((random.choice(chars)) for x in range(10))
    return(auth_token)


#FileInfo query function
def fileinfo(document):
    selectedfilemaps = UrlMap.objects.filter(document=document)
    domain = getattr(settings, 'DOMAIN_NAME', 'http://127.0.0.1:8000')
    for selectedfilemap in selectedfilemaps:
        selectedfilemap.short_url = domain + '/redirect/'+ selectedfilemap.short_url
        selectedfilemap.max_uses = selectedfilemap.max_count
        if selectedfilemap.lifespan == -1:
            selectedfilemap.date_expired = 'Never'
            selectedfilemap.lifespan = 'Infinite'
        if selectedfilemap.max_uses == -1:
            selectedfilemap.max_uses = 'Unlimited'    
    return selectedfilemaps


#Template template information class
class RenderInfo(object):
    def __init__(self, filename):
        selectedfiles = Document.objects.filter(upload=filename)
        for selectedfile in selectedfiles:
            self.document = selectedfile
            self.fileinfo = fileinfo(selectedfile)


#FileSettings class
class LinkSettings(object):
    def __init__(self, enabled, lifespan, max_uses):
        self.enabled = enabled
        self.lifespan = lifespan
        self.max_uses = max_uses