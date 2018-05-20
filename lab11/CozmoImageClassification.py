#!/usr/bin/env python

##############
#### Your name: Eric Swanson
##############

import sys
import collections

import cozmo

import cv2
import numpy as np
import re
from imgclassification import ImageClassifier
from sklearn import svm, metrics
import _pickle

class Tracker:

    def __init__(self, threshold):
        self.frames = collections.deque(maxlen=threshold)
        self.size = 0
        self.counts = self.resetMap()
        self.threshold = threshold
        self.frameCounter = 0
    
    def addPrediction(self, prediction):
        self.frameCounter += 1
        print("Frame: ",self.frameCounter)
        if len(self.frames) == self.frames.maxlen:
            last = self.frames.popleft()
            self.counts[last] -= 1
            self.size -= 1
        
        self.frames.append(prediction)
        self.counts[prediction] += 1
        
        maxPrediction = None
        valid = False
        maxCount = -1
        if len(self.frames) == self.frames.maxlen:
            for key, value in self.counts.items():
                if value > maxCount:
                    maxPrediction = key
                    maxCount = value
                    
        if maxPrediction is not None and maxPrediction != 'none' and (float(maxCount)/self.threshold) >= .7:
            valid = True
            self.resetTracker()
        print(valid, maxPrediction, maxCount)    
        return valid, maxPrediction
        
    def resetMap(self):
        return {'drone':0,'hands':0,'inspection':0,'none':0,'order':0,'place':0,'plane':0,'truck':0}
    
    def resetTracker(self):
        self.frames.clear()
        self.counts = self.resetMap()
        self.frameCounter = 0
        
        

def main(robot: cozmo.robot.Robot):

    img_clf = None
    with open('.\svc_image_classifier.pk1','rb') as fid:
        img_clf = _pickle.load(fid)
    #img_clf = ImageClassifier()
    #print("Loading the data...")
    # load images
    #(train_raw, train_labels) = img_clf.load_data_from_folder('./train/')

    #print("Data loaded.")
    # convert images into features
    #train_data = img_clf.extract_image_features(train_raw)
    
    # train model and test on training data
    #img_clf.train_classifier(train_data, train_labels)
    
    tracker = Tracker(10)
    
    #cozmo.robot.LiftPosition(cozmo.robot.MAX_LIFT_HEIGHT)
    robot.move_lift(3)
    robot.set_head_angle(cozmo.util.degrees(0)).wait_for_completed()

    try:

        while True:
            #get camera image
            event = robot.world.wait_for(cozmo.camera.EvtNewRawCameraImage, timeout=30)

            #convert camera image to opencv format
            #opencv_image = cv2.cvtColor(np.asarray(event.image), cv2.COLOR_RGB2GRAY)
            image = np.asarray(event.image)
            image = image[np.newaxis,...]
            print(image.shape)
            features = img_clf.extract_image_features(image)
            prediction = img_clf.predict_labels(features)
            print("prediction is: ",prediction)
            valid,value = tracker.addPrediction(prediction[0])
            
            if valid:
                if value == 'drone':
                    robot.say_text("I see a drone").wait_for_completed()
                    robot.play_anim_trigger(cozmo.anim.Triggers.CodeLabVictory).wait_for_completed()
                    # do an animation
                elif value == 'hands':
                    robot.say_text("I see hands").wait_for_completed()
                    robot.play_anim_trigger(cozmo.anim.Triggers.Hiccup).wait_for_completed()
                elif value == 'inspection':
                    robot.say_text("I see an inspection").wait_for_completed()
                    robot.play_anim_trigger(cozmo.anim.Triggers.FacePlantRoll).wait_for_completed()
                elif value == 'order':
                    robot.say_text("I see an order").wait_for_completed()
                    robot.play_anim_trigger(cozmo.anim.Triggers.LaserPounce).wait_for_completed()
                elif value == 'truck':
                    robot.say_text("I see a truck").wait_for_completed()
                    robot.play_anim_trigger(cozmo.anim.Triggers.PeekABooSurprised).wait_for_completed()
                
                robot.move_lift(3)
                robot.set_head_angle(cozmo.util.degrees(0)).wait_for_completed()

    except KeyboardInterrupt:
        print("")
        print("Exit requested by user")
    except cozmo.RobotBusy as e:
        print(e)
    


if __name__ == "__main__":
    cozmo.run_program(main, use_viewer = True, force_viewer_on_top = True)
