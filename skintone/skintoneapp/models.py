from datetime import date
from django.db import models

# Create your models here.
class UserImageDb(models.Model):
    name = models.CharField(max_length=120)
    user_image = models.ImageField(upload_to='user_image/')


    def __str__(self):
        return self.name


class Contact(models.Model):
    name = models.CharField(max_length=120 , null=True)
    email = models.EmailField(max_length=50 , null=True)
    phoneNumber = models.CharField(max_length=12, null=True)
    date = models.DateField()

    def __str__(self):
        return self.name        

