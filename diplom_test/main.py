import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os, os.path
import glcm
import pe
import gradients as grds
from PIL import Image
import math

#download folder BMP
def getBMP(fullDir):
    # считаем количество изображений
    fileNumber = len(next(os.walk(fullDir))[2])
    print(fileNumber, "pictures were found")
    imgArr = []
    for i in range(1, fileNumber + 1):
        imgArr.append(mpimg.imread(fullDir + '/' + str(i) + ".bmp"))
    print(len(imgArr), "image was read")
    #дописать исключения
    return imgArr
#process RGB/grayscale
def rgb2gray(rgb):
    #скалярное произведение начальных цветов с определенными теоретическими коэффициентами по системе YUV
    return np.dot(rgb[...,:3], [0.333, 0.333, 0.333]).round(3).astype(int)


def averageRGB(img, windW, windH):
    #укрупним области
    w = len(img[0])
    h = len(img)
    ed = img
    for i in range(h-(windH-1)):
        for j in range(w-(windW-1)):
            R,G,B = 0,0,0
            for a in range (windH):
                for b in range (windW):
                    R += ed[i+a][j+b][0]
                    G += ed[i+a][j+b][1]
                    B += ed[i+a][j+b][2]
            size = windW * windH
            R /= size
            G /= size
            B /= size
            for a in range (windH):
                for b in range (windW):
                    ed[i+a][j+b][0] = R
                    ed[i+a][j+b][1] = G
                    ed[i+a][j+b][2] = B
    return ed


def averageGray(img, windW, windH):
    #укрупним области
    w = len(img[0])
    h = len(img)
    ed = img
    for i in range(h-(windH-1)):
        for j in range(w-(windW-1)):
            G = 0
            for a in range (windH):
                for b in range (windW):
                    G += ed[i+a][j+b]
            size = windW * windH
            G /= size
            for a in range (windH):
                for b in range (windW):
                    ed[i+a][j+b] = G
    return ed
#normalization to the summ
def normalizeArray2D(table):
    size1 = len(table)
    size2 = len(table[0])
    sum = 0
    rez = np.zeros([size1,size2],dtype=float)
    for i in range (size1):
        for j in range (size2):
            sum += table[i][j]
    for i in range(size1):
        for j in range(size2):
            rez[i][j] = table[i][j]/sum
    return rez


# getting the current working directory
cwd = os.getcwd()

# reading of our images
print("Donwloading images for a pathological and a normal state of a kidney parenchyma for our ultrasonography:")
pathoFull = cwd + "/pathology"
pathoBMP = getBMP(pathoFull)
for i in range (len(pathoBMP)):
    pathoBMP[i] = rgb2gray(pathoBMP[i])

normaFull = cwd + "/norma"
normaBMP = getBMP(normaFull)
for i in range (len(normaBMP)):
    normaBMP[i] = rgb2gray(normaBMP[i])

# auh = autoimmune hepatitis
auhFull = cwd + "/unCheckPatho/auh"
auhBMP = getBMP(auhFull)
for i in range(len(auhBMP)):
    auhBMP[i] = rgb2gray(auhBMP[i])

# PE works but have NO sense
'''
# PERMUTATION ENTROPY and ordinal patterns calculations and processing
patternNumber = 5
#min, max, increasing, decreasing, stability
patternAXIS1 = 1
patternAXIS2 = 4
AXIS1name = "МАКСИМУМ, %"
AXIS2name = "СТАБІЛЬНІСТЬ, %"

print('\nPathological specimens')
pathoPEpatterns = np.zeros((1, patternNumber))
for i in range(len(pathoBMP)):
    tmp = pe.pe(pathoBMP[i])
    tmp.PErawAnalysis(10)
    # это чтобы добавить 1 (!!!) отметку в легенду, мб исправить потом
    # НАДО перейти к scatter (!!!)
    plt.plot(tmp.rez[0][patternAXIS1],
             tmp.rez[0][patternAXIS2],
             'ro')
    #label='pathological SAMPLES'
    for j in range(patternNumber):
        pathoPEpatterns[0][j] += tmp.rez[0][j]

for k in range(patternNumber):
    pathoPEpatterns[0][k] /= len(pathoBMP)
plt.plot(pathoPEpatterns[0][patternAXIS1],
         pathoPEpatterns[0][patternAXIS2],
         'r*', label='pathological AVERAGE',
         markersize=30)
print(pathoPEpatterns)

print('Normal specimens')
normaPEpatterns = np.zeros((1, patternNumber))
for i in range(len(normaBMP)):
    tmp = pe.pe(normaBMP[i])
    tmp.PErawAnalysis(10)
    plt.plot(tmp.rez[0][patternAXIS1],
             tmp.rez[0][patternAXIS2],
             'b^')
    for j in range(patternNumber):
        normaPEpatterns[0][j] += tmp.rez[0][j]

for k in range(patternNumber):
    normaPEpatterns[0][k] /= len(normaBMP)
plt.plot(normaPEpatterns[0][patternAXIS1],
         normaPEpatterns[0][patternAXIS2],
         'b*', label='normal AVERAGE',
         markersize=30)
print(normaPEpatterns)

perc = np.zeros((1, patternNumber))
for i in range(patternNumber):
    dif = abs(normaPEpatterns[0][i] - pathoPEpatterns[0][i])
    perc[0][i] = (dif / max(normaPEpatterns[0][i], pathoPEpatterns[0][i])) * 100
print('Normalized difference in percents:')
print(perc)

plt.xlabel(AXIS1name)
plt.ylabel(AXIS2name)
plt.legend()
plt.savefig('ordinal_patterns.png')
'''

fig = plt.figure(figsize=(10, 10), dpi=80, facecolor='w', edgecolor='k')
# grCoMap = plt.get_cmap('gray')

# 5x5 картинок
'''
columns = 5
rows    = math.ceil(len(pathoBMP) / columns)
for i in range(len(normaBMP)):
    curIm = normaBMP[i]
    #curIm = curIm[0:3,0:3]
    #plt.imshow(curIm)
    curRow, curCol = 0, 0
    calculation = glcm.GLCM(curIm).glcm_complex_duplex()
    number = i+1
    print(rows,columns,number)
    fig.add_subplot(rows,columns,number)
    plt.imshow(calculation)
    plt.tight_layout()
plt.savefig('norma.png')
'''

# сохран всех 50 картинок глцм в папку временных
'''
for i in range(len(normaBMP)):
    curIm = normaBMP[i]
    calculation = glcm.GLCM(curIm).glcm_complex_duplex()
    number = i+1
    print(number)
    plt.imshow(calculation)
    path = "glcm/n/n" + str(number) + ".png"
    plt.imsave(path, calculation, cmap="inferno")
print("norma was saved sucessfull")
for i in range(len(pathoBMP)):
    curIm = pathoBMP[i]
    calculation = glcm.GLCM(curIm).glcm_complex_duplex()
    number = i+1
    print(number)
    plt.imshow(calculation)
    path = "glcm/p/p" + str(number) + ".png"
    plt.imsave(path, calculation, cmap="inferno")
print("pathology was saved sucessfull")
'''

for i in range(len(normaBMP)):
    curIm = normaBMP[i]
    calculation = glcm.GLCM(curIm).glcm_complex_duplex()
    number = i + 1
    print(number)
    # plt.imshow(calculation)
    path = "glcm/n/n" + str(number) + ".csv"
    np.savetxt(path, calculation, fmt="%d", delimiter=",")
for i in range(len(pathoBMP)):
    curIm = pathoBMP[i]
    calculation = glcm.GLCM(curIm).glcm_complex_duplex()
    number = i + 1
    print(number)
    # plt.imshow(calculation)
    path = "glcm/p/p" + str(number) + ".csv"
    np.savetxt(path, calculation, fmt="%d", delimiter=",")
for i in range(len(auhBMP)):
    curIm = auhBMP[i]
    calculation = glcm.GLCM(curIm).glcm_complex_duplex()
    number = i + 1
    print(number)
    # plt.imshow(calculation)
    path = "glcm/auh/auh" + str(number) + ".csv"
    np.savetxt(path, calculation, fmt="%d", delimiter=",")

## GLCM results' saving
# plt.imsave("tmp/tmp2.png",gray, cmap=grCoMap)


