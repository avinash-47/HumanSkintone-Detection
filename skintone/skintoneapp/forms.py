from django import forms
from django.db.models import fields
from .models import UserImageDb,Contact


class UploadForm(forms.ModelForm):

    class Meta:
        model = UserImageDb
        fields = ['name', 'user_image']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'user-box'}),
            'user_image': forms.FileInput(attrs={'class': 'user-box'})
        }    


class ContactForm(forms.ModelForm):

    class Meta:
        model = Contact
        fields = ['name', 'email', 'phoneNumber', 'date']