from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from ..models import *


#Randomizer function should return filename notequal to filename
class RandomizerTest(TestCase):
    def test_randomizer(self):
        filename = 'abcd'
        returned_filename = randomizer(self, filename)
        self.assertNotEqual(filename, returned_filename)


#Document model should return the name of the file
class Document_test(TestCase):
	def create_document(self):
		user = User.objects.create_user(username='testuser',
                                 email='testuser@test.com',
                                 password='testing')
		file_mock = SimpleUploadedFile('test.txt', b'This is test content')
		return Document.objects.create(upload=file_mock, uploader=user)

	def test_document_creation(self):
		document_instance = self.create_document()
		self.assertTrue(isinstance(document_instance, Document))
		self.assertTrue(document_instance.__str__(), 
						document_instance.upload.name)


#UrlMap model should return full url
class UrlMap_test(TestCase):
	def create_UrlMap(self):
		doc_test_inst = Document_test()
		return UrlMap.objects.create(document = doc_test_inst.create_document(),
									 full_url = 'test.fullurl',
									 short_url = 'testshort',
									 usage_count = 0,
									 max_count = -1,
									 lifespan = -1,
									 date_created = timezone.now(),
									 date_expired = timezone.now()+timedelta(seconds=60),
									 enabled = 'True',
									 webhook = 'http://test.webhook')
		
	def test_UrlMap_creation(self):
		UrlMap_instance = self.create_UrlMap()
		self.assertTrue(isinstance(UrlMap_instance, UrlMap))
		self.assertTrue(UrlMap_instance.__str__(),
						UrlMap_instance.full_url)


