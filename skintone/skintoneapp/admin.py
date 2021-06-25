from django.contrib import admin
from django.db import models
from skintoneapp.models import UserImageDb,Contact

# Register your models here.
myModels = [UserImageDb, Contact]
admin.site.register(myModels)