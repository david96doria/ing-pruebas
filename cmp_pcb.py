# Import required modules
import cv2
from time import sleep
from picamera import PiCamera
import pandas as pd
from openpyxl import load_workbook
import datetime
import xlrd
import subprocess

date = datetime.datetime.now()

def run(*args):
    return subprocess.check_call(['git'] + list(args))

def push_database(msg):
    run("add", ".")
    run("commit", "-m", msg)
    run("push", "-u", "origin", "master")

def create_file():
    # dataframe Name and Age columns
    df = pd.DataFrame({'Fecha': [],
                       'Modelo': [],
                       'ID':[],
                       'Status':[]
                       })

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter('./database.xlsx', engine='xlsxwriter')

    # Convert the dataframe to an XlsxWriter Excel object.
    df.to_excel(writer, sheet_name='Sheet1', index=False)

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()

def fill_cell(status):
    # new dataframe with same columns
    df = pd.DataFrame({'Fecha': [date.strftime("%Y-%m-%d")],
                       'Modelo': ["Blue TFT"],
                       'ID':[date.microsecond],
                       'Status':[status]
                       })
    # open file and copy existing sheets
    writer = pd.ExcelWriter('./database.xlsx', engine='openpyxl')
    writer.book = load_workbook('./database.xlsx')
    writer.sheets = dict((ws.title, ws) for ws in writer.book.worksheets)

    # read existing file
    reader = pd.read_excel(r'./database.xlsx')
    # write out the new sheet
    df.to_excel(writer,index=False,header=False,startrow=len(reader)+1)
    writer.close()

    # push changes to Bitbucket
    commit_message = 'testing' #date.microsecond + 'fue' + status
    push_database(commit_message)

# create_file()

# Profile 1:
# Centered square PCB [5x5]cm.
#x = 450
#y = 110
#w = 570
#h = 480

# Profile 2:
# Blue boards (TFT Shield + QG8 interface)
x = 250
y = 110
w = 1280 - x
h = 720  - y

# Create a camera object and define
# some global configuration variables
camera = PiCamera()
dst = "./images/imgnew.jpg" # Path where the new photo will be stored.
ref = "./images/imgref.jpg" # Path where the fer image is stored.
errMax    = 1    # Max (%) allowed diff error.

# Start taking photos:
camera.start_preview()
camera.capture(dst)
camera.stop_preview()
print("New photo was saved successfully!")

# Read images from the destination folder
img1 = cv2.imread(dst,0)
img2 = cv2.imread(ref,0)

# Crop the images
im1 = img1[y:y+h, x:x+w]
im2 = img2[y:y+h, x:x+w]

# Perform diff algorithm:
def get_image_difference(img1, img2):
    hist1 = cv2.calcHist([img1], [0],None,[256],[0, 256])
    hist2 = cv2.calcHist([img2], [0],None,[256],[0, 256])

    # Compare the histograms
    histDiff = cv2.compareHist(hist1,hist2,cv2.HISTCMP_BHATTACHARYYA)
    proba_match = cv2.matchTemplate(hist1,hist2,cv2.TM_CCOEFF_NORMED)[0][0]
    template_diff = 1 - proba_match

    com_image_diff = (histDiff/10) + template_diff
    return com_image_diff

# Calculate the diff between both photos
diff = get_image_difference(img1, img2)
diff = 100*diff
msg1 = ""
msg2 = ""
print("Error:", diff, "%")

# Evaluate diff
if (diff > errMax):
    msg1 = ('Automatic-Inspection Failed!')
    msg2 = ('Please, contact a debug technician.')
    fill_cell('fail')
else:
    msg1 = ('Automatic-Inspection Passed!')
    msg2 = ('Please, continue with the process.')
    fill_cell('pass')

# Resize and show the images
rs1 = cv2.resize(im1, (480, 360))
rs2 = cv2.resize(im2, (480, 360))
im3 = cv2.hconcat([rs1, rs2])
cv2.imshow(msg1, im3)
cv2.waitKey(0)
print(msg1)
print(msg2)
