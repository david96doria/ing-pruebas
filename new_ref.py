# Import required modules
import cv2
from time import sleep
from picamera import PiCamera

# Create a camera object and define
# some global configuration variables
camera = PiCamera()
dst = "./images/imgref.jpg" # Path where the reference photo will be stored.

# Start taking photos:
camera.start_preview()
camera.capture(dst)
camera.stop_preview()
print("New reference image was saved successfully!")

# Crop the images
#img = cv2.imread(dst,0)
#print(img.shape)
#x = 250
#y = 110
#w = 1280 - x
#h = 720  - y
#crop = img[y:y+h, x:x+w]
#cv2.imshow("Cropped", crop)
#cv2.waitKey(0)
