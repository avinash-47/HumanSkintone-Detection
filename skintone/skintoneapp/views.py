import sqlite3
import os
from os import listdir
from os.path import isfile, join
from datetime import date
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from .forms import *
from datetime import datetime
from .models import Contact, UserImageDb
from .camera import VideoCamera
from django.http.response import StreamingHttpResponse
import numpy as np
import cv2
from sklearn.cluster import KMeans
from collections import Counter
import imutils
from matplotlib import pyplot as plt
from django.conf import settings

# Create your views here.

def Home(request):
    return render(request, 'index.html')


def upload(request):
    o = [f for f in listdir("./media/user_image/") if isfile(join("./media/user_image/", f))]
    location = "./media/user_image/"
    
    if len(o)!=0:
        file = o[0]
        path = os.path.join(location, file)
        os.remove(path) 
        conn = sqlite3.connect(settings.BASE_DIR / 'db.sqlite3')
        c = conn.cursor()
        c.execute('DELETE FROM skintoneapp_userimagedb;',)
        conn.commit()
        conn.close()

    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('result')   
    else:
        form = UploadForm()           
    return render(request, 'upload.html', {'form' : form})

def video(request):
	return render(request,'video.html')

def image(request):
	return render(request,'image.html')

def success(request):
    return HttpResponse('Successfully Uploaded')    

def thankYou(request):
    return render(request, 'thankyou.html')


def capture(request):
    return render(request, 'captureimage.html')    


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phoneNumber = request.POST.get('phoneNumber')

        contact = Contact(name=name, email=email, phoneNumber = phoneNumber, date = datetime.today() )
        contact.save()
        return redirect('thankyou')
                
    return render(request, 'contact.html')    


