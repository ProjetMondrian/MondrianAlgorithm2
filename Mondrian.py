import itertools
import cv2 as cv
import math
import operator
import sys
import time
import numpy
from PIL import  Image, ImageDraw, ImageFilter

## If face_recognition is installed it will be used but because the installation is not trivial the program will still run without it.
try:
    import face_recognition
    useFR = True
except ImportError: useFR = False


## Filename can be given as a command line argument or defined here.
## If neither of the two is done, the program will ask the user to input a correct filename during the execution.
try: [filename] = sys.argv[1:]
except ValueError: pass
#filename = "..."

## Some options/parameters
showOutput = True
saveOutput = True
printTimeInfo = False
useOnlyMondrianColors = False
compareUsingEuclidianDistance = True
autoAdjustTolerance = True
autoAdjustNbrOfColors = False
useContourRecognition = False

if not autoAdjustNbrOfColors:
    desiredNbrOfColors = 5
else:
    desiredNbrOfColors = 10

while True:
    try:
        im = Image.open(filename)
        break
    except (NameError,FileNotFoundError,AttributeError):
        filename = input('Missing or incorrect file name, try again: ')


## All RGB values in the output will be  multiples of this factor, the bigger it is the fewer different colors there will be.
## A much more complex normalization function is defined further below.
## This just explains how the normalization factor is used (if used at all).
normalizationFactor = 10
normalizationFunction = lambda x: int(x/normalizationFactor)*normalizationFactor


## The following function decides (with a certain tolerance) if two colors are to be considered the same for the merging process.
## The most logical way to compare triplets is to calculate the euclidian distance between the two.
## A second method is also available which works similarly to the normalization function and can produce interesting alternative results but in general the euclidian distance method should be preferred.
if not autoAdjustTolerance:
    comparisonTolerance = 10
else:
    comparisonTolerance = normalizationFactor

def comparisonFunction(tuple1,tuple2):
    if compareUsingEuclidianDistance:
        return euclidianDistance(tuple1,tuple2) <= comparisonTolerance

    else:
        return tuple(map(lambda x: int(x/comparisonTolerance),tuple1)) == tuple(map(lambda x: int(x/comparisonTolerance),tuple2))

if im.format == 'PNG':
    im = im.convert('RGB')
    im.save(filename[0:filename.index(".")]+".jpg")
    filename = filename[0:filename.index(".")]+".jpg"

## The input image will be resized to the given size, which will also be the size of the output.
desiredSize = (512, 512)
if (im.size != desiredSize):
    im = im.resize(desiredSize)
    #filename = "resized_"+filename
    #im.save(filename)


## Contains the RGB values of each pixel in the resized input image.
px = im.load()
imageArray = numpy.asarray(im)
lineWidth = 5

## Some functions used later, some may be unused like a lot of the commented lines further on, they were just alternative strategies to be tested

def euclidianDistance(tuple1,tuple2):
    if type(tuple1) is int: return math.sqrt(tuple1**2+tuple2**2)
    else: return math.sqrt((tuple2[0]-tuple1[0])**2 + (tuple2[1]-tuple1[1])**2 + (tuple2[2]-tuple1[2])**2)
                     
def drawGrid(draw,points,coeff2):
    for i in range(1,coeff2):
        draw.line((points*i, 0, points*i, im.size[1]), fill=(0,0,0), width=lineWidth)
        draw.line((0,points*i, im.size[1], points*i), fill=(0,0,0), width=lineWidth)
    return

