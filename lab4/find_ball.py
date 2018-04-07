#!/usr/bin/env python3

import cv2
import sys
import copy

import numpy as np

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit('install Pillow to run this code')


def find_ball(opencv_image, debug=False):
    """Find the ball in an image.
        
        Arguments:
        opencv_image -- the image
        debug -- an optional argument which can be used to control whether
                debugging information is displayed.
        
        Returns [x, y, radius] of the ball, and [0,0,0] or None if no ball is found.
    """

    ball = None
    THRESHOLD = 50
    SIMPLE_THRESHOLD = 50
    # Normalize the image
    normalizedImg = np.zeros(opencv_image.shape)
    normalizedImg = cv2.normalize(opencv_image,  normalizedImg, 0, 255, cv2.NORM_MINMAX)
    
    circles = cv2.HoughCircles(normalizedImg,cv2.HOUGH_GRADIENT,1,10,param1=70,param2=50,minRadius=1)
    
    
    # Loop through each returned circle.  First convert the circles to int values for pixels.  Make sure the center is
    # in the image and that the center pixel is sufficiently black.  Then calculate the interior average of the found
    # circle.  If the interior average is sufficiently black and blacker than a previous circle use the new one.
    last_best = 255;
    if circles is not None:
        circles = np.uint16(np.around(circles[0,:]))
        [h,w] = np.ogrid[:opencv_image.shape[0],:opencv_image.shape[1]]
        for circle in circles:
            if circle[1] < len(h[:,0]) and circle[0] < len(w[0,:]) and normalizedImg[circle[1]][circle[0]] < SIMPLE_THRESHOLD:
                interior = calculateInterior(normalizedImg, h, w, circle[1], circle[0], circle[2]*9/10)
                #print(interior)
                #display_circles(opencv_image,None,circle, interior)
                if( interior < THRESHOLD and interior < last_best):
                    last_best = interior
                    ball = circle
    #print("\nLast best is: "+str(last_best))
    return ball


# Helper function to calculate the average pixels inside the circle.  
# Adapted from some code found on stack overflow to mask an image with a circle
def calculateInterior(img, h, w, ch, cw, r):  
    dist_from_center = np.sqrt((h - ch)**2 + (w-cw)**2)
    mask = dist_from_center <= r
    sum = 0;
    count = 0;
    # Look at the square surrounding the circle only for performance reasons and find average
    # pixel value in the circle
    for i in range(int(max(h[:,0][0],ch-r)),int(min(h[:,0][-1],ch+r))):
        for j in range(int(max(w[0,:][0],cw-r)),int(min(w[0,:][-1],cw+r))):
            if mask[i][j]:
                sum = sum + img[i][j]
                count = count + 1
   
    if( count > 0):
        return sum/count
    else:
        return 255
    
def display_circles(opencv_image, circles, best=None, sum=0):
    """Display a copy of the image with superimposed circles.
        
       Provided for debugging purposes, feel free to edit as needed.
       
       Arguments:
        opencv_image -- the image
        circles -- list of circles, each specified as [x,y,radius]
        best -- an optional argument which may specify a single circle that will
                be drawn in a different color.  Meant to be used to help show which
                circle is ranked as best if there are multiple candidates.
        
    """
    #make a copy of the image to draw on
    circle_image = copy.deepcopy(opencv_image)
    circle_image = cv2.cvtColor(circle_image, cv2.COLOR_GRAY2RGB, circle_image)
    
    if circles is not None:
        for c in circles:
            # draw the outer circle
            cv2.circle(circle_image,(c[0],c[1]),c[2],(255,255,0),2)
            # draw the center of the circle
            cv2.circle(circle_image,(c[0],c[1]),2,(0,255,255),3) 
            # write coords
            #cv2.putText(circle_image,str(c)+" "+str(sum),(c[0],c[1]),cv2.FONT_HERSHEY_SIMPLEX,
            #            .5,(255,255,255),2,cv2.LINE_AA)            
    
    #highlight the best circle in a different color
    if best is not None:
        # draw the outer circle
        cv2.circle(circle_image,(best[0],best[1]),best[2],(0,0,255),2)
        # draw the center of the circle
        cv2.circle(circle_image,(best[0],best[1]),2,(0,0,255),3) 
        # write coords
        cv2.putText(circle_image,str(best)+" "+str(sum),(best[0],best[1]),cv2.FONT_HERSHEY_SIMPLEX,
                    .5,(255,255,255),2,cv2.LINE_AA)            
        
    
    #display the image
    pil_image = Image.fromarray(circle_image)
    pil_image.show()    
      
if __name__ == "__main__":
    pass
