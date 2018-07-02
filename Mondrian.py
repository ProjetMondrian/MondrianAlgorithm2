import itertools
import operator
import time
from PIL import  Image, ImageDraw

im = Image.open("input.jpg")
px = im.load()


## Some functions used later, some may be unused like a lot of the commented lines further on, they were just alternative strategies to be tested

def drawGrid(draw,points,coeff2):
    for i in range(1,coeff2+1):
        draw.line((points*i, 0, points*i, im.size[1]), fill=0, width=3)
        draw.line((0,points*i, im.size[1], points*i), fill=0, width=3)
    return

def undrawGrid(draw,points,coeff2,newColorMatrix):
    for i in range(0,coeff2-1):
        for j in range(0,coeff2-1):
            if (newColorMatrix[i][j] == newColorMatrix[i][j+1]):
                draw.line((points*i, points*j, points*i, points*(j+1)), fill=newColorMatrix[i][j], width=3)
            if (newColorMatrix[i][j] == newColorMatrix[i+1][j]):
                draw.line((points*i, points*j, points*(i+1), points*j), fill=newColorMatrix[i][j], width=3)

def drawRectangles(draw,points,coeff2):
    while(xy2[1][1]<=im.size[1]):
        while(xy2[1][1]<=im.size[1]):
            draw.rectangle(xy, fill=None, outline=(0,0,0))
            xy2[0] = tuple(map(sum,zip(xy2[0],increment1)))
            xy2[1] = tuple(map(sum,zip(xy2[1],increment1)))
        xy2 = xy
        xy2[0] = tuple(map(sum,zip(xy2[0],increment2)))
        xy2[1] = tuple(map(sum,zip(xy2[1],increment2)))

def findMostCommon(L):
    currentCount = 0
    for i in L:
        if (currentCount < L.count(i)):
            currentCount = L.count(i)
            mostCommonColor = (i)
    return mostCommonColor

## For now the program only uses 512 by 512 pixels images for simplicity, will work for all images later
## The image is divided in 16x16 squares of 32x32 pixels each
coeff1 = 32
coeff2 = 16

progress = 0

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
        newColorMatrix[x][y] = newColor3
        for i in range(0+coeff1*x,coeff1+coeff1*x):
            for j in range(0+coeff1*y,coeff1+coeff1*y):
                px[i,j]=newColor3

## The program can take some time to run for larger images so these few lines just print the progress to give an idea of how long it will take
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

#xy = [(0,0),(64,64)]
#increment1 = (0,64)
#increment2 = (64,0)
#xy2= xy
points = im.size[1]/coeff2
draw = ImageDraw.Draw(im)

drawGrid(draw,points,coeff2)
#drawRectangles(draw,points,coeff2)
#undrawGrid(draw,points,coeff2,newColorMatrix)

im.show()
im.save("output.png")
#print(newColorMatrix)
