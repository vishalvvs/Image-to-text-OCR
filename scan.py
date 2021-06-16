# NOTE : Run this python file in Command Prompt/Terminal
# USAGE - Go to the directory where the source files are kept via Command Prompt/Terminal. Then run the following command.
# python scan.py 
# Don't Forget to change the path of file to open the document at line 145.

# import the necessary packages
from pypower.transform import four_point_transform
from skimage.filters import threshold_local
import numpy as np
import cv2
import imutils
import tkinter
from tkinter import filedialog
import pytesseract
import os

# Path of working folder on Disk
src_path = "./"
def get_string(img_path):
    # Read image with opencv
    img = cv2.imread(img_path)
    
    # Convert to gray
    img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    # Apply dilation and erosion to remove some noise
    kernel = np.ones((1, 1), np.uint8)
    img = cv2.dilate(img, kernel, iterations=1)
    img = cv2.erode(img, kernel, iterations=1)

    # Apply threshold to get image with only black and white
    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)

    # Recognize text with tesseract for python
    result = pytesseract.image_to_string(img)

    return(result)


#initiate tkinker and hide window 
main_win = tkinter.Tk() 
main_win.withdraw()

main_win.overrideredirect(True)
main_win.geometry('0x0+0+0')

main_win.deiconify()
main_win.lift()
main_win.focus_force()

#open file selector 
main_win.sourceFile = filedialog.askopenfilename(filetypes = (("Image Files",("*.jpg","*.png","*.jpeg")),("All Files","*")),parent=main_win, initialdir= "/",
title='Please select a image file')

#close window after selection 
main_win.destroy()

img_path = main_win.sourceFile


# load the image and compute the ratio of the old height
# to the new height, clone it, and resize it
image = cv2.imread(img_path)
ratio = image.shape[0] / 500.0
orig = image.copy()
image = imutils.resize(image, height = 500)

# convert the image to grayscale, blur it, and find edges
# in the image
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (5, 5), 0)
edged = cv2.Canny(gray, 75, 200)

print("\n----- Image Scanning Started -----\n")

# show the original image and the edge detected image
print("STEP 1: Edge Detection")
cv2.imshow("Image", image)
cv2.imshow("Edged", edged)
#cv2.imwrite('./scanned_output/edged.jpg',edged)
cv2.waitKey(0)
cv2.destroyAllWindows()

# find the contours in the edged image, keeping only the
# largest ones, and initialize the screen contour
cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:5]

# loop over the contours
for c in cnts:
	# approximate the contour
	peri = cv2.arcLength(c, True)
	approx = cv2.approxPolyDP(c, 0.02 * peri, True)

	# if our approximated contour has four points, then we
	# can assume that we have found our screen
	if len(approx) == 4:
		screenCnt = approx
		break

# show the contour (outline) of the piece of paper
print("STEP 2: Find contours of paper")
cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 2)
cv2.imshow("Outline", image)
#cv2.imwrite('./scanned_output/outline.jpg',image)
cv2.waitKey(0)
cv2.destroyAllWindows()

# apply the four point transform to obtain a top-down
# view of the original image
warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)

# convert the warped image to grayscale, then threshold it
# to give it that 'black and white' paper effect
warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
T = threshold_local(warped, 11, offset = 10, method = "gaussian")
warped = (warped > T).astype("uint8") * 255


# show the original and scanned images
print("STEP 3: Apply perspective transform")
cv2.imshow("Original", imutils.resize(orig, height = 650))
cv2.imshow("Scanned", imutils.resize(warped, height = 650))
cv2.waitKey(0)
cv2.destroyAllWindows()

#Write the Scanned Output into an image file
print("\n------ Saving the Scanned Image -------")
cv2.imwrite('./scanned_output/output.jpg',warped)


x = input("\n----- Do You Want to Recognize Text from the Scanned Image??  [y/n] ------ ")

if(x=='Y' or x=='y'):
    print("\n----- Start recognize text from image -----")
    text = get_string(img_path)
    print(text)
    print("\n------ Writing Recognized Text into File -------\n\n")
    with open("./scanned_output/OCR Text.txt", "w", encoding="utf-8") as f:
        f.write(text)
        f.close()
        
    #change the path of the OCR Text.txt file to open it.
    os.startfile('C:/Users/dqure/Desktop/CamScanner/scanned_output/OCR Text.txt')
    print("------ Done -------")
    
else:
    exit()