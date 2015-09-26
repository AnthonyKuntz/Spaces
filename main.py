from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime
from Tkinter import *
from collections import Counter

import ctypes
import _ctypes
import sys
import os
from random import randint

if sys.hexversion >= 0x03000000:
    import _thread as thread
else:
    import thread

# file transfer scripts
import imageTransfer


class KinectInterface(object):

    def __init__(self):
        self.width = 1500
        self.height = 700
        # Get updates every 100ms
        self.timerDelay = 50
        self.kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body)
        self.leftHandStates = []
        self.rightHandStates = []
        self.oldLeftHandPos = ('inf','inf')
        self.oldRightHandPos = ('inf','inf')
        self.oldSpineBasePos = ('inf','inf')
        self.isDragging = False
        self.updateCounter = 0
        self.images = []
        self.baseURL = "http://128.237.138.95:3000"
        self.imageTransferer = imageTransfer.imageTransfer(self.baseURL, self.images, "ak")
        self.updatedFrame = True
        self.indexBeingDragged = None
        self.thisFrameHasBody = False
        self.lastFrameHadBody = False
        self.swipingRight = False
        self.swipingLeft = False
        
    def initAnimation(self):
        self._frame_surface = self.canvas
        self.dock = Dock(self.canvas,800,200,200,400)
        self.listOfSpaces = []


    # def draw_color_frame(self, frame, target_surface):
    #     target_surface.lock()
    #     address = self.kinect.surface_as_array(target_surface.get_buffer())
    #     ctypes.memmove(address, frame.ctypes.data, frame.size)
    #     del address
    #     target_surface.unlock()

    def initSpaceFromList(self, image):
        self.listOfSpaces += [Space(image, "red", self.canvas)]

    def onTimerFiredWrapper(self):
        if (self.timerDelay == None):
            return # turns off timer
        self.onTimerFired()

        if (self.updateCounter % (1000/self.timerDelay) == 0):
            self.imageTransferer.updateImages(self.initSpaceFromList)

        self.updateCounter += 1
        self.canvas.after(self.timerDelay, self.onTimerFiredWrapper) 

    def onTimerFired(self):
        self.lastFrameHadBody = self.thisFrameHasBody
        self.thisFrameHasBody = False
        if self.kinect.has_new_body_frame():

            body_frame = self.kinect.get_last_body_frame()

            if body_frame is not None:

                self.updatedFrame = False
                for i in range(0, self.kinect.max_body_count):
                    body = body_frame.bodies[i]
                    
                    if body.is_tracked:
                        self.thisFrameHasBody = True
                        # Get hand positions, deltas, and states (open/close)

                        # Values for enumeration '_JointType'
                        # JointType_SpineBase = 0
                        # JointType_SpineMid = 1
                        # JointType_Neck = 2
                        # JointType_Head = 3
                        # JointType_ShoulderLeft = 4
                        # JointType_ElbowLeft = 5
                        # JointType_WristLeft = 6
                        # JointType_HandLeft = 7
                        # JointType_ShoulderRight = 8
                        # JointType_ElbowRight = 9
                        # JointType_WristRight = 10
                        # JointType_HandRight = 11
                        # JointType_HipLeft = 12
                        # JointType_KneeLeft = 13
                        # JointType_AnkleLeft = 14
                        # JointType_FootLeft = 15
                        # JointType_HipRight = 16
                        # JointType_KneeRight = 17
                        # JointType_AnkleRight = 18
                        # JointType_FootRight = 19
                        # JointType_SpineShoulder = 20
                        # JointType_HandTipLeft = 21
                        # JointType_ThumbLeft = 22
                        # JointType_HandTipRight = 23
                        # JointType_ThumbRight = 24

                        joints = body.joints
                        joint_points = self.kinect.body_joints_to_color_space(joints)
                        leftHand = joint_points[PyKinectV2.JointType_HandLeft]
                        rightHand = joint_points[PyKinectV2.JointType_HandRight]
                        spineBase = joint_points[PyKinectV2.JointType_SpineBase]

                        leftHandPos = (leftHand.x, leftHand.y)
                        rightHandPos = (rightHand.x, rightHand.y)
                        spineBasePos = (spineBase.x, spineBase.y)

                        try:
                            leftHandDelta = (leftHandPos[0] - self.oldLeftHandPos[0], 
                                             leftHandPos[1] - self.oldLeftHandPos[1])
                            rightHandDelta = (rightHandPos[0] - self.oldRightHandPos[0],
                                              rightHandPos[1] - self.oldRightHandPos[1])
                            spineBaseDelta = (spineBasePos[0] - self.oldSpineBasePos[0],
                                              spineBasePos[1] - self.oldSpineBasePos[1])
                        except TypeError:
                            leftHandDelta = (0,0)
                            rightHandDelta = (0,0)
                            spineBaseDelta = (0,0)

                        self.oldRightHandPos = rightHandPos
                        self.oldLeftHandPos = leftHandPos
                        self.oldSpineBasePos = spineBasePos

                        if len(self.leftHandStates) < 10:
                            self.leftHandStates.append(body.hand_left_state)
                            leftHandState = 0
                        else:
                            self.leftHandStates.remove(self.leftHandStates[0])
                            self.leftHandStates.append(body.hand_left_state)
                            data = Counter(self.leftHandStates)
                            leftHandState = data.most_common(1)[0][0]

                        if len(self.rightHandStates) < 10:
                            self.rightHandStates.append(body.hand_right_state)
                            rightHandState = 0
                        else:
                            self.rightHandStates.remove(self.rightHandStates[0])
                            self.rightHandStates.append(body.hand_right_state)
                            data = Counter(self.rightHandStates)
                            rightHandState = data.most_common(1)[0][0]


                        # Do actions based on hand pos, deltas, state
                        
                        # values for enumeration '_HandState'
                        # HandState_Unknown = 0
                        # HandState_NotTracked = 1
                        # HandState_Open = 2
                        # HandState_Closed = 3
                        # HandState_Lasso = 4

                        # if rightHandState == 3:
                        #     print "right hand closed"
                        # elif rightHandState == 2:
                        #     print "right hand open"

                        # if leftHandState == 3:
                        #     print "left hand closed"
                        # elif leftHandState == 2:
                        #     print "left hand closed"

                        if (rightHandDelta[0] - spineBaseDelta[0] > 40 and 
                              abs(rightHandDelta[1] - spineBaseDelta[1]) < 10 and
                              rightHandPos[1] - 300 > self.height *9.0/10 and 
                              not self.isDragging and not self.swipingRight):
                            #print "swipe right", rightHandDelta[0] - spineBaseDelta[0]
                            self.dock.shift(1)
                            self.swipingRight = True
                        else :
                            self.swipingRight = False

                        if (leftHandDelta[0] - spineBaseDelta[0] < -40 and
                                abs(leftHandDelta[1] - spineBaseDelta[1]) < 10 and
                                rightHandPos[1] - 300 > self.height *9.0/10 and 
                                not self.swipingLeft):
                            #print "swipe left", leftHandDelta[0] - spineBaseDelta[0]
                            self.dock.shift(-1)
                            self.swipingLeft = True
                        else:
                            self.swipingLeft = False

                        if (rightHandState == 3 and rightHandPos[1] - 300 > self.height *9.0/10):
                            pass

                        if (rightHandState == 2 and 
                                (abs(rightHandDelta[0]) > 0 or
                                 abs(rightHandDelta[1]) > 0)) and self.listOfSpaces != []:
                            # if self.listOfSpaces != []:
                            #     for space in self.listOfSpaces:
                            #         print space.centerX, space.centerY, "hand at", rightHandPos
                            self.isDragging = True
                            if self.indexBeingDragged == None:
                                minDist = 999999999
                                closestI = None
                                for i in xrange(len(self.listOfSpaces)):
                                    thisDist = self.listOfSpaces[i].distanceFromCenter(1919-rightHandPos[0], rightHandPos[1])
                                    if (minDist == None or thisDist < minDist) and self.listOfSpaces[i].selected:
                                        # print thisDist, minDist, i, "this, min, i" 
                                        minDist = thisDist
                                        closestI = i
                                self.indexBeingDragged = closestI
                            if self.indexBeingDragged != None:
                                self.listOfSpaces[self.indexBeingDragged].updatePositionByD(-rightHandDelta[0], rightHandDelta[1])
                            #print rightHandDelta
                            #print rightHandPos
                        else:
                            if self.isDragging:
                                if rightHandPos[1] - 300 > self.height *9.0/10:
                                    if self.indexBeingDragged != None:
                                        self.listOfSpaces[self.indexBeingDragged].deselect()
                                        self.listOfSpaces[self.indexBeingDragged].updatePosition(self.width/2, self.height/2)
                                        print "deselected"
                                        self.dock.addImg(self.listOfSpaces[self.indexBeingDragged])

                            self.isDragging = False
                            self.indexBeingDragged = None

        if not self.thisFrameHasBody and self.lastFrameHadBody:
            self.oldSaveSpace()
                
    
    def saveSpace(self):
        if self.updatedFrame: return
        self.updatedFrame = True
        frame = self.kinect.get_last_color_frame().tolist()
        self.newList = []

        topBottomCrop = 108*3
        leftRightCrop = 384*2
        fullHeight = 1080
        fullWidth = 1920
        rMax = 100
        bMax = 100
        gMax = 100

        for row in range(topBottomCrop, fullHeight - topBottomCrop):
            for col in range(leftRightCrop, fullWidth - leftRightCrop):
                index = (row * fullWidth + col) * 4
                r = frame[index - 1]
                g = frame[index - 2]
                b = frame[index - 3]
                
                # if(row < 10 and col < 10):
                #     print "r:", r, "g:", g, "b:", b
                
                if(r < rMax and g < gMax and b < bMax):
                    self.newList += [[row, col]]
        
        # add saved image to images list
        self.images.append(self.newList)
        self.listOfSpaces += [ Space(self.newList, "blue", self.canvas) ]
            
    def oldSaveSpace(self):

        # save space
        if self.updatedFrame: return
        self.updatedFrame = True
        frame = self.kinect.get_last_color_frame().tolist()
        self.newList = []
        for j in range(108*3,1080-108*3):
            for i in range(j*1920*4,j*1920*4+1920*4,4):
                col = i%(j*1920*4)/4 if j != 0 else i
                if col < 1920*1.0/3 or col > 1920*2.0/3: continue
                r = frame[i - 2]
                g = frame[i - 3]
                b = frame[i - 4]
                # if j < 10 and i < 10: print r,g,b
                h, s, v = self.rgb2hsv(r,g,b)
                s *= 100
                v *= 100
                # if j < 10 and i < 10: print h,s,v
                isBlack = v <= 60 and abs(r-g) < 50 and abs(r-b) < 20 and abs(b-g) < 50
                # if j < 10 and i < 10: print isBlack
                
                
                
                if isBlack:
                    row = j
                    col = i%(j*1920*4)/4 if j != 0 else i
                    self.newList += [[row, col]]
        
        # add saved image to images list
        self.images.append(self.newList)
        self.listOfSpaces += [ Space(self.newList, "blue", self.canvas) ]

        

    # def makeJonImage(self, image):
    #     jonImage = []
    #     counter = 0
    #     for row in range(1080):
    #         thisRow = []
    #         for col in range(1920-1,-1,-1):
    #             r = image[row][col][2]
    #             g = image[row][col][1]
    #             b = image[row][col][0]
    #             h, s, v = self.rgb2hsv(r,g,b)
    #             s *= 100
    #             v *= 100
    #             isOrange = v <= 60 or (v <= 70 and s <= 20)
    #             # isOrange = r + b + g > 500
    #             thisRow += [int(isOrange)]
    #         jonImage += [thisRow]
    #     return jonImage


    @staticmethod
    def rgb2hsv(r, g, b):
        r, g, b = r/255.0, g/255.0, b/255.0
        mx = max(r, g, b)
        mn = min(r, g, b)
        df = mx-mn
        if mx == mn:
            h = 0
        elif mx == r:
            h = (60 * ((g-b)/df) + 360) % 360
        elif mx == g:
            h = (60 * ((b-r)/df) + 120) % 360
        elif mx == b:
            h = (60 * ((r-g)/df) + 240) % 360
        if mx == 0:
            s = 0
        else:
            s = df/mx
        v = mx
        return h, s, v

    # def onKeyPressed(self,event):
    #     if event.keysym == "t":
    #         # print self.newList
    #         for (row, col) in self.newList:
    #             self.canvas.create_rectangle(col,row,col,row,fill = "black")
    #         return
    #     self.imageList = self.jonsImage
    #     self.photo = PhotoImage(width = 1920, height = 1080)
    #     print len(self.imageList)
    #     print len(self.imageList[0])
    #     for row in xrange(1080):
    #         for col in xrange(1920):
    #             self.photo.put(self.rgbString(self.imageList[row][col]*255,self.imageList[row][col]*165,0), (col, row))
    #     self.canvas.create_image(0,0,anchor = NW, image = self.photo)
        # newFilename = "output.gif"
        # newFilepath = self.getPath(newFilename)
        # self.photo.save(newFilepath)

    # def rgbString(self, red, green, blue):
    #     return "#%02x%02x%02x" % (red, green, blue)

    # def getPath(self, filename):
    #     # Appends filename to end of current directory path
    #     return os.path.dirname(__file__) + os.sep + filename

    # From course notes at cs.cmu.edu/~112 Fall 14
    def run(self):
        # create the root and the canvas
        self.root = Tk()
        self.root.resizable(False, False)
        color = "white" # Boring color
        self.canvas = Canvas(self.root, width=self.width,
            height=self.height, background = color)

        ratio = 1
        heightRatio = 1/5.0
        self.smallCanvas = Canvas(self.root, width =self.width*ratio, # For making a UI
            height = self.height*heightRatio, background = "grey") 

        self.canvas.pack()
        self.smallCanvas.pack()
        self.initAnimation()
        # set up events
        # def f(event): self.mouseMotion(event)
        # self.canvas.bind("<Motion>", f)
        # def f(event): self.onMousePressedWrapper(event)    
        # self.root.bind("<Button-1>", f)
        # def f(event): self.onKeyPressed(event)
        # self.root.bind("<Key>", f)
        self.onTimerFiredWrapper()
        self.root.mainloop()


class Dock(object):

    #(self, listOfPoints, color, canvas)

    def testImages(self,n):
        # 1920/1080
        self.spaces = [Space([(randint(0,1080),randint(0,1920)) for _ in xrange(randint(1000,10000))],"blue",self.canvas) for _ in xrange(n)]
        self.canvas.delete(ALL)
 #       return [[(randint(0,1080),randint(0,1920)) for _ in xrange(randint(1000,10000))] for _ in xrange(n)]

    # Takes in the list representing a Space
    # and returns a thumbnail image for that Space
    def makeDocImg(self, space):
        self.blank = PhotoImage(file = "blank.gif")
        for coord in space.listOfPoints:
            y, x = coord
            try: self.blank.put("#000000", (x, y))
            except: pass
        self.smallImg = self.blank.subsample(10,10)
        return self.smallImg

    def __init__(self,canvas,x,y,w,h,spaces=""):
        self.canvas = canvas
        self.i = 0
        self.spaces = list(spaces)
        self.testImages(1)
        self.blankspace = PhotoImage(file = "blank.gif").subsample(10,10)
        self.thumbs = [self.makeDocImg(locs) for locs in self.spaces]
        self.start = 0
        (self.x, self.y, self.w, self.h) = (x,y,w,h)
        self.displayed = 3
        self.initDraw()

    def addImg(self,locs):
        self.spaces.insert(0,locs)
        self.thumbs.insert(0,self.makeDocImg(locs))
        self.start += 1
        self.i += 1

    def loadImg(self):
        self.spaces[self.i].drawPixels()

    def initDraw(self):
        self.shownFrames = []
        (x,y,w,h) = (self.x, self.y, self.w, self.h)
        self.margin = margin = w/50.0
        self.w2 = w2 = (h - (self.displayed+1) * margin)/self.displayed
        self.canvas.create_rectangle(x,y,x+w,y+h,outline="orange",fill="white",width=5)
        for i in xrange(min(len(self.spaces),self.displayed)):
            top = y + margin*(i+1) + w2*i
            self.shownFrames += [(top,self.canvas.create_image(x+margin,top,image=self.thumbs[i],anchor=NW))] #added imageOffset to left -J
            if i == self.i:
                self.tracker = self.canvas.create_rectangle(x-25,top+margin,x,top+25,fill="orange",outline="orange")

    def shift(self,shift):
        if self.i + shift < 0 or (self.i + shift) >= len(self.spaces): return
        elif (self.i + shift < self.start) or (self.i + shift == self.start + self.displayed):
            self.windowShift(shift)
        else:
            i = (self.i + shift) - self.start
            top = self.y + self.margin*(i+1) + self.w2*i
            self.canvas.delete(self.tracker)
            self.tracker = self.canvas.create_rectangle(self.x-25,top+self.margin,self.x,top+25,fill="orange",outline="orange")
        self.i += shift

    def windowShift(self, shift=1):
        shiftTo = min(max(0, self.start + shift),max(0,len(self.spaces)-self.displayed))
        actualShift = shiftTo - self.start
        self.start = shiftTo
        margin = self.w/50.0
        w2 = (self.h - (self.displayed+1) * margin)/self.displayed
        bottom = self.y + margin*self.displayed + w2*(self.displayed - 1)
        for i in xrange(actualShift):
            f = self.shownFrames.pop(0)
            self.canvas.delete(f[1])
            for i in xrange(len(self.shownFrames)):
                f = self.shownFrames[i]
                top = f[0]
                self.canvas.coords(f[1],(self.x + margin,top-w2-margin))
                self.shownFrames[i] = (top-w2-margin,f[1])
            self.shownFrames += [ (bottom, self.canvas.create_image(self.x+margin,bottom,image=self.thumbs[self.start+self.displayed-1],anchor=NW) ) ]
        for i in xrange(-actualShift):
            f = self.shownFrames.pop()
            self.canvas.delete(f[1])
            for i in xrange(len(self.shownFrames)):
                f = self.shownFrames[i]
                top = f[0]
                self.canvas.coords(f[1],(self.x+margin,top+w2+margin))
                self.shownFrames[i] = (top+w2+margin,f[1])
            self.shownFrames.insert(0,(self.y+margin,
                                self.canvas.create_image(self.x+margin,self.y+margin,image=self.thumbs[self.start],anchor=NW)))

# class ImageCropper(object):
    
#     @staticmethod
#     def crop(image):
#         """ 
#         takes in an 2D array of 1s and 0s and crops around all the 1s
        
#         image: 2D array of 1s and 0s
#                represent a map over an image where pixels that match the
#                the desired color go to 1 and other pixels go to 0
#         """
        
#         # Get width, height of image
#         width = len(image[0])
#         height = len(image)
        
#         crop_left = width-1
#         crop_right = 0
#         crop_up = height-1
#         crop_down = 0
        
#         row_index = 0
#         col_index = 0
#         crop_row = True
        
#         for row in image:
#             for val in row:
                
#                 if val == 1:
#                     crop_row = False
#                     crop_left = min(crop_left, col_index)
#                     crop_right = max(crop_right, col_index)
                
#                 col_index += 1
            
#             if not crop_row:
#                 crop_up = min(crop_up, row_index)
#                 crop_down = max(crop_down, row_index)
            
#             row_index += 1
#             col_index = 0
#             crop_row = True
      
#         cropped_image = [[0]*(crop_right-crop_left+1) 
#                 for _ in range(crop_down-crop_up+1)]
       
#         for i in range(0, crop_down-crop_up+1):
#             for j in range(0, crop_right-crop_left+1):
#                 cropped_image[i][j] = image[i + crop_left][j+crop_up]
       
#         return cropped_image

    # @staticmethod
    # def crop2(image, color):
    #     """ 
    #     takes in an image and returns the smallest rectangle that contains 
    #     all color colored pixels
        
    #     image: image represented as 2D array of (r,g,b,a) quadruples
    #     color: color represened as (r,g,b,a) quadruple
    #     """
        
    #     # Get width, height of image
    #     width = len(image[0])
    #     height = len(image)
        
    #     # get r,g,b,a values of color to crop with
    #     (r,g,b,a) = color
        
    #     crop_left = width-1
    #     crop_right = 0
    #     crop_up = height-1
    #     crop_down = 0
        
    #     row_index = 0
    #     col_index = 0
    #     crop_row = True
        
    #     color_tolerance = 10
        
    #     for row in image:
    #         for pixel in row:
    #             (r2,g2,b2,a2) = pixel
                
    #             if (abs(r2-r) < color_tolerance and 
    #                     abs(g2-g) < color_tolerance and 
    #                     abs(b2-b) < color_tolerance and 
    #                     abs(r2-r) < color_tolerance):
    #                 crop_row = False
    #                 crop_left = min(crop_left, col_index)
    #                 crop_right = max(crop_right, col_index)
                
    #             col_index += 1
            
    #         if not crop_row:
    #             crop_up = min(crop_up, row_index)
    #             crop_down = max(crop_down, row_index)
            
    #         row_index += 1
    #         col_index = 0
    #         crop_row = True
      
    #     cropped_image = [[0]*(crop_right-crop_left+1) 
    #             for _ in range(crop_down-crop_up+1)]
       
    #     for i in range(0, crop_down-crop_up+1):
    #         for j in range(0, crop_right-crop_left+1):
    #             cropped_image[i][j] = image[i + crop_left][j+crop_up]
       
    #     return cropped_image

from Tkinter import *

class Space(object):

    def __init__(self, listOfPoints, color, canvas):
        # A Space takes in a 1D list of tuples
        # (row, col) which represent the location
        # of every pixel in that Space.
        self.listOfPoints = listOfPoints

        # Give all methods access to the outside canvas
        self.canvas = canvas
        self.color = color

        # When selected, a Space is open and displayed
        # When not selected, a Space is minimized and 
        # stored in the dock at the bottom of the screen
        self.selected = True

        self.calculateCenter()
        self.drawPixels()

    def calculateCenter(self):
        maxX = max( [coord[1] for coord in self.listOfPoints])
        minX = min( [coord[1] for coord in self.listOfPoints])
        self.centerX = ( maxX + minX ) / 2

        # NOTE: coord[0] corresponds to y since tuples are (row, col)

        maxY = max( [coord[0] for coord in self.listOfPoints])
        minY = min( [coord[0] for coord in self.listOfPoints])
        self.centerY = ( maxY + minY ) / 2


    def drawPixels(self):
        self.listOfDrawnPixels = []
        for i in xrange(len(self.listOfPoints)):
            try:
                y, x = self.listOfPoints[i][0], self.listOfPoints[i][1]
                y -= 300
                x = 1919 - x
                x -= 300
                self.listOfPoints[i] = [y, x]
                self.listOfDrawnPixels += [self.canvas.create_rectangle(x, y, x, y, 
                                           fill = self.color, outline = self.color)] # Draw a pixel and get a handle on it
            except:
                continue

    def distanceFromCenter(self, x, y):
        return ( (x - self.centerX)**2 + (y - self.centerY)**2 ) ** .5


    # UpdatePixels adds all current board drawings to the Space
    def updatePixels(self, listOfNewPoints):
        self.listOfPoints = set(self.listOfPoints)
        self.listOfPoints.update(listOfNewPoints)
        self.listOfPoints = list(self.listOfPoints)
        self.destroyPixels()
        self.drawPixels()
        self.calculateCenter()

    # Updates position of a Space to an exact location
    def updatePosition(self, x, y):
        dx = x - self.centerX
        dy = y - self.centerY

        self.centerX = x
        self.centerY = y

        for i in xrange(len(self.listOfPoints)):
            y, x = self.listOfPoints[i][0], self.listOfPoints[i][1]
            y += dy
            x += dx
            self.listOfPoints[i] = (y, x)
        for i in xrange(len(self.listOfDrawnPixels)):
            y, x = self.listOfPoints[i][0], self.listOfPoints[i][1]
            self.canvas.coords(self.listOfDrawnPixels[i], x, y, x, y)


    # UpdatePositionbyD is given a shift for the space, and
    # applies that shift to the location of all
    # the points in the space, and the space itself.
    def updatePositionByD(self, dx, dy):
        self.centerX += dx
        self.centerY += dy

        for i in xrange(len(self.listOfPoints)):
            y, x = self.listOfPoints[i][0], self.listOfPoints[i][1]
            y += dy
            x += dx
            self.listOfPoints[i] = (y, x)
        for i in xrange(len(self.listOfDrawnPixels)):
            try:
                y, x = self.listOfPoints[i][0], self.listOfPoints[i][1]
                self.canvas.coords(self.listOfDrawnPixels[i], x, y, x, y)
                # Update the canvas position of each pixel
                # Pixels and their positions correspond to each other via their list indexes
            except: continue

    def select(self):
        if self.selected: return
        self.selected = True
        self.drawPixels()


    def deselect(self):
        if not self.selected: return
        self.selected = False
        self.destroyPixels()


    def destroyPixels(self):
        for pixel in self.listOfDrawnPixels:
            self.canvas.delete(pixel)

        self.listOfDrawnPixels = []

# def testSpaces():
#     root = Tk()
#     canvas = Canvas(root, width = 500, height = 500)
#     canvas.pack()
#     listOfData = [(0,0),(1919,1079)]
#     s1 = Space(listOfData, "blue", canvas)
#     listOfData2 = [(50,50),(51,51),(52,52)]
#     s2 = Space(listOfData2, "red", canvas)
#     s1.deselect()
#     s1.select()
#     s1.deselect()
#     s1.select()
#     newData = [(63,62),(64,64)]

#     print s2.distanceFromCenter(500,500)
#     s2.updatePixels(newData)
#     s3 = Space(newData, "cyan", canvas)

#     print s2.distanceFromCenter(500,500)
#     s2.updatePositionByD(50,50)
#     print s2.distanceFromCenter(500,500)
#     root.mainloop()

# testSpaces()


interface = KinectInterface()
interface.run()