'''
# считывание 1го изображение для тестов
original = mpimg.imread("pathology/14.bmp")
#original = original[0:20,0:20,:]
fig = plt.figure()
#plt.subplot(211)
#plt.imshow(original)
#plt.title("Оригінальне зображення")
plt.imsave("tmp/tmp1.png", original)
rawGray = rgb2gray(original)
gray = np.array(rawGray)
calculation = glcm.GLCM(gray).glcm_complex_duplex()
#grCoMap = plt.get_cmap('gray')
ax = fig.add_subplot(111)
# GLCM results' saving
plt.imshow(calculation)
#cmap=grCoMap

#plt.imsave("tmp/tmp2.png",gray, cmap=grCoMap)
'''

'''
ax = fig.add_subplot(212)
plt.imshow(gray, cmap=grCoMap)
plt.title("Original")
'''

# this code computes and plots gradients of the image
'''
dif = grds.gradient(gray)
plt.subplot(323)
dif.computeHorizontal()
plt.imshow(dif.getHorizontal(),cmap="inferno")
plt.title("Horizontal")
plt.subplot(324)
dif.computeVertical()
plt.imshow(dif.getVertical(),cmap="inferno")
plt.title("Vertical")
plt.subplot(325)
dif.computeDiagonal135()
plt.imshow(dif.getDiagonal135(),cmap="inferno")
plt.title("Diagonal135")
plt.subplot(326)
dif.computeDiagonal45()
plt.imshow(dif.getDiagonal45(),cmap="inferno")
plt.title("Diagonal45")
fig.tight_layout()
## save
#fig.savefig("tmp/p5.pdf")
'''

# attempt to plot the red-blue mask on the gray image
'''
#img = Image.fromarray(grayAsRGB.astype(np.uint8))
img = Image.open("tmp/tmp2.png")
plt.subplot(312)
plt.imshow(np.array(img))
plt.title("Аугментоване зображення")
px = img.load()
maxFreq = np.amax(calculation)
maxRed  = 0.5
maxBlue = 0.3
reds  = np.arange(0,maxRed, 0.1) * 255
blues = np.arange(0,maxBlue,0.1) * 255
def paintPixelPIL(img,x,y,r,g,b):
    R = img.getpixel((x, y))[0] + r
    G = img.getpixel((x, y))[1] + g
    B = img.getpixel((x, y))[2] + b
    img.putpixel((x, y), (R, G, B))
    return img
print('len(ed)-1=',len(ed)-1,'\n')
print('len(ed[0])-1',len(ed[0])-1,'\n')
for i in range (len(ed)-1):
    for j in range (len(ed[0])-1):
        if calculation [ed[i][j]-1] [ed[i][j+1]-1] <= 0.15*maxFreq:
            paintPixelPIL(img, i, j,   90, 0, 0)
            paintPixelPIL(img, i, j+1, 90, 0, 0)
        else:
            if calculation [ed[i][j]-1] [ed[i][j+1]-1] <= 0.3*maxFreq:
                paintPixelPIL(img, i, j,   55, 0, 0)
                paintPixelPIL(img, i, j+1, 55, 0, 0)
            else:
                if calculation[ed[i][j] - 1][ed[i][j + 1] - 1] <= 0.45*maxFreq:
                    paintPixelPIL(img, i, j,     40, 0, 40)
                    paintPixelPIL(img, i, j + 1, 40, 0, 40)
                else:
                    if calculation[ed[i][j] - 1][ed[i][j + 1] - 1] <= 0.6 * maxFreq:
                        paintPixelPIL(img, i, j, 0, 0, 55)
                        paintPixelPIL(img, i, j + 1, 0, 0, 55)
                    else:
                        if calculation[ed[i][j] - 1][ed[i][j + 1] - 1] <= 0.75 * maxFreq:
                            paintPixelPIL(img, i, j, 0, 0, 90)
                            paintPixelPIL(img, i, j + 1, 0, 0, 90)

img.save("tmp/colorized.png", "PNG", quality = 100)
im2arr = np.array(img)
plt.subplot(313)
plt.imshow(im2arr)
plt.title("Зображення, покрите маскою на основі GLCM")
'''

# labels for GLCM
'''
plt.title("Color-Color symmetrical GLCM")
plt.xlabel("color1")
plt.ylabel("color2")
#plt.legend()
'''

plt.show()
