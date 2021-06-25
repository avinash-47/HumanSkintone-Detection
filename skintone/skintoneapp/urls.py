from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from skintoneapp import views

urlpatterns = [
    path('', views.Home, name='home'),
    path('upload', views.upload, name='upload'),
    path('success', views.success, name='success'),
    path('capture', views.capture, name='capture'),
    path('contact', views.contact, name='contact'),
    path('video', views.video,name='video'),
    path('image', views.image,name='image'),
    path('video_feed', views.video_feed,name='video_feed'),
    path('result', views.result,name='result'),
    path('thankyou', views.thankYou,name='thankyou'),
    path('contactHome', views.contactHome,name='contactHome'),
]
