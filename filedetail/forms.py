from django import forms
from .models import UrlMap
from home.models import Document
from django.utils import timezone
import datetime

class CustomLinkForm(forms.Form):
	expires_on = forms.DateTimeField(initial=str(timezone.now())[:16])
	max_uses = forms.CharField(max_length=5)
	lifespan = forms.CharField(max_length=5, label='Lifespan in secs(optional)', required=False)

	def clean(self):
		expires_on = self.cleaned_data['expires_on']
		if expires_on < timezone.now():
			raise forms.ValidationError("The date/time cannot be in the past!")
		return expires_on	


