#Author: Pavel Rozvora
#Email: prozvora@gmail.com
#Date: 2018-03-25

import cv2
import numpy as np
import sys
import math

def main():
    if (len(sys.argv) < 2 or len(sys.argv) > 3):
        print('Usage: python2 NiceDice.py <image filename> [debug].\n')
        print('Typing the \'debug\' option will surround the dice with green boxes')
        print('Press spacebar to cycle through debug images\n')
        sys.exit()

    #initialize outputs
    debug = False
    numDice = 0
    num1 = 0
    num2 = 0
    num3 = 0
    num4 = 0
    num5 = 0
    num6 = 0
    numUnknown = 0

    filename = sys.argv[1]
    #enter debug mode
    if (len(sys.argv) == 3 and sys.argv[2] == 'debug'):
        debug = True

    original = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
    gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3,3), 0)
    #threshold image to remove as much noise as possible
    threshold, binarized = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = np.ones((3,3), np.uint8)
    #remove holes
    opening = cv2.morphologyEx(binarized, cv2.MORPH_OPEN, kernel, iterations=3)

    cont_img = opening.copy()
    _,contours, hierarchy = cv2.findContours(cont_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cropped_dice = []   #list of detected dice
    circled_pips = []   #list of dice with hough circles in the pips

    #count the dice and crop out detected dice to count pips
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 50000:    #ignore noise
            numDice = numDice+1
            #get axis parallel bounding rectangle to crop the dice
            x,y,w,h = cv2.boundingRect(cnt)
            cropped_dice.append(cont_img[y:y+h, x:x+w])
            #create bounding rectangles around the dice for debug
            if debug == True:
                #axis parallel rectangle
                cv2.rectangle(original, (x,y), (x+w, y+h), (0,255,0), 4)

    for die in cropped_dice:
        #invert color of the die to make the pips white and face black
        inv_die = cv2.bitwise_not(die)
        #make pips more pronounced
        circle_kernel = np.array([[0, 1, 1, 1, 0],[1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [0, 1, 1, 1, 0]], np.uint8)
        inv_die = cv2.dilate(inv_die, circle_kernel, iterations=4)
        #perform Hough Circle transform to detect pips
        circles = cv2.HoughCircles(inv_die, cv2.HOUGH_GRADIENT, 1, 50,param1=5, param2=15, minRadius=30, maxRadius=100)
        if circles is None: #if no pips detected on die
            numUnknown = numUnknown+1
            continue
        circles = np.round(circles[0, :]).astype("int")
        num_pips = circles.shape[0]
        if num_pips == 1:
            num1 = num1+1
        elif num_pips == 2:
            num2 = num2+1
        elif num_pips == 3:
            num3 = num3+1
        elif num_pips==4:
            num4 = num4+1
        elif num_pips==5:
            num5 = num5+1
        elif num_pips==6:
            num6 = num6+1
        else:
             numUnknown = numUnknown+1
        color_die = cv2.cvtColor(inv_die, cv2.COLOR_GRAY2BGR)
        for (x, y, r) in circles:
            # draw the circle in the output image, then draw a rectangle
            # corresponding to the center of the circle
            cv2.circle(color_die, (x, y), r, (0, 255, 0), 4)
            cv2.rectangle(color_die, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)

        circled_pips.append(color_die)

    print('INPUT Filename: \t'+filename)
    print('Number of Dice: \t'+repr(numDice))
    print('Number of 1\'s: \t\t'+repr(num1))
    print('Number of 2\'s: \t\t'+repr(num2))
    print('Number of 3\'s: \t\t'+repr(num3))
    print('Number of 4\'s: \t\t'+repr(num4))
    print('Number of 5\'s: \t\t'+repr(num5))
    print('Number of 6\'s: \t\t'+repr(num6))
    print('Number of Unknown: \t'+repr(numUnknown))
    total = num1 + 2*num2 + 3*num3 + 4*num4 + 5*num5 + 6*num6
    print('Total of all dots: \t'+repr(total))

    if debug == True:
        showCv2(original)   #die detection
        for die in circled_pips:    #pip detection
            showCv2(die)


#display images in 3 windows
#destroy windows by pressing any key
def showCv2(image):
    image = cv2.resize(image, (0,0), fx=0.2, fy=0.2)
    cv2.imshow('image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cv2.waitKey(1)

if __name__ == '__main__':
    main()
