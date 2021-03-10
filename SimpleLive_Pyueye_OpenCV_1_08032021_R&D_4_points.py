#===========================================================================#
#                                                                           #
#  Copyright (C) 2006 - 2018                                                #
#  IDS Imaging Development Systems GmbH                                     #
#  Dimbacher Str. 6-8                                                       #
#  D-74182 Obersulm, Germany                                                 #
#                                                                           #
#  The information in this document is subject to change without notice     #
#  and should not be construed as a commitment by IDS Imaging Development   #
#  Systems GmbH. IDS Imaging Development Systems GmbH does not assume any   #
#  responsibility for any errors that may appear in this document.          #
#                                                                           #
#  This document, or source code, is provided solely as an example          #
#  of how to utilize IDS software libraries in a sample application.        #
#  IDS Imaging Development Systems GmbH does not assume any responsibility  #
#  for the use or reliability of any portion of this document or the        #
#  described software.                                                      #
#                                                                           #
#  General permission to copy or modify, but not for profit, is hereby      #
#  granted, provided that the above copyright notice is included and        #
#  reference made to the fact that reproduction privileges were granted     #
#  by IDS Imaging Development Systems GmbH.                                 #
#                                                                           #
#  IDS Imaging Development Systems GmbH cannot assume any responsibility    #
#  for the use or misuse of any portion of this software for other than     #
#  its intended diagnostic purpose in calibrating and testing IDS           #
#  manufactured cameras and software.                                       #
#                                                                           #
#===========================================================================#

# Developer Note: I tried to let it as simple as possible.
# Therefore there are no functions asking for the newest driver software or freeing memory beforehand, etc.
# The sole purpose of this program is to show one of the simplest ways to interact with an IDS camera via the uEye API.
# (XS cameras are not supported)
#---------------------------------------------------------------------------------------------------------------------------------------

#Libraries
# from pyimagesearch.centroidtracker import CentroidTracker
import pyueye
from pyueye import ueye
import numpy as np
import cv2
import sys
import datetime
from imutils import perspective
from imutils import contours
import imutils
import argparse
import math
from matplotlib import pyplot as plt



#---------------------------------------------------------------------------------------------------------------------------------------

#Variables
hCam = ueye.HIDS(0)             #0: first available camera;  1-254: The camera with the specified camera ID
sInfo = ueye.SENSORINFO()
cInfo = ueye.CAMINFO()
pcImageMemory = ueye.c_mem_p()
MemID = ueye.int()
rectAOI = ueye.IS_RECT()
pitch = ueye.INT()
nBitsPerPixel = ueye.INT(24)    #24: bits per pixel for color mode; take 8 bits per pixel for monochrome
channels = 3                    #3: channels for color mode(RGB); take 1 channel for monochrome
m_nColorMode = ueye.INT()		# Y8/RGB16/RGB24/REG32
bytes_per_pixel = int(nBitsPerPixel / 8)
#---------------------------------------------------------------------------------------------------------------------------------------
print("START")
print()

def midpoint(ptA, ptB):
    return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)


# Starts the driver and establishes the connection to the camera
nRet = ueye.is_InitCamera(hCam, None)
if nRet != ueye.IS_SUCCESS:
    print("is_InitCamera ERROR")

# Reads out the data hard-coded in the non-volatile camera memory and writes it to the data structure that cInfo points to
nRet = ueye.is_GetCameraInfo(hCam, cInfo)
if nRet != ueye.IS_SUCCESS:
    print("is_GetCameraInfo ERROR")

# You can query additional information about the sensor type used in the camera
nRet = ueye.is_GetSensorInfo(hCam, sInfo)
if nRet != ueye.IS_SUCCESS:
    print("is_GetSensorInfo ERROR")

nRet = ueye.is_ResetToDefault( hCam)
if nRet != ueye.IS_SUCCESS:
    print("is_ResetToDefault ERROR")

# Set display mode to DIB
nRet = ueye.is_SetDisplayMode(hCam, ueye.IS_SET_DM_DIB)

# Set the right color mode
if int.from_bytes(sInfo.nColorMode.value, byteorder='big') == ueye.IS_COLORMODE_BAYER:
    # setup the color depth to the current windows setting
    ueye.is_GetColorDepth(hCam, nBitsPerPixel, m_nColorMode)
    bytes_per_pixel = int(nBitsPerPixel / 8)
    print("IS_COLORMODE_BAYER: ", )
    print("\tm_nColorMode: \t\t", m_nColorMode)
    print("\tnBitsPerPixel: \t\t", nBitsPerPixel)
    print("\tbytes_per_pixel: \t\t", bytes_per_pixel)
    print()

elif int.from_bytes(sInfo.nColorMode.value, byteorder='big') == ueye.IS_COLORMODE_CBYCRY:
    # for color camera models use RGB32 mode
    m_nColorMode = ueye.IS_CM_BGRA8_PACKED
    nBitsPerPixel = ueye.INT(32)
    bytes_per_pixel = int(nBitsPerPixel / 8)
    print("IS_COLORMODE_CBYCRY: ", )
    print("\tm_nColorMode: \t\t", m_nColorMode)
    print("\tnBitsPerPixel: \t\t", nBitsPerPixel)
    print("\tbytes_per_pixel: \t\t", bytes_per_pixel)
    print()

elif int.from_bytes(sInfo.nColorMode.value, byteorder='big') == ueye.IS_COLORMODE_MONOCHROME:
    # for color camera models use RGB32 mode
    m_nColorMode = ueye.IS_CM_MONO8
    nBitsPerPixel = ueye.INT(8)
    bytes_per_pixel = int(nBitsPerPixel / 8)
    print("IS_COLORMODE_MONOCHROME: ", )
    print("\tm_nColorMode: \t\t", m_nColorMode)
    print("\tnBitsPerPixel: \t\t", nBitsPerPixel)
    print("\tbytes_per_pixel: \t\t", bytes_per_pixel)
    print()

else:
    # for monochrome camera models use Y8 mode
    m_nColorMode = ueye.IS_CM_MONO8
    nBitsPerPixel = ueye.INT(8)
    bytes_per_pixel = int(nBitsPerPixel / 8)
    print("else")

# Can be used to set the size and position of an "area of interest"(AOI) within an image
nRet = ueye.is_AOI(hCam, ueye.IS_AOI_IMAGE_GET_AOI, rectAOI, ueye.sizeof(rectAOI))
if nRet != ueye.IS_SUCCESS:
    print("is_AOI ERROR")

width = rectAOI.s32Width
height = rectAOI.s32Height

# Prints out some information about the camera and the sensor
print("Camera model:\t\t", sInfo.strSensorName.decode('utf-8'))
print("Camera serial no.:\t", cInfo.SerNo.decode('utf-8'))
print("Maximum image width:\t", width)
print("Maximum image height:\t", height)

#---------------------------------------------------------------------------------------------------------------------------------------

# Allocates an image memory for an image having its dimensions defined by width and height and its color depth defined by nBitsPerPixel
nRet = ueye.is_AllocImageMem(hCam, width, height, nBitsPerPixel, pcImageMemory, MemID)
if nRet != ueye.IS_SUCCESS:
    print("is_AllocImageMem ERROR")
else:
    # Makes the specified image memory the active memory
    nRet = ueye.is_SetImageMem(hCam, pcImageMemory, MemID)
    if nRet != ueye.IS_SUCCESS:
        print("is_SetImageMem ERROR")
    else:
        # Set the desired color mode
        nRet = ueye.is_SetColorMode(hCam, m_nColorMode)



# Activates the camera's live video mode (free run mode)
nRet = ueye.is_CaptureVideo(hCam, ueye.IS_DONT_WAIT)
if nRet != ueye.IS_SUCCESS:
    print("is_CaptureVideo ERROR")

# Enables the queue mode for existing image memory sequences
nRet = ueye.is_InquireImageMem(hCam, pcImageMemory, MemID, width, height, nBitsPerPixel, pitch)
if nRet != ueye.IS_SUCCESS:
    print("is_InquireImageMem ERROR")
else:
    print("Press s to save the image")
    print("Press q to leave the programm")


# DECLARE VARIABLES
pix = 2.75 # float(input('pix size (in um): '))
# ct = CentroidTracker()
# (H, W) = (None, None)

# Continuous image display
while(nRet == ueye.IS_SUCCESS):
    # In order to display the image in an OpenCV window we need to extract the data of our image memory
    array = ueye.get_data(pcImageMemory, width, height, nBitsPerPixel, pitch, copy=False)

    # bytes_per_pixel = int(nBitsPerPixel / 8)

    # ...reshape it in an numpy array...
    frame = np.reshape(array,(height.value, width.value, bytes_per_pixel))

    # ...resize the image by a half
    frame = cv2.resize(frame,(0,0),fx=0.3, fy=0.3)

    #print('size',frame.shape)
    
#---------------------------------------------------------------------------------------------------------------------------------------

    #Include image data processing here

    # Flip image
    # DECLARE VARIABLES WHICH WILL BE RESET EACH TIME IT LOOPS
    dic2 = {
        'XYTupleList': [],
        'XDifference': 0,
        'YDifference': 0,
    }

    image = cv2.flip(frame, -1)

    # Find contours
    cnts = cv2.findContours(image.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    for c in cnts:
        # Use goodFeaturesToTrack to identify the corners, aka points with high definition and with which the gradient
        # fades off abruptly
        pts = cv2.goodFeaturesToTrack(image, 9, 0.01, 12)
        # Convert it into keypoints so that they can be plotted later
        kps = [cv2.KeyPoint(x=f[0][0], y=f[0][1], _size=20) for f in pts]
        # if M["m00"] > 30:
        for i in range(len(pts)):
            for j in range(len(pts)):
                # Calculate the difference in the y-coordinates so that we can use it to filter the lines
                y_distance = abs(pts[i][0][1] - pts[j][0][1])
                x_distance = abs(pts[i][0][0] - pts[j][0][0])
                # The distance is calculated as 219 by using plt.imshow(image), plt.show()
                if 0 < x_distance < 8 and 200 < y_distance < 223:
                    (cX, cY) = midpoint((pts[i][0][0], pts[i][0][1]), (pts[j][0][0], pts[j][0][1]))

                    cv2.line(image, (int(pts[i][0][0]), int(pts[i][0][1])), (int(pts[j][0][0]), int(pts[j][0][1])), (255, 0, 0), 1)

                    cv2.circle(image, (int(cX), int(cY)), 4, (255, 255, 255), -1)
                    # cv2.rectangle(image, (int(cX -20 ), int(cY -20)), (int(cX + 20), int(cY + 20)), (0, 0, 0), -1)
                    cv2.putText(image, "mid", (int(cX-20), int(cY - 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                    # Append the X and Y coordinates
                    # Result of dic2['XYTupleList'] = [(288.0, 238.0), (322.0, 157.5)]
                    # Where dic2['XYTupleList'] = [(x, y), (x1, y1)]
                    # To access x, do dic2['XYTupleList'][0][0]
                    dic2['XYTupleList'].append((cX, cY))

                    if len(dic2['XYTupleList']) == 2:
                        xDifference = dic2['XYTupleList'][0][0] - dic2['XYTupleList'][1][0]
                        yDifference = dic2['XYTupleList'][0][1] - dic2['XYTupleList'][1][1]
                        dic2['XDifference'] = xDifference * pix
                        dic2['YDifference'] = yDifference * pix
                    # print(dic2)
                    cv2.rectangle(image, (0, 0), (225, 80), (255, 255, 255), -1)
                    cv2.putText(image, "X-Difference is " + str(abs(dic2['XDifference'])) + " um", (0, 60), cv2.QT_FONT_NORMAL,
                                0.5,
                                (0, 0, 0), thickness=1)
                    cv2.putText(image, "Y-Difference is " + str(abs(dic2['YDifference'])) + " um", (0, 30), cv2.QT_FONT_NORMAL,
                                0.5,
                                (0, 0, 0), thickness=1)

        img2 = cv2.drawKeypoints(image, kps, None, color=(0, 255, 0), flags=0)
        # pts = pts.sort()
        cv2.imshow("froggy", img2)
        # print("break")

    # Save screenshot into file. edit the file location to be saved into
    img_name = datetime.datetime.now().strftime("%Y-%m-%d%H-%M-%S-%f")
    # cv2.imwrite('output_image/' + str(img_name) + '.jpg', input_rgb)
    # Press q if you want to end the loop
    if cv2.waitKey(1) &0xFF==ord('s'):
        cv2.imwrite('C:/Users/Er Wen/Pictures/Optical' + str(img_name) + '.jpg', image) #儲存路徑
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
#---------------------------------------------------------------------------------------------------------------------------------------

# Releases an image memory that was allocated using is_AllocImageMem() and removes it from the driver management
ueye.is_FreeImageMem(hCam, pcImageMemory, MemID)

# Disables the hCam camera handle and releases the data structures and memory areas taken up by the uEye camera
ueye.is_ExitCamera(hCam)

# Destroys the OpenCv windows
cv2.destroyAllWindows()

print()
print("END")