def gen(camera):
	while True:
		frame = camera.get_frame()
		yield (b'--frame\r\n'
				b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def video_feed(request):
	return StreamingHttpResponse(gen(VideoCamera()),
					content_type='multipart/x-mixed-replace; boundary=frame')


def result(request):
    
    form = UserImageDb.objects.latest('name')
    o = [f for f in listdir("./media/user_image/") if isfile(join("./media/user_image/", f))]
    img = cv2.imread("./media/user_image/"+o[0])
    add="./media/user_image/"+o[0]
    rgb_lower = [45,34,30]
    rgb_higher = [255,206,180]

    
    skin_shades = {
        'Dark' : [rgb_lower,[145,114,100]],
        'Mild' : [[145,114,100],[180,128,130]],
        'Fair':[[180,128,130],rgb_higher]
    }

    convert_skintones = {}
    for shade in skin_shades:
        convert_skintones.update({
            shade : [
                (skin_shades[shade][0][0] * 256 * 256) + (skin_shades[shade][0][1] * 256) + skin_shades[shade][0][2],
                (skin_shades[shade][1][0] * 256 * 256) + (skin_shades[shade][1][1] * 256) + skin_shades[shade][1][2]
            ]
        })


    def extractSkin(image):
        img = image.copy()
        black_img = np.zeros((img.shape[0],img.shape[1],img.shape[2]),dtype=np.uint8)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        lower_threshold = np.array([0, 48, 80], dtype=np.uint8)
        print(lower_threshold)
        upper_threshold = np.array([20, 255, 255], dtype=np.uint8)
        print(upper_threshold)

        skinMask = cv2.inRange(img, lower_threshold, upper_threshold)
        skin = cv2.bitwise_and(img, img, mask=skinMask)
        return cv2.cvtColor(skin, cv2.COLOR_HSV2BGR)


    def removeBlack(estimator_labels, estimator_cluster):
        hasBlack = False
        occurance_counter = Counter(estimator_labels)
        def compare(x, y): return Counter(x) == Counter(y)
        for x in occurance_counter.most_common(len(estimator_cluster)):
            color = [int(i) for i in estimator_cluster[x[0]].tolist()]
            if compare(color, [0, 0, 0]) == True:
                del occurance_counter[x[0]]
                hasBlack = True
                estimator_cluster = np.delete(estimator_cluster, x[0], 0)
                break
        return (occurance_counter, estimator_cluster, hasBlack)


    def getColorInformation(estimator_labels, estimator_cluster, hasThresholding=False):
        occurance_counter = None
        colorInformation = []
        hasBlack = False


        if hasThresholding == True:
            (occurance, cluster, black) = removeBlack(
                estimator_labels, estimator_cluster)
            occurance_counter = occurance
            estimator_cluster = cluster
            hasBlack = black
        else:
            occurance_counter = Counter(estimator_labels)
        totalOccurance = sum(occurance_counter.values())
        for x in occurance_counter.most_common(len(estimator_cluster)):
            index = (int(x[0]))
            index = (index-1) if ((hasThresholding & hasBlack)
                                  & (int(index) != 0)) else index
            color = estimator_cluster[index].tolist()
            color_percentage = (x[1]/totalOccurance)
            colorInfo = {"cluster_index": index, "color": color,
                         "color_percentage": color_percentage}
            colorInformation.append(colorInfo)
        return colorInformation


    def extractDominantColor(image, number_of_colors=1, hasThresholding=False):
        if hasThresholding == True:
            number_of_colors += 1
        img = image.copy()
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = img.reshape((img.shape[0]*img.shape[1]), 3)
        estimator = KMeans(n_clusters=number_of_colors, random_state=4)
        estimator.fit(img)
        colorInformation = getColorInformation(
            estimator.labels_, estimator.cluster_centers_, hasThresholding)
        return colorInformation


    def plotColorBar(colorInformation):
        color_bar = np.zeros((100, 500, 3), dtype="uint8")
        top_x = 0
        for x in colorInformation:
            bottom_x = top_x + (x["color_percentage"] * color_bar.shape[1])
            color = tuple(map(int, (x['color'])))
            cv2.rectangle(color_bar, (int(top_x), 0),
                          (int(bottom_x), color_bar.shape[0]), color, -1)
            top_x = bottom_x
        return color_bar

    image = imutils.resize(img, width=250)
    plt.subplot(3, 1, 1)
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.title("Original Image")

    skin = extractSkin(image)

    plt.subplot(3, 1, 2)
    plt.imshow(cv2.cvtColor(skin, cv2.COLOR_BGR2RGB))
    plt.title("Thresholded  Image")

    unprocessed_dominant = extractDominantColor(skin, number_of_colors=1, hasThresholding=True)

    decimal_lower = (rgb_lower[0] * 256 * 256) + (rgb_lower[1] * 256) + rgb_lower[2]
    decimal_higher = (rgb_higher[0] * 256 * 256) + (rgb_higher[1] * 256) + rgb_higher[2]
    dominantColors = []
    for clr in unprocessed_dominant:
        clr_decimal = int((clr['color'][0] * 256 * 256) + (clr['color'][1] * 256) + clr['color'][2])
        if clr_decimal in range(decimal_lower,decimal_higher+1):
            clr['decimal_color'] = clr_decimal
            dominantColors.append(clr)

    skin_tones = []

    if len(dominantColors) == 0:
        skin_tones.append('Dark')
    else:
        for color in dominantColors:
            for shade in convert_skintones:
                
                if color['decimal_color'] in range(convert_skintones[shade][0],convert_skintones[shade][1]+1):
                    skin_tones.append(shade)
    
    result =str(skin_tones)
  
    return render(request, 'result.html', {'form': form, 'result': result, 'add' : add})                                  


def contactHome(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phoneNumber = request.POST.get('phoneNumber')

        contact = Contact(name=name, email=email, phoneNumber = phoneNumber, date = datetime.today() )
        contact.save()
        return redirect('thankyou')
                
    return render(request, 'index.html')       