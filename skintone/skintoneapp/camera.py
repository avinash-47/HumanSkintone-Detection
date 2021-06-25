import cv2,os,urllib.request
import numpy as np
from django.shortcuts import redirect, render
from django.conf import settings
face_detection_videocam = cv2.CascadeClassifier(os.path.join(
			settings.BASE_DIR,'opencv_haarcascade_data/haarcascade_frontalface_default.xml'))

class VideoCamera(object):
	def __init__(self):
		self.video = cv2.VideoCapture(0)

	def get_frame(self):
		img_counter=0
		while True:
			success, image = self.video.read()
			if not success:
				print("failed to grab frame")
				break
			cv2.imshow("Take Photo",image)

			k=cv2.waitKey(1)
			if k%256==27:
				print("Esc hit, closing...")
				break
			elif k%256==32:
				img_name = '../skintone/static/images/opencv_frame_{}.png'.format(img_counter)
				cv2.imwrite(img_name,image)
				print("{} written!".format(img_name))
				break
		self.video.release()
		cv2.destroyAllWindows()