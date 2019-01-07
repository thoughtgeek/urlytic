from django.test import TestCase
from .models import randomizer, Document
from .views import upload
from .forms import DocumentForm
from django.urls import resolve
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.core.files import File
from django.utils.six import BytesIO
from django.core.files.storage import default_storage
import pandas as pd
import json


from PIL import Image
from io import StringIO


def create_image(storage, filename, size=(100, 100), image_mode='RGB', image_format='PNG'):
   """
   Generate a test image, returning the filename that it was saved as.

   If storage is None, the BytesIO containing the image data
   will be passed instead.
   """
   data = BytesIO()
   Image.new(image_mode, size).save(data, image_format)
   data.seek(0)
   if not storage:
       return data
   image_file = ContentFile(data.read())
   return storage.save(filename, image_file)

class UploadImageTests(TestCase):
   def setUp(self):
       super(UploadImageTests, self).setUp()


   def test_valid_form(self):
       '''
       valid post data should redirect with status code 200
       Check if data field updated on page
       '''
       url = reverse('home')
       avatar = create_image(None, 'avatar.png')
       avatar_file = SimpleUploadedFile('back.png', avatar.getvalue())
       data = {'upload': avatar_file}
       response = self.client.post(url, data, follow=True)

       tables = pd.read_html(str(response.content))
       table_json = tables[0].to_json()
       table_dict = json.loads(table_json)
       table_name = table_dict['Name']
       default_storage.delete(table_name['0'])

       self.assertNotEquals(table_name['0'],  'No data.')
       self.assertEquals(response.status_code, 200)
       self.assertTemplateUsed('core/document_form.html')

class views_test(TestCase):

    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/')
        self.assertEqual(found.func, upload)

class models_test(TestCase):

    """
    randomizer function should return filename notequal to
    filename

    """
    def test_randomizer(self):
        filename = 'abcd'
        returned_filename = randomizer(self, filename)
        self.assertNotEqual(filename, returned_filename)

