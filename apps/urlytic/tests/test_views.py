from bs4 import BeautifulSoup
from django.test import TestCase
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
		self.assertEqual(title_returned.strip('\n'), error_title)
	
	# Check for shortlink that is not enabled	
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
		self.assertEqual(title_returned.strip('\n'), error_title)	