def undrawGrid(draw,points,coeff2,newColorArray):
    """Erase black lines between squares of the same color."""
    ## This is the merge function.
    ## If two neighboring regions are considered to be the same color by the comparison function then this function replaces the black line between them by a line of their color (making it invisible).
    for j in range(0,coeff2-1):
        if comparisonFunction(newColorArray[0][j],newColorArray[0][j+1]):
            draw.line((points*0, points*(j+1), points*(0+1)-3, points*(j+1)), fill=newColorArray[0][j], width=lineWidth)

    for i in range(0,coeff2-1):
        if comparisonFunction(newColorArray[i][0],newColorArray[i+1][0]):
            draw.line((points*(i+1), points*0, points*(i+1), points*1-3), fill=newColorArray[i][0], width=lineWidth)

    for i in range(1,coeff2):
        for j in range(1,coeff2):
            if comparisonFunction(newColorArray[i][j],newColorArray[i][j-1]):
                draw.line((points*i+3, points*j, points*(i+1)-3, points*j), fill=newColorArray[i][j], width=lineWidth)

            if comparisonFunction(newColorArray[i][j],newColorArray[i-1][j]):
                draw.line((points*i, points*j+3, points*i, points*(j+1)-3), fill=newColorArray[i][j], width=lineWidth)


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

def removeDots(image,points,coeff2,newColorArray):
    """Paint over dots left behind by the merge function."""
    for i in range(1,coeff2):
        if (px[3,points*i] != (0,0,0)):
            im.putpixel((0,points*i-1),newColorArray[0][i-1])
            im.putpixel((1,points*i-1),newColorArray[0][i-1])
            im.putpixel((0,points*i),newColorArray[0][i])
            im.putpixel((1,points*i),newColorArray[0][i])
            im.putpixel((0,points*i+1),newColorArray[0][i])
            im.putpixel((1,points*i+1),newColorArray[0][i])
            if lineWidth==5:
                im.putpixel((0,points*i-2),newColorArray[0][i-1])
                im.putpixel((1,points*i-2),newColorArray[0][i-1])
                im.putpixel((0,points*i+2),newColorArray[0][i])
                im.putpixel((1,points*i+2),newColorArray[0][i])

    for i in range(1,coeff2):
        for j in range(1,coeff2):
            if (px[points*i-3,points*j] != (0,0,0) and px[points*i+3,points*j] != (0,0,0) and px[points*i,points*j-3] != (0,0,0) and px[points*i,points*j+3] != (0,0,0)):
                draw.line((points*i-5,points*j,points*i+5,points*j),fill=newColorArray[i][j],width=lineWidth)
    for i in range(1,coeff2):
        if px[points*i,500]!=(0,0,0):
            draw.line((points*i,500,points*i,511),fill=newColorArray[i][15],width=lineWidth)
        if px[500,points*i]!=(0,0,0):
            draw.line((500,points*i,511,points*i),fill=newColorArray[15][i],width=lineWidth)


def eyeRecognition(x,y,L):
    ## Also not being used, faceRecognition more reliable.
    global coeff1
    for i in range(0,coeff1):
        j=0
        foundWhite1 = 0
        foundBlack = 0
        foundWhite2 = 0
        while foundWhite1<2 and j<coeff1:
            if not (False in tuple(map(lambda x: x>=180,L[coeff1*j+i]))):
                foundWhite1 +=1
            j+=1
        while foundWhite1>=2 and foundBlack<2 and j<coeff1:
            if not (False in tuple(map(lambda x: x<=40,L[coeff1*j+i]))):
                foundBlack +=1
            j+=1
        while foundWhite1>=2 and foundBlack>=2 and foundWhite2<1 and j<coeff1:
            if not (False in tuple(map(lambda x: x>=180,L[coeff1*j+i]))):
                foundWhite2 +=1
            j+=1
        if foundWhite1==2 and foundBlack==2 and foundWhite2==1:
            return (x,y)
    return None

def faceRecognition(image):
    """Find the positions of eyes and lips in the input image."""
    faceLandmarks = [[],[],[]]
    face_landmarks_list = face_recognition.face_landmarks(image)
    if len(face_landmarks_list)>0:
        if len(face_landmarks_list[0]['left_eye'])>0:
            leftEyePos = [tuple(map(lambda i: int(i/32),i)) for i in face_landmarks_list[0]['left_eye']]
            for i in set(leftEyePos):
                if leftEyePos.count(i)>=len(leftEyePos)//len(set(leftEyePos)):
                    faceLandmarks[0] += [i,]
        if len(face_landmarks_list[0]['right_eye'])>0:
            rightEyePos = [tuple(map(lambda i: int(i/32),i)) for i in face_landmarks_list[0]['right_eye']]
            for i in set(rightEyePos):
                if rightEyePos.count(i)>=len(rightEyePos)//len(set(rightEyePos)):
                    faceLandmarks[1] += [i,]
        if len(face_landmarks_list[0]['top_lip'])>0:
            mouthPos = [tuple(map(lambda i: int(i/32),i)) for i in (face_landmarks_list[0]['top_lip']+face_landmarks_list[0]['bottom_lip'])]
            for i in set(mouthPos):
                if mouthPos.count(i)>=len(mouthPos)//len(set(mouthPos)):
                    faceLandmarks[2] += [i,]
    return faceLandmarks

