import itertools
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
#filename = "women.jpg"

showOutput = True
saveOutput = True
normalizeWithFunction = False

im = Image.open(filename)

## All RGB values in the output will be  multiples of this factor, the bigger it is the fewer different colors there will be.
normalizationFactor = 10
normalizationFunction = lambda x: int(x/normalizationFactor)*normalizationFactor

## When merging, RGB values are considered equal if they have the same quotient by integer division with this number, the bigger it is the bigger the merged regions will be. This value is irrelevent if smaller than the normalization factor.
comparisonFactor = 10
comparisonFunction = lambda x: int(x/comparisonFactor)

## The input image will be resized to the given size, which will also be the size of the output.
desiredSize = (512, 512)
if (im.size != desiredSize):
    im = im.resize(desiredSize)
#im.save("resized_input.jpg")

## Contains the RGB values of each pixel in the resized input image.
px = im.load()


## Some functions used later, some may be unused like a lot of the commented lines further on, they were just alternative strategies to be tested

def drawGrid(draw,points,coeff2):
    for i in range(1,coeff2+1):
        draw.line((points*i, 0, points*i, im.size[1]), fill=0, width=3)
        draw.line((0,points*i, im.size[1], points*i), fill=0, width=3)
    return

def undrawGrid(draw,points,coeff2,newColorMatrix):
    for j in range(0,coeff2-1):
        if (tuple(map(comparisonFunction,newColorMatrix[0][j])) == tuple(map(comparisonFunction,newColorMatrix[0][j+1]))):
            draw.line((points*0+2, points*(j+1), points*(0+1)-2, points*(j+1)), fill=newColorMatrix[0][j], width=3)
    for i in range(0,coeff2-1):
        if (tuple(map(comparisonFunction,newColorMatrix[i][0])) == tuple(map(comparisonFunction,newColorMatrix[i+1][0]))):
            draw.line((points*(i+1), points*0, points*(i+1), points*1-2), fill=newColorMatrix[i][0], width=3)
    for i in range(1,coeff2):
        for j in range(1,coeff2):
            if (tuple(map(comparisonFunction,newColorMatrix[i][j])) == tuple(map(comparisonFunction,newColorMatrix[i][j-1]))):
                draw.line((points*i+2, points*j, points*(i+1)-2, points*j), fill=newColorMatrix[i][j], width=3)
            if (tuple(map(comparisonFunction,newColorMatrix[i][j])) == tuple(map(comparisonFunction,newColorMatrix[i-1][j]))):
                draw.line((points*i, points*j+2, points*i, points*(j+1)-2), fill=newColorMatrix[i][j], width=3)

def drawRectangles(draw,points,coeff2):
    while(xy2[1][1]<=im.size[1]):
        while(xy2[1][1]<=im.size[1]):
            draw.rectangle(xy, fill=None, outline=(0,0,0))
            xy2[0] = tuple(map(sum,zip(xy2[0],increment1)))
            xy2[1] = tuple(map(sum,zip(xy2[1],increment1)))
        xy2 = xy
        xy2[0] = tuple(map(sum,zip(xy2[0],increment2)))
        xy2[1] = tuple(map(sum,zip(xy2[1],increment2)))

def removeDots(image,points,coeff2,newColorMatrix):
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
    currentCount = 0
    for i in L:
        if (currentCount < L.count(i)):
            currentCount = L.count(i)
            mostCommonColor = (i)
    return mostCommonColor

def normalizeColors(color):
    R=color[0]
    G=color[1]
    B=color[2]
    if normalizeWithFunction:
        return tuple(map(lambda x:int(x/normalizationFactor)*normalizationFactor,color))

    else :
        if (R>(1.4*G) and R>(1.4*B) and R>150):
            return (230,60,60)   #RED

        elif (B>(1*G) and B>(1.5*R) and B>100):
            return (25,60,170)   #BLUE

        elif (R>(2*B) and G>(2*B) and R>100 and G>100):
            return (250,240,60)  #YELLOW

        elif R>=100 and G >=100 and B>=100:
            return (255,255,255) #WHITE

        else:
            return (0,0,0)       #BLACK

## For now the program only uses 512 by 512 pixels images for simplicity
## The image is divided in 16x16 squares of 32x32 pixels each
coeff1 = 32
coeff2 = 16

progress = 0

## Initiates a matrix to hold the RGB values of each region in the split image.
newColorMatrix = [0] * coeff2
for i in range(coeff2):
    newColorMatrix[i] = [0] * coeff2

for x in range(0,coeff2):
    for y in range(0,coeff2):
        if(x==0 and y==0):
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
        newColor3 = normalizeColors(newColor3) #tuple(map(normalizationFunction,newColor3))
        newColorMatrix[x][y] = newColor3
        for i in range(0+coeff1*x,coeff1+coeff1*x):
            for j in range(0+coeff1*y,coeff1+coeff1*y):
                px[i,j]=newColor3

## The program can take some time to run for larger images so these few lines just print the progress to give an idea of how long it will take to run.
        if(x==0 and y==0):
            time2 = time.clock()
            timeRemaining = (time2-time1)*255+1.5
        else:
            timeRemaining -= time.clock()-time2
            time2=time.clock()
        print(' '*10,'Estimated time remaining:', int(timeRemaining), 'seconds',' '*5, end='\r')
        progress += 1/2.56
        print('    '+str(int(progress))+'%'+' '*4, end='\r', flush=True)

print(' '*20,'Finished',' '*20)


points = int(im.size[1]/coeff2)
draw = ImageDraw.Draw(im)

drawGrid(draw,points,coeff2)
undrawGrid(draw,points,coeff2,newColorMatrix)
removeDots(im,points,coeff2,newColorMatrix)

if showOutput:
    im.show()

if saveOutput:
    im.save(filename[0:filename.index(".")]+"_output.png")
