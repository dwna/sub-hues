#!/usr/bin/python2.7
import colorsys
from PIL import Image, ImageDraw, ImageFont
import random
import numpy
from collections import Counter
import random
import praw
import config
import urllib, cStringIO
import traceback
from colorthief import ColorThief



#How many posts you want to scan for images (None idicates no limit, which in praw is 100)
numImages = None
#What what images will be resized to
imgSize = 25

#Subreddit to scan
sub = "all"

#Background color of the circle
background = (0,0,0)

#If using colorthief or not
cf = False
cfCount = 25 ** 2

#Mode for size of plotted points
#None - All points are same size
#True - Points are sized relative to the maximum count of a single color
#False - Points are sized no matter the largest color count
relativeSize = None

#Chaning colors' alpha based on the number of colors with the same hue angle
relativeAlpha = False


#############################################


#Logging in
r = praw.Reddit(username=config.r_username, password=config.r_password,client_id=config.r_client_id,client_secret=config.r_client_secret,user_agent=config.r_user_agent)


#Downloading Image
def GetImage(url):
    return Image.open(cStringIO.StringIO(urllib.urlopen(str(url)).read()))

#Correcting the amount of colorthief colors returned in the palette
def CfNumCorrection(num):
    actual = num
    if num ==1:  
        actual = 2
    if num == 2:
        actual = 2
    elif num == 3:
        actual = 2
    elif num >= 8 and num<=50:
        actual = num+1
    elif num>50:
        actual= 51
    return actual



#############################################



#Loading Subreddit
sr = r.subreddit(sub)


masterColors = Counter()
colorList = Counter()

count = 1


#Downloading Images from Subreddit
for submission in sr.top(limit=numImages):
    try:
        print (count, str(submission.title)[:30]+"...")
    except:
        print (count,"Unexpected Character")

    #Getting the image
    try:
        loadedImg = GetImage(submission.preview['images'][0]['resolutions'][-1]['url']).convert("RGB")

        colorList = {}
        #Using colorthief or not
        if not cf:

            loadedImg = loadedImg.resize((imgSize,imgSize))
            colors = loadedImg.getcolors(loadedImg.size[0] *loadedImg.size[1])
            del loadedImg

            #Adding the colors to the master list of all 
            for a in range(len(colors)):
                if len(colors[a][1]) == 4:
                    colors[a][1].pop()
            for a in colors:
            #masterColors[a[1]] = a[0]
                colorList[a[1]] = a[0]

        else:

            loadedImg.save("temp.png")
            cfCount=CfNumCorrection(cfCount)
            palette = ColorThief("temp.png").get_palette(color_count =cfCount,quality=1)



            for a in palette:
                colorList[a] = 1


    except Exception as exc:
        print (exc)
        #print ( traceback.print_exc())

    masterColors.update(colorList)
    count+=1


masterColors=Counter(masterColors)

#Reformating the data
colors = [(masterColors[x],x) for x in masterColors]

del masterColors



#############################################



#Initializing Image
img = Image.new("RGB",(5000,5000),(225,225,225,255))
draw = ImageDraw.Draw(img,"RGBA")

#Getting center coordinate of image
center = (int(img.size[0]/2),int(img.size[1]/2 ))

print ("Center Coordinates: ", center)

#############################################
#big circle's diameter and radius
main_d = ((img.size[0]+img.size[1])/2)*.750
main_r = main_d/2.

#Graphing radius
graph_r = main_r - (img.size[0]*1/32.)
print ("Main Radius: ",main_r)
print ("Graphing Radius: ", graph_r)

#Drawing big circle
draw.ellipse((center[0]-main_r,center[1]-main_r,center[0]+main_r,center[1]+main_r),fill = background)
#############################################
#Choosing between random and loaded image

#Custom Sorting-so lowest value plotted first
def sorter(data):
    index = [x/255. for x in data[1]]
    index=colorsys.rgb_to_hsv(*index)
    index = (index[2],data[0],index[1])
    return  index

colors.sort(key=sorter,reverse=False)
#colors.reverse()



print ("Total Unique Colors: ", len(colors))



#Finding number of colors in each hue angle
hueCounts = [0 for z  in range(361)]
for a in colors:
    h = [x/255. for x in a[1]]
    h = colorsys.rgb_to_hsv(*h)
    h = int(round(h[0] *360))
    hueCounts[h] +=1
maxHue = float(max(hueCounts))



#############################################


#function finding the coordinate for the color
def FindCoord(hsv_color):
    angle = hsv_color[0]

    #Finding theta for triangle
    def FixAngle(theta):
        startAng = theta
        while True:
            if theta >= 0 and theta <= 90:
                break
            else:
                theta-=90
        #Correcting Quadrents II and IV
        if startAng >90 and startAng <= 180:
            theta = 90 - theta
        elif startAng >270 and startAng <= 360:
            theta = 90 - theta

        return theta

    fixedAngle= FixAngle(angle)
    coord = center

    #Finding base and height of the triangle
    h = numpy.sin(numpy.deg2rad(fixedAngle)) * graph_r 
    b=numpy.cos(numpy.deg2rad(fixedAngle)) * graph_r
    #b=numpy.sin(numpy.deg2rad(90-fixedAngle)) * graph_r

    #Finding Point on Circumfrence
    if angle >= 0 and angle <= 90:
        #Quadrent I
        coord = (coord[0]+b,coord[1]+h)
    elif angle > 90 and angle <= 180:
        #Quadrent II
        coord = (coord[0]-b,coord[1]+h)
    elif angle > 180 and angle <= 270:
        #Quadrent III
        coord = (coord[0]-b,coord[1]-h)
    elif angle > 270 and angle <= 360:
        #Quadrent IV
        coord = (coord[0]+b,coord[1]-h)


    #How far the point is away from the center
    weight = hsv[1]/100.
    weightOpp = 1-weight

    #Moving the point towards center
    coord = ((weight*coord[0])+(weightOpp*center[0]), (weight*coord[1])+(weightOpp*center[1]))

    return coord

#############################################

#Transparency
alpha = int(.75*255)

#Sizing of the points
sizeBase = 1/128. * graph_r
sizeLim = 4 * sizeBase



#Finding the highest frequency of a color
maxCount = 0
for a in colors:
    if a[0] > maxCount:
        maxCount = a[0]
print ("Highest Frequency: ",maxCount)
#############################################

#Main function
for a in range(len(colors)):
    #if a / 100 == 0:
        #print (a+1,"/",len(colors))



    #Getting HSV value

    hsv = [x/255. for x in colors[a][1]]
    #hsv=colorsys.rgb_to_hsv(hsv[0],hsv[1],hsv[2])
    hsv = colorsys.rgb_to_hsv(*hsv)
    hsv = (hsv[0]*360,hsv[1]*100,hsv[2]*100)

    #Getting coordinates
    point_coords = FindCoord(hsv)



    #Choosing point sizing
    if relativeSize:
        #Relative sizing to other colors
        point_r =((colors[a][0]/float(maxCount)) *(sizeLim-sizeBase))+sizeBase

    elif relativeSize==False:
        #Absolute scale for colors
        point_r = (.25*(colors[a][0]-sizeBase))+sizeBase

        #Optional limiting of absolute sizing
        '''
        if point_r > .75*graph_r:
            point_r  =.75*graph_r
        '''

    elif relativeSize==None:
        point_r=sizeBase


    #relative transparency
    if relativeAlpha:
        alpha = (1 * (hueCounts[int(round(hsv[0]))] / maxHue)) 
        alpha = int(alpha*255)


    #Adding transparency 
    color = list(colors[a][1])
    color.append(alpha)
    color = tuple(color)

    #Graphing each color
    draw.ellipse((point_coords[0]-point_r,point_coords[1]-point_r,point_coords[0]+point_r,point_coords[1]+point_r),fill = color,outline=None)


#############################################


#Rotating so it is oriented correctly
img = img.rotate(90)


#Adding title
draw = ImageDraw.Draw(img)
try:
    font = ImageFont.truetype("helvetica bold.ttf", int(.04*img.size[1]))
except:
    font = ImageFont.load_default()
fontBox = font.getsize("The most common hues of r/{}".format(sub))

draw.text(((img.size[0]/2)-(fontBox[0]/2.), (img.size[1]*.0625)-(fontBox[1]/2.)),"The most common hues of r/{}".format(sub),(0,0,0),font=font)


#Saving Image
if not cf:
    img.save("{}_{}n_{}x{}.png".format(str(sr), numImages,imgSize,imgSize))
elif cf:
    img.save("{}_{}n_cf{}.png".format(str(sr), numImages,cfCount))

print ("Finished")
