import itertools
import math
import operator
import time
from PIL import  Image, ImageDraw

## Choose one from the list of available filenames:
#filename = "building.jpg"
#filename = "bwlena.jpg"
#filename = "duck.jpg"
#filename = "k.jpg"
#filename = "obama.jpg"
#filename = "lena.jpg"
#filename = "white_background_input.jpg"
filename = "women.jpg"

showOutput = True
saveOutput = False
printTimeInfo = True
useOnlyMondrianColors = False
compareUsingEuclidianDistance = True

im = Image.open(filename)


## All RGB values in the output will be  multiples of this factor, the bigger it is the fewer different colors there will be.
## A much more complex normalization function is defined further below.
## This just explains how the normalization factor is used (if used at all).
normalizationFactor = 10
normalizationFunction = lambda x: int(x/normalizationFactor)*normalizationFactor


## The following function decides (with a certain tolerance) if two colors are to be considered the same for the merging process.
## The most logical way to compare triplets is to calculate the euclidian distance between the two.
## A second method is also available which works similarly to the normalization function and can produce interesting alternative results but in general the euclidian distance method should be preferred.
comparisonTolerance = 100
def comparisonFunction(tuple1,tuple2):
    if compareUsingEuclidianDistance:
        return euclidianDistance(tuple1,tuple2) <= comparisonTolerance

    else:
        return tuple(map(lambda x: int(x/comparisonTolerance),tuple1)) == tuple(map(lambda x: int(x/comparisonTolerance),tuple2))


## The input image will be resized to the given size, which will also be the size of the output.
desiredSize = (512, 512)
if (im.size != desiredSize):
    im = im.resize(desiredSize)

## Contains the RGB values of each pixel in the resized input image.
px = im.load()


## Some functions used later, some may be unused like a lot of the commented lines further on, they were just alternative strategies to be tested

def euclidianDistance(tuple1,tuple2):
    return math.sqrt((tuple2[0]-tuple1[0])**2 + (tuple2[1]-tuple1[1])**2 + (tuple2[2]-tuple1[2])**2)
                     
def drawGrid(draw,points,coeff2):
    for i in range(1,coeff2+1):
        draw.line((points*i, 0, points*i, im.size[1]), fill=0, width=3)
        draw.line((0,points*i, im.size[1], points*i), fill=0, width=3)
    return

def undrawGrid(draw,points,coeff2,newColorMatrix):
    """Erase black lines between squares of the same color."""
    ## This is the merge function.
    ## If two neighboring regions are considered to be the same color by the comparison function then this function replaces the black line between them by a line of their color (making it invisible).
    for j in range(0,coeff2-1):
        if comparisonFunction(newColorMatrix[0][j],newColorMatrix[0][j+1]):
            draw.line((points*0+2, points*(j+1), points*(0+1)-2, points*(j+1)), fill=newColorMatrix[0][j], width=3)

    for i in range(0,coeff2-1):
        if comparisonFunction(newColorMatrix[i][0],newColorMatrix[i+1][0]):
            draw.line((points*(i+1), points*0, points*(i+1), points*1-2), fill=newColorMatrix[i][0], width=3)

    for i in range(1,coeff2):
        for j in range(1,coeff2):
            if comparisonFunction(newColorMatrix[i][j],newColorMatrix[i][j-1]):
                draw.line((points*i+2, points*j, points*(i+1)-2, points*j), fill=newColorMatrix[i][j], width=3)
                    
            if comparisonFunction(newColorMatrix[i][j],newColorMatrix[i-1][j]):
                draw.line((points*i, points*j+2, points*i, points*(j+1)-2), fill=newColorMatrix[i][j], width=3)

def drawRectangles(draw,points,coeff2):
    ## Not currently being used.
    while(xy2[1][1]<=im.size[1]):
        while(xy2[1][1]<=im.size[1]):
            draw.rectangle(xy, fill=None, outline=(0,0,0))
            xy2[0] = tuple(map(sum,zip(xy2[0],increment1)))
            xy2[1] = tuple(map(sum,zip(xy2[1],increment1)))
        xy2 = xy
        xy2[0] = tuple(map(sum,zip(xy2[0],increment2)))
        xy2[1] = tuple(map(sum,zip(xy2[1],increment2)))

def removeDots(image,points,coeff2,newColorMatrix):
    """Paint over dots left behind by the merge function."""
    for i in range(1,coeff2):
        if (px[3,points*i] != (0,0,0)):
            im.putpixel((0,points*i-1),newColorMatrix[0][i-1])
            im.putpixel((1,points*i-1),newColorMatrix[0][i-1])
            im.putpixel((0,points*i),newColorMatrix[0][i])
            im.putpixel((1,points*i),newColorMatrix[0][i])
            im.putpixel((0,points*i+1),newColorMatrix[0][i])
            im.putpixel((1,points*i+1),newColorMatrix[0][i])

    for i in range(1,coeff2):
        for j in range(1,coeff2):
            if (px[points*i-2,points*j] != (0,0,0) and px[points*i+2,points*j] != (0,0,0) and px[points*i,points*j-2] != (0,0,0) and px[points*i,points*j+2] != (0,0,0)):
                im.putpixel((points*i-1,points*j-1),newColorMatrix[i][j])
                im.putpixel((points*i,points*j-1),newColorMatrix[i][j])
                im.putpixel((points*i+1,points*j-1),newColorMatrix[i][j])
                im.putpixel((points*i-1,points*j),newColorMatrix[i][j])
                im.putpixel((points*i,points*j),newColorMatrix[i][j])
                im.putpixel((points*i+1,points*j),newColorMatrix[i][j])
                im.putpixel((points*i-1,points*j+1),newColorMatrix[i][j])
                im.putpixel((points*i,points*j+1),newColorMatrix[i][j])
                im.putpixel((points*i+1,points*j+1),newColorMatrix[i][j])

def findMostCommon(L):

    #return max(set(L), key = L.count)

    #"""
    currentCount = 0
    L2=list(set(L))
    L2.sort()
    for i in L2:
        if (currentCount < L.count(i)):
            currentCount = L.count(i)
            mostCommonColor = i
    return mostCommonColor
    #"""

def getColorCount(color,colorlist):
    count = 0
    for i in range(0,coeff2):
        count += colorlist[i].count(color)
    return count


def normalizeColors(color):
    R=color[0]
    G=color[1]
    B=color[2]
    Red=(230,60,60)
    Blue=(25,60,170)
    Yellow=(250,240,60)
    White=(255,255,255)
    Black=(0,0,0)
    distance=[0,0,0,0,0]
    mondrianColors=[Red,Blue,Yellow,White,Black]
    if not(useOnlyMondrianColors):
        ## This is the normalization method explained at the start.
        return tuple(map(lambda x:int(x/normalizationFactor)*normalizationFactor,color))

    elif useOnlyMondrianColors:
        ## This alternative method replaces the input color by whichever of the 5 Mondrian colors it is closest to.
        for i in range(0,5):
            distance[i] = euclidianDistance(color,mondrianColors[i])
        minIndex = distance.index(min(distance))
        return mondrianColors[minIndex]


    else :
        ## Another way of calculating which Mondrian color to replace the input color by, not using the euclidian distance between the two. This method is currently not being used.
        if (R>(1.4*G) and R>(1.4*B) and R>150):
            return Red

        elif (B>(1*G) and B>(1.5*R) and B>100):
            return Blue

        elif (R>(2*B) and G>(2*B) and R>100 and G>100):
            return Yellow

        elif R>=100 and G >=100 and B>=100:
            return White

        else:
            return Black

def getFinalColorList(newColorList):
    """Return a list not containing colors that appear rarely and are barely different from more frequent similar colors."""
    ## Remove duplicates from the list of colors, create a second list whose size never changes to iterate over.
    uniqueNewColorList=list(set(newColorList))
    uniqueNewColorList2=list(set(newColorList))
    uniqueNewColorList.sort()
    uniqueNewColorList2.sort()

    ## If two colors are considered similar enough by the comparison function then the one that appears the least frequently is removed from the list of colors.
    for i in uniqueNewColorList2:
        for j in uniqueNewColorList2:
            if i in uniqueNewColorList and j in uniqueNewColorList:
                if i!=j and comparisonFunction(i,j):
                    if getColorCount(i,newColorMatrix) > getColorCount(j,newColorMatrix):
                        uniqueNewColorList.remove(j)
                    else:
                        uniqueNewColorList.remove(i)
    return uniqueNewColorList

def recolorRegions(x,y,newColorMatrix,finalColorList):
    """Apply the same color to all squares in a merged region."""
    ## If the comparison tolerance is larger than the normalization factor then two regions can be merged even though they do not appear exactly similar.
    ## The purpose of this function is that if that happens then the color that appears the most often is assigned to each square in the merged region so that each merged region will be one single color.




    ## If the color of the current square unit is not in the reduced unique color list then the function returns whichever color of that list it is closest to.
    if not newColorMatrix[x][y] in finalColorList:
        distance = [0] * len(finalColorList)
        for i in range(0,len(finalColorList)):
            distance[i] = euclidianDistance(newColorMatrix[x][y],finalColorList[i])
        minIndex = distance.index(min(distance))
        return finalColorList[minIndex]
    else:
        return newColorMatrix[x][y]

def recolorPixels(x,y,px, newColorMatrix):
    """Apply the right color to each pixel in a square unit."""
    for i in range(0+coeff1*x,coeff1+coeff1*x):
        for j in range(0+coeff1*y,coeff1+coeff1*y):
            px[i,j]=newColorMatrix[x][y]


## For now the program only uses 512 by 512 pixels images for simplicity
## The image is divided in 16x16 squares of 32x32 pixels each
coeff1 = 32
coeff2 = 16

progress = 0

## Initiates a matrix to hold the RGB values of each region in the split image.
newColorMatrix = [0] * coeff2
for i in range(coeff2):
    newColorMatrix[i] = [0] * coeff2
newColorList=[]

startTime = time.clock()
for x in range(0,coeff2):
    for y in range(0,coeff2):
        if(x==0 and y==0 and printTimeInfo):
            time1 = time.clock()
        compteur = (0,0,0)
        compteur2= [(0,0,0)]
        compteur3= ((0,0,0),)
        for i in range(0+coeff1*x,coeff1+coeff1*x):
            for j in range(0+coeff1*y,coeff1+coeff1*y):
                #compteur = tuple(map(sum,zip(compteur,px[i,j])))
                #compteur2= compteur2+list(px[i,j],)
                compteur3 += (px[i,j],)

        #newColor =(int(compteur[0]/(2500)),int(compteur[1]/(2500)),int(compteur[2]/(2500)))
        #newColor2=findMostCommon(compteur2)
        newColor3 = findMostCommon(compteur3)
        newColor3 = normalizeColors(newColor3)
        newColorMatrix[x][y] = newColor3
        newColorList += [newColor3,]

## The program can take some time to run for larger images so these few lines just print the progress to give an idea of how long it will take to run.
        if printTimeInfo:
            if(x==0 and y==0):
                time2 = time.clock()
                timeRemaining = (time2-time1)*255+1.5
            else:
                timeRemaining -= time.clock()-time2
                time2=time.clock()
            print(' '*18,'Estimated time remaining:', int(timeRemaining), 'seconds',' '*5, end='\r')
            progress += 1/2.56
            print(' Splitting: '+str(int(progress))+'%'+' '*4, end='\r', flush=True)

if printTimeInfo:
    splittingEndTime = time.clock()
    print(' Splitting: completed in',splittingEndTime-startTime,'seconds.',' '*15)
    print(' Merging: ...', end='\r')

points = int(im.size[1]/coeff2)
draw = ImageDraw.Draw(im)

finalColorList = getFinalColorList(newColorList)

progress = 0
mergingStartTime = time.clock()
for x in range(0,coeff2):
    for y in range(0,coeff2):
        if(x==0 and y==0 and printTimeInfo):
            time1 = time.clock()
        if not(useOnlyMondrianColors):
            newColorMatrix[x][y] = recolorRegions(x,y,newColorMatrix,finalColorList)
        recolorPixels(x,y,px,newColorMatrix)

        if printTimeInfo:
            if(x==0 and y==0):
                time2 = time.clock()
                timeRemaining = (time2-time1)*255+1.5
            else:
                timeRemaining -= time.clock()-time2
                time2=time.clock()
            print(' '*18,'Estimated time remaining:', int(timeRemaining), 'seconds',' '*5, end='\r')
            progress += 1/2.56
            print(' Merging: '+str(int(progress))+'%'+' '*4, end='\r', flush=True)

drawGrid(draw,points,coeff2)
undrawGrid(draw,points,coeff2,newColorMatrix)
removeDots(im,points,coeff2,newColorMatrix)

if printTimeInfo:
    mergingEndTime = time.clock()
    print(' Merging: completed in',mergingEndTime-mergingStartTime,'seconds.',' '*15)
    print(' Total time:',mergingEndTime-startTime,'seconds.')

if showOutput:
    im.show()

if saveOutput:
    im.save(filename[0:filename.index(".")]+"_output.png")