def findMostContrast(L,comparisonList):
    """Find the element of a list which is most distant on average from every element of a comparison list if given, otherwise compares to each element of the first list"""
    distances = [0]*len(L)
    
    if len(comparisonList)!=0:
        for i in set(L):
            tmp = 0
            for j in set(comparisonList):
                tmp += euclidianDistance(i,j)
            distances[L.index(i)] = tmp/len(comparisonList)
            maxIndex = distances.index(max(distances))
        return L[maxIndex]
    
    else:
        for i in set(L):
            tmp=0
            for j in set(L):
                tmp += euclidianDistance(i,j)
            distances[L.index(i)]=tmp/len(L)
        maxIndex = distances.index(max(distances))
        return L[maxIndex]

def findMostCommon(L,howMany):
    currentCount = 0
    L2=list(set(L))
    L2.sort()
    Lcount = [0]*len(L2)
    x=0
    for i in L2:
        Lcount[x] = L.count(i)
        x+=1
    tmpList = [(j,i) for i,j in enumerate(Lcount)]
    tmpList.sort()
    tmpList = tmpList[howMany:]
    mostCommonColors = [L2[i] for j,i in tmpList]
    return mostCommonColors[howMany:]
    ## Alternatively if being concise is an issue, could also just do: return max(set(L), key = L.count)
    ## But performances are fairly identical for the two and the longer version gives more control in terms of handling cases where the given list has two modes and not a unique one.

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
        return tuple(map(lambda x:int(x/normalizationFactor+0.5)*normalizationFactor,color))
        #return tuple(map(lambda x:round(x/normalizationFactor)*normalizationFactor,color))

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
                    if getColorCount(i,newColorArray) > getColorCount(j,newColorArray):
                        uniqueNewColorList.remove(j)
                    else:
                        uniqueNewColorList.remove(i)
    return uniqueNewColorList

def recolorRegions(x,y,newColorArray,finalColorList):
    """Apply the same color to all squares in a merged region."""
    ## If the comparison tolerance is larger than the normalization factor then two regions can be merged even though they do not appear exactly similar.
    ## The purpose of this function is that if that happens then the color that appears the most often is assigned to each square in the merged region so that each merged region will be one single color.

    ## If the color of the current square unit is not in the reduced unique color list then the function returns whichever color of that list it is closest to.
    if not newColorArray[x][y] in finalColorList:
        distance = [0] * len(finalColorList)
        for i in range(0,len(finalColorList)):
            distance[i] = euclidianDistance(newColorArray[x][y],finalColorList[i])
        minIndex = distance.index(min(distance))
        return finalColorList[minIndex]
    else:
        return newColorArray[x][y]

def adjustTolerance(desiredNbrOfColors,newColorList):
    """Increment the comparison tolerance until the final color list contains as many colors as desired."""
    global comparisonTolerance
    L = getFinalColorList(newColorList)
    while len(L) > desiredNbrOfColors:
        comparisonTolerance += 10
        L = getFinalColorList(newColorList)
    while len(L) < desiredNbrOfColors:
        comparisonTolerance -= 1
        L = getFinalColorList(newColorList)

def adjustNbrOfColors(L):
    global desiredNbrOfColors
    wasModified = False
    for i in L:
        for j in L:
            if euclidianDistance(i,j)<= 2*comparisonTolerance:
                desiredNbrOfColors-=1
                wasModified = True
    print(wasModified)
    return wasModified

def drawContour(im,draw):
    """Identify contours and draw corresponding lines."""
    img = im.filter(ImageFilter.BLUR)
    img = im.filter(ImageFilter.SMOOTH)
    img = cv.cvtColor(numpy.array(img), cv.COLOR_RGB2BGR)
    edges = cv.Canny(img,100,200)
    pos = numpy.nonzero(edges)
    pos2 = [(pos[0][i],pos[1][i]) for i in range(0,len(pos[0]))]
    pos3=[tuple(map(lambda x:int(round(x/32)),i)) for i in pos2]
    pos3 = [(i[1],i[0]) for i in pos3]
    for i in pos3:
        if pos3.count((i[0]+1,i[1]))>20 and i[0]<16 and i[1]<16:
            draw.line([(32*i[0],32*i[1]),(32*(i[0]+1),32*i[1])],fill=(0,0,0),width=5)
        if pos3.count((i[0],i[1]+1))>20 and i[0]<16 and i[1]<16:
            draw.line([(32*i[0],32*i[1]),(32*(i[0]),32*(i[1]+1))],fill=(0,0,0),width=5)

def recolorPixels(x,y,px, newColorArray):
    """Apply the right color to each pixel in a square unit."""
    for i in range(0+coeff1*x,coeff1+coeff1*x):
        for j in range(0+coeff1*y,coeff1+coeff1*y):
            px[i,j]=newColorArray[x][y]

def mondrianize(px, draw):
    """Draw up to 5 lines that go across the whole image vertically and horizontally at the most relevant positions to make it look more Mondrian-esque."""
    horizontalLineArray = numpy.ones((16,16))
    verticalLineArray = numpy.ones((16,16))
    for i in range(0,16):
        for j in range(0,16):
            if px[32*i,32*j+10]!=(0,0,0):
                verticalLineArray[i][j]=0
            if px[32*i+10,32*j]!=(0,0,0):
                horizontalLineArray[i][j]=0

    transposeH = numpy.transpose(horizontalLineArray)
    countH = numpy.count_nonzero(transposeH,1)
    countV = numpy.count_nonzero(verticalLineArray,1)
    sortedIndexesH = (numpy.argsort(countH)).tolist()
    sortedIndexesV = (numpy.argsort(countV)).tolist()
    for i in sortedIndexesH:
        for j in sortedIndexesH:
            indexDistanceI = 0
            indexDistanceJ = 0
            if i!=j and countH[i]==countH[j]:
                for k in sortedIndexesH:
                    indexDistanceI+=abs(i-k)
                    indexDistanceJ+=abs(j-k)
                if indexDistanceI>indexDistanceJ:
                    a,b=sortedIndexesH.index(i),sortedIndexesH.index(j)
                    if a<b:sortedIndexesH[b], sortedIndexesH[a] = sortedIndexesH[a], sortedIndexesH[b]
                else:
                    a,b=sortedIndexesH.index(i),sortedIndexesH.index(j)
                    if a>b:sortedIndexesH[b], sortedIndexesH[a] = sortedIndexesH[a], sortedIndexesH[b]

    for i in sortedIndexesV:
        for j in sortedIndexesV:
            indexDistanceI = 0
            indexDistanceJ = 0
            if i!=j and countV[i]==countV[j]:
                for k in sortedIndexesV:
                    indexDistanceI+=abs(i-k)
                    indexDistanceJ+=abs(j-k)
                if indexDistanceI>indexDistanceJ:
                    a,b=sortedIndexesV.index(i),sortedIndexesV.index(j)
                    if a<b:sortedIndexesV[b], sortedIndexesV[a] = sortedIndexesV[a], sortedIndexesV[b]
                else:
                    a,b=sortedIndexesV.index(i),sortedIndexesV.index(j)
                    if a>b:sortedIndexesV[b], sortedIndexesV[a] = sortedIndexesV[a], sortedIndexesV[b]

    sortedIndexesH = sortedIndexesH[-5:]
    sortedIndexesV = sortedIndexesV[-5:]
    whereToDrawH = [i for i in sortedIndexesH[-2:]]+[i for i in sortedIndexesH[:-2] if countH[i]>=5]
    whereToDrawV = [i for i in sortedIndexesV[-2:]]+[i for i in sortedIndexesV[:-2] if countV[i]>=4]
    for i in whereToDrawH:
        draw.line((0,points*i,512,points*i), fill=(0,0,0), width=lineWidth)
    for i in whereToDrawV:
        draw.line((points*i,0, points*i,512), fill=(0,0,0), width=lineWidth)




## For now the program only uses 512 by 512 pixels images for efficiency.
## The image is divided in 16x16 squares of 32x32 pixels each
coeff1 = 32
coeff2 = 16

progress = 0

## Initiates a list of lists which acts as an array to hold the RGB values of each region in the split image.
newColorArray = [0] * coeff2
for i in range(coeff2):
    newColorArray[i] = [0] * coeff2
newColorList=[]
foundEyes=[]
lipColor=[]
if useFR:landmarksPos = faceRecognition(imageArray)
else:landmarksPos=[]
startTime = time.clock()

## Calculate the value to apply to each region of the output.
for x in range(0,coeff2):
    for y in range(0,coeff2):
        if(x==0 and y==0 and printTimeInfo):
            time1 = time.clock()
        compteur3= []
        for i in range(0+coeff1*x,coeff1+coeff1*x):
            for j in range(0+coeff1*y,coeff1+coeff1*y):
                px[i,j] = normalizeColors(px[i,j])
                compteur3 += [px[i,j],]
        if useFR:
            if (x,y) in landmarksPos[2]:
                lipColor += findMostCommon(compteur3,-7)
        newColor3 = findMostCommon(compteur3,-1)
        newColorArray[x][y] = newColor3[0]
        newColorList += [newColor3[0],]

        ## The program can take some time to run for some images so these few lines just print the progress to give an idea of how long it will take to run.
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

mergingStartTime = time.clock()

## Some parameters can adjust themselves automatically.
## But for the number of colors it's best to choose a value at the start and not change it.
wasModified = True
ctr = 1
while wasModified and autoAdjustNbrOfColors:
    if autoAdjustTolerance: adjustTolerance(desiredNbrOfColors,newColorList)
    finalColorList = getFinalColorList(newColorList)
    wasModified = adjustNbrOfColors(finalColorList)
if autoAdjustTolerance: adjustTolerance(desiredNbrOfColors,newColorList)


finalColorList = getFinalColorList(newColorList)
if useFR and len(landmarksPos[2])>0:lipColor=findMostContrast(lipColor,[newColorArray[i][j] for i,j in landmarksPos[2]])

## Apply the new calculated value to each pixel in the image.
progress = 0
for x in range(0,coeff2):
    for y in range(0,coeff2):
        if(x==0 and y==0 and printTimeInfo):
            time1 = time.clock()
        if not(useOnlyMondrianColors):
            newColorArray[x][y] = recolorRegions(x,y,newColorArray,finalColorList)
        if useFR and len(landmarksPos[0])>0:
            for i in landmarksPos[0]:
                newColorArray[i[0]][i[1]] = (254,254,254)
            for i in landmarksPos[1]:
                newColorArray[i[0]][i[1]] = (254,254,254)
            for i in landmarksPos[2]:
                newColorArray[i[0]][i[1]] = lipColor
        recolorPixels(x,y,px,newColorArray)

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

## These functions give the finishing touch to the image.
drawGrid(draw,points,coeff2)
undrawGrid(draw,points,coeff2,newColorArray)
removeDots(im,points,coeff2,newColorArray)
if useContourRecognition: drawContour(im,draw)
mondrianize(px,draw)

#im = im.resize((1000,1000), Image.NEAREST)

if printTimeInfo:
    mergingEndTime = time.clock()
    print(' Merging: completed in',mergingEndTime-mergingStartTime,'seconds.',' '*15)
    print(' Total time:',mergingEndTime-startTime,'seconds.')

if showOutput:
    im.show()

if saveOutput:
    if filename.startswith('resized_'):filename=filename[8:]
    im.save(filename[:filename.index(".")]+"_output.png")

