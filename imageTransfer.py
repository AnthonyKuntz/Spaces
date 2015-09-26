#imageTransfer.py
import json
from asyncHttp import asyncHttp

# An instance of this class contains a reference to the images array (passed in to __init__)
# __init__ must also be passed a string containing the address of the server (e.g. this.that.something:3000)
# 
# To use the class's functionality, periodically call updateImages()*. This function will both upload images
# to the server and download new ones. Do not directly interact with the class apart from calling this method.
# Also, DO NOT re-arrange the order of the images as this may cause duplication of images or prevent new images
# from being transferred.
#
# *You may call this function as often as you like, though if another instance of it hasn't finished executing,
# the newly called instance will do nothing (no harm done, no positive effect either).
# 
# Once an image has been uploaded to the server, changes to that element of the images arrary will not be transferred.
# Because updateImages() starts a thread, calls after it should not assume that updateImages has finished.
#
# Pass an argument onNew() to updateImages and it will run onNew on each newly arrived image

class imageTransfer:

    def __init__(this, su, images, user):
        this.user = user
        this.flag = False
        this.serverUrl = ""
        this.ids = []
        this.serverUrl = su
        this.images = images
    
    #use this function for debugging only:
    def getIds(this):
        return this.ids

    #Call only from updateImages()
    def checkForImages(this, onNew, diff):
        if(not this.flag):
            print "Called incorrectly"
            return

        def callback(response):
            #print response.body
            if(type(response.body) is list):
                #print "check for new:", response.body
                this.ids += response.body[0]
                this.images += response.body[1]

                for x in xrange(len(this.images) - len(response.body[1]), len(this.images)):
                    temp = this.images[x]
                    this.images[x] = this.images[x - diff]
                    this.images[x - diff] = temp
                    print type(this.images[x - diff])
                    onNew(this.images[x - diff])
            else:
                #print "Error (1)"
                pass
            this.flag = False

        asyncHttp.get(this.serverUrl + "/imagesGet", {"images": this.ids}, callback)

    #This function is the "meat"
    def updateImages(this, onNew):
        if(this.flag):
            return
        this.flag = True

        diff = len(this.images) - len(this.ids)
        if(diff == 0):
            #print "images", this.images, "ids", this.ids
            this.checkForImages(onNew, diff)
            return

        def callback(response):
            if(type(response.body) is list):
                this.ids += response.body
                print "successful upload, this.ids:", this.ids
                this.checkForImages(onNew, diff)
            else:
                print "failed upload"
                this.flag = False
        # submit = []
        # for x in xrange(len(this.images) - diff, len(this.images)):
        #     submit += [json.dumps(this.images[x])]

        #asyncHttp.get(this.serverUrl + "/imagesPost", {"images": [[[1080 / 2 - 108, 1920 / 2 - 384], [1080 / 2 - 108 - 1, 1920 / 2 - 384], [1080 / 2 - 108 - 1, 1920 / 2 - 384 - 1], [1080 / 2 - 108, 1920 / 2 - 384 - 1]]]}, callback)
        #asyncHttp.get(this.serverUrl + "/imagesPost", {"images": this.images[len(this.images) - diff:len(this.images)]}, callback)
        this.sendImage(this.images[len(this.images) - diff], "start", callback) #send newest -- Problems!!! swap newcomer based on diff

    chunkSize = 64
    def sendImage(this, image, flag, final):
        if(flag == "end"):
            asyncHttp.get(this.serverUrl + "/imagesPost", {"user": this.user, "data": "end"}, final)
        elif(flag == "start"): #We're at the start
            asyncHttp.get(this.serverUrl + "/imagesPost", {"user": this.user, "data": "start"}, lambda x: this.sendImage(image, 0, final))
        else: #data transmission
            if(len(image) <= flag):
                this.sendImage(image, "end", final)
            else:
                asyncHttp.get(this.serverUrl + "/imagesPost", {"user": this.user, "data": image[flag:min(flag + this.chunkSize, len(image))]}, 
                    lambda x: this.sendImage(image, flag + this.chunkSize, final))
