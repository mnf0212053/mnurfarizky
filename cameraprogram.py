# Author : Muhammad Nur Farizky
# Year : 2019
# Description :
# This program is used to analyze the speed of a moving object using webcam.
# The measured speed is given in pixel/s


import subprocess
import datetime
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np


#######################################

x=100
secondi = 0
secondf = 0
minuti = 0
minutf = 0
ti = 0
tf = 0
deltat = 0
deltatmat = []
t = []
vt = []
vt.append(0)

files = [r"c:\Users\ASUS\Documents\pytonproject\images1.jpg", r"c:\Users\ASUS\Documents\pytonproject\images2.jpg", r"c:\Users\ASUS\Documents\pytonproject\images3.jpg", r"c:\Users\ASUS\Documents\pytonproject\images4.jpg", r"c:\Users\ASUS\Documents\pytonproject\images5.jpg", r"c:\Users\ASUS\Documents\pytonproject\images6.jpg", r"c:\Users\ASUS\Documents\pytonproject\images7.jpg", r"c:\Users\ASUS\Documents\pytonproject\images8.jpg", r"c:\Users\ASUS\Documents\pytonproject\images9.jpg"]

#Taking images and calculating the time between frames.
print("Taking images...")
for n in range(0, len(files)):
    subprocess.call(["fswebcam", "--set",  "brightness=100%", "-p","YUYV", "-d", "/dev/video0", "-r", "640x480", "--no-banner", files[n]])
    
    datetime.datetime.now()
    secondi = secondf
    secondf = datetime.datetime.now().second
    minuti = minutf
    minutf = datetime.datetime.now().minute
    ti = tf
    tf = datetime.datetime.now().microsecond
    deltat = tf-ti+(secondf-secondi+(minutf-minuti)*60)*1000000
    deltatmat.append(2000000) 
    t.append(2000000*n)

print("Images taken. Processing...")
#Declaring variables
jcenteri = 0
icenteri = 0
jcenterf = 0
icenterf = 0

xavgmatavgf = 0
yavgmatavgf = 0

#Reading images
for n in range(0,len(files)):
    img = mpimg.imread(files[n])

    imgmat1 = []
    imgmat2 = []
    imgmat3 = []
    imgmat = []

    for i in range(0, len(img)): 
        for j in range(0, len(img[i])):
            for k in range(0, len(img[i][j])):
                imgmat1.append(pow(img[i][j][k]/255,0.33))
            imgmat2.append(imgmat1)
            imgmat1 = []
        imgmat3.append(imgmat2)
        imgmat2 = []
        
        
    #Scanning the location of the object inside the images
    avg = 185/255 
    border = 30
    num = 0
    colorvaluei = []
    colorvaluef = []
    isobject = 0
    xpos = []
    ypos = []
    xavgmat = []
    yavgmat = []
   
    for i in range(0, len(imgmat3)):
        for j in range(0, len(imgmat3[i])):
            if not isobject:
                colorvaluei = colorvaluef
            colorvaluef = imgmat3[i][j]
            if j>0:
                if (abs(colorvaluef[0] - 135/255)*255 > border) | (abs(colorvaluef[1] - 135/255)*255 > border) | (abs(colorvaluef[2] - 135/255)*255 > border):
                    xpos.append(j)
                    ypos.append(i)
                    isobject = 1
                else:
                    isobject = 0

        #The location of the object is calculated based on the average of the object pixel    
        xavg = 0
        for x in range(0,len(xpos)):
            xavg = xavg + xpos[x]
        xavg = xavg / len(xpos)
        xavgmat.append(xavg)
                            
        yavg = 0
        for y in range(0,len(ypos)):
            yavg = yavg + ypos[y]
        yavg = yavg / len(ypos)
        yavgmat.append(yavg)
        
    
    #Averaging it again to get the single (x, y) coordinate
    xavgmatavgi = xavgmatavgf
    yavgmatavgi = yavgmatavgf
    
    xavgmatavg = 0
    for xx in range(0, len(xavgmat)):
        xavgmatavg = xavgmatavg + xavgmat[xx]
    xavgmatavgf = xavgmatavg / len(xavgmat)
            
    yavgmatavg = 0
    for yy in range(0, len(yavgmat)):
        yavgmatavg = yavgmatavg + yavgmat[yy]
    yavgmatavgf = yavgmatavg / len(yavgmat)
    
    #Calculating the speed of the object
    if n > 0:
        ri = pow(pow(xavgmatavgi, 2) + pow(yavgmatavgi, 2), 0.5)
        rf = pow(pow(xavgmatavgf, 2) + pow(yavgmatavgf, 2), 0.5)
        print("rf = ", rf, "ri = ", ri)
        v = ((rf-ri)/deltatmat[n])*1000000
        vt.append(v)
        print(v)

#Showing the plot
fig, ax = plt.subplots()
ax.plot(t,vt)
ax.set(xlabel='time (s)', ylabel='velocity (px/s)',
    title='kelajuan terhadap waktu')
ax.grid()
plt.show()

