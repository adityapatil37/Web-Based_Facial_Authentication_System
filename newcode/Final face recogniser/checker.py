import cv2 as cv
import os
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from mtcnn.mtcnn import MTCNN


def face_scanner(path):
    img = cv.imread(path)

    img = cv.cvtColor(img, cv.COLOR_BGR2RGB) 

    detector = MTCNN()
    results = detector.detect_faces(img)
    results
    x,y,w,h = results[0]['box']

    img = cv.rectangle(img, (x,y), (x+w, y+h), (0,0,255), 0)

    my_face = img[y:y+h, x:x+w]
    #Facenet takes as input 160x160 
    my_face = cv.resize(my_face, (160,160))
    cv.imwrite(f"{path}",my_face)
    return path

