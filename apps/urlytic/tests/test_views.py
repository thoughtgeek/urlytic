import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.test import TestCase
from django.http import HttpResponseRedirect
from .test_models import UrlMap_test
from ..views import *

#Test expand view
class Expand_test(TestCase):
	#Check for shortlink that does not exist
	def test_expand_doesnotexist(self):
		#Title for error page
		error_title = 'Access Error - Invalid shortlink'
		url = reverse('shortlink', kwargs={'link':'randomtitle'})
		response = self.client.get(url)
		soup = BeautifulSoup(response.content, 'html.parser')
		title_returned = soup.title.string
		self.assertEqual(response.status_code, 200)
		self.assertEqual(title_returned.strip('\n'), error_title)
	
	#Check for shortlink that is not enabled
	def test_expand_notenabled(self):
		#Title for error page
		error_title = 'Access Error - Shortlink disabled'
		UrlMap_test_instance = UrlMap_test()
		UrlMap_instance = UrlMap_test_instance.create_UrlMap()
		UrlMap_instance.enabled = 'False'
		UrlMap_instance.save()
		url = reverse('shortlink', kwargs={'link':UrlMap_instance.short_url})
		response = self.client.get(url)
		soup = BeautifulSoup(response.content, 'html.parser')
		title_returned = soup.title.string
		self.assertEqual(response.status_code, 200)
		self.assertEqual(title_returned.strip('\n'), error_title)

	#Check if maximum number usages has exceeded
	def test_expand_maxusage(self):
		#Title for error page
		error_title = 'Access Error - Max usages for link reached'
		UrlMap_test_instance = UrlMap_test()
		UrlMap_instance = UrlMap_test_instance.create_UrlMap()
		UrlMap_instance.max_count = '3'
		UrlMap_instance.usage_count = '3'
		UrlMap_instance.save()
		url = reverse('shortlink', kwargs={'link':UrlMap_instance.short_url})
		response = self.client.get(url)
		soup = BeautifulSoup(response.content, 'html.parser')
		title_returned = soup.title.string
		self.assertEqual(response.status_code, 200)
		self.assertEqual(title_returned.strip('\n'), error_title)

	#Check if lifespan of link exceeded
	def test_expand_linkexpired(self):
		#Title for error page
		error_title = 'Access Error - Shortlink expired'
		UrlMap_test_instance = UrlMap_test()
		UrlMap_instance = UrlMap_test_instance.create_UrlMap()
		UrlMap_instance.lifespan = 120
		UrlMap_instance.date_expired = UrlMap_instance.date_expired - timedelta(seconds=60)
		UrlMap_instance.save()
		url = reverse('shortlink', kwargs={'link':UrlMap_instance.short_url})
		response = self.client.get(url)
		soup = BeautifulSoup(response.content, 'html.parser')
		title_returned = soup.title.string
		self.assertEqual(response.status_code, 200)
		self.assertEqual(title_returned.strip('\n'), error_title)	

	#Check link is correctly redirected
	def test_expand_checkredirect(self):
		UrlMap_test_instance = UrlMap_test()
		UrlMap_instance = UrlMap_test_instance.create_UrlMap()
		UrlMap_instance.webhook = None
		UrlMap_instance.save()
		url = reverse('shortlink', kwargs={'link':UrlMap_instance.short_url})
		domain = getattr(settings, 'DOMAIN_NAME', 'http://127.0.0.1:8000')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 302)
		self.assertTrue(isinstance(response, HttpResponseRedirect))
		self.assertEqual(response.get('location'), UrlMap_instance.full_url)

	#Check webhook if WEBHOOK_LINK set in test settings
	def test_expand_checkwebhook(self):
		try:
			webhook_link = getattr(settings, 'WEBHOOK_LINK')
			UrlMap_test_instance = UrlMap_test()
			UrlMap_instance = UrlMap_test_instance.create_UrlMap()
			UrlMap_instance.webhook = webhook_link
			UrlMap_instance.save()
			url = reverse('shortlink', kwargs={'link':UrlMap_instance.short_url})
			response = self.client.get(url)
			self.assertEqual(response.status_code, 302)
		except AttributeError:
			raise AttributeError('WEBHOOK_LINK is not defined in the settings file.'
			  				 	 'Please use /settings/test.py with WEBHOOK_LINK set')

	