
Video of working code for 4_points.py
https://user-images.githubusercontent.com/50956270/110584876-e321d200-81aa-11eb-82fe-6d694dd5f76b.mp4

# OpticalProject
Computer vision project meant for the identifying, tracking and calculating the coordinates of the ends of the optical fiber cables to be connected with one another. 

## How to run the program 
- The latest python program is the 4_points.py program
- This program utilises the default API provided by the IDS camera -> UI-3480ML-M-GL
- Just open this in pycharm environment and ensure that the two items are within the sights of the camera, if not the program may crash 
- If you want the logic for calculating the midpoint based on the cv2.goodFeaturesToTrack() function, please refer to lines 206 to 265 of the 4_points.py document

## Reading Materials 
- For more on cv2.goodFeaturesToTrack(), please kindly refer to this link https://docs.opencv.org/master/d4/d8c/tutorial_py_shi_tomasi.html 
