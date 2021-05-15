import numpy as np
import cv2
import pyautogui
from tensorflow.keras.models import load_model
import time

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.loaded_model = load_model('./my_eyes.h5', compile = False)
        self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
        self.list_heatmap = []

    def __del__(self):
        self.video.release()        

    def get_frame(self,capture_heatmap=False):

        loaded_model = self.loaded_model
        face_cascade = self.face_cascade
        eye_cascade = self.eye_cascade
        list_heatmap = self.list_heatmap

        #start_time = time.time()
        stop = 0
        while stop == 0:

            ret, img = self.video.read()

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            #faces = face_cascade.detectMultiScale(img, scaleFactor = 1.1, minNeighbors = 5)
            
            ex,ey,ew,eh=1,1,1,1
            
            for (ex,ey,ew,eh) in faces:
                cv2.rectangle(img,(ex,ey),(ex+ew,ey+eh),(255,0,0),5)
                #print(ex,ey,eh,ew)
                milieu_crop_y = ey+eh/2
                milieu_crop_x = ex+ew/2
                distance_visage = 223/((eh+ew)/2)*0.4
                distance_visage = str(distance_visage)+'00000'
                distance_visage = float(distance_visage[0:5])
            
            image = img[ey:ey+eh, ex:ex+ew]
            eyes_array = []
            eyes = eye_cascade.detectMultiScale(image, scaleFactor = 1.1, minNeighbors = 5)
            
            for (eex,eey,eew,eeh) in eyes:
                if eey < image.shape[0]/2:
                    cv2.rectangle(image,(eex,eey),(eex+eew,eey+eeh),(0,255,0),2) 
                    #print(eex,eey,eeh,eew)
                    eyes_array.append(eex)
                    eyes_array.append(eey)
                    eyes_array.append(eew)
                    eyes_array.append(eeh)
                    
            if len(eyes_array)== 8:        
                if eyes_array[0] > eyes_array[4]:  
                    #right-left
                    middle_left_x = ex+eyes_array[4]+eyes_array[6]/2
                    middle_left_y = ey+eyes_array[5]+eyes_array[7]/2
                    middle_right_x = ex+eyes_array[0]+eyes_array[2]/2
                    middle_right_y = ey+eyes_array[1]+eyes_array[3]/2
                    img_crop2 = image[eyes_array[1]:eyes_array[1]+eyes_array[3]+1, eyes_array[0]:eyes_array[0]+eyes_array[2]+1]
                    img_crop1 = image[eyes_array[5]:eyes_array[5]+eyes_array[7]+1, eyes_array[4]:eyes_array[4]+eyes_array[6]+1]
                else :
                    #left-right
                    middle_right_x = ex+eyes_array[4]+eyes_array[6]/2
                    middle_right_y = ey+eyes_array[5]+eyes_array[7]/2
                    middle_left_x = ex+eyes_array[0]+eyes_array[1]/2
                    middle_left_y = ey+eyes_array[2]+eyes_array[3]/2
                    img_crop1 = image[eyes_array[1]:eyes_array[1]+eyes_array[3]+1, eyes_array[0]:eyes_array[0]+eyes_array[2]+1]
                    img_crop2 = image[eyes_array[5]:eyes_array[5]+eyes_array[7]+1, eyes_array[4]:eyes_array[4]+eyes_array[6]+1]

                img_crop1 = img_crop1[2:img_crop1.shape[0]-2 , 2:img_crop1.shape[0]-2]
                img_crop2 = img_crop2[2:img_crop2.shape[0]-2 , 2:img_crop2.shape[0]-2]
                
                original_size_1 = img_crop1.shape[0]
                original_size_2 = img_crop2.shape[0]

                width = 32
                height = 32

                dim = (width, height) 
                img_crop1 = cv2.resize(img_crop1, dim, interpolation = cv2.INTER_AREA)
                img_crop2 = cv2.resize(img_crop2, dim, interpolation = cv2.INTER_AREA)
                
                img_crop1 = cv2.cvtColor(img_crop1, cv2.COLOR_BGR2GRAY)
                img_crop2 = cv2.cvtColor(img_crop2, cv2.COLOR_BGR2GRAY)
                
                img_2 = np.hstack((img_crop1, img_crop2))
                #cv2.imshow('Eyes_frame', img_2) 
                
                img_crop1 = img_crop1/255 
                img_crop1 = img_crop1.reshape(1,32,32)
                #img_crop1 = np.expand_dims(img_crop1, axis=-1)
                #img_crop1 = img_crop1.reshape(1,32,32)
                #print(img_crop1.shape)
                
                img_crop11 = np.empty(0)
                img_crop11 = np.append(img_crop11, milieu_crop_x/640)
                img_crop11 = np.append(img_crop11, milieu_crop_y/480)
                img_crop11 = np.append(img_crop11, distance_visage)
                img_crop11 = np.append(img_crop11, middle_left_x/640)
                img_crop11 = np.append(img_crop11, middle_left_y/480)
                img_crop11 = np.append(img_crop11, original_size_1)
                img_crop11 = np.append(img_crop11, 0.5)
                img_crop11 = img_crop11.reshape(1, -1)
                #print(img_crop11.shape)
                pred1 = loaded_model.predict_on_batch([img_crop1,img_crop11])
                #print(pred1)
                #nb1 = int(pred1[0 :pred1.find('-')])
                #nb2 = int(pred1[pred1.find('-')+1: len(pred1)])
                
                #img_crop2 = img_crop2.flatten()
                img_crop2 = img_crop2/255
                img_crop2 = img_crop2.reshape(1,32,32)
                
                img_crop22 = np.empty(0)
                img_crop22 = np.append(img_crop22, milieu_crop_x/640)
                img_crop22 = np.append(img_crop22, milieu_crop_y/480)
                img_crop22 = np.append(img_crop22, distance_visage)
                img_crop22 = np.append(img_crop22, middle_right_x/640)
                img_crop22 = np.append(img_crop22, middle_right_y/480)
                img_crop22 = np.append(img_crop22, original_size_2)
                img_crop22 = np.append(img_crop22, 0)
                img_crop22 = img_crop22.reshape(1, -1)
                #print(img_crop1.shape)
                pred2 = loaded_model.predict([img_crop2,img_crop22])
                #print(pred2)
                #nb12 = int(pred2[0 :pred2.find('-')])
                #nb22 = int(pred2[pred1.find('-')+1: len(pred2)])
                
                x_final = ((pred1[0][0] + pred2[0][0])/2)*1920
                y_final = ((pred1[0][1]+ pred2[0][1])/2)*1080
                
                print(x_final,y_final)
                list_heatmap.append([x_final,y_final])
                
                pyautogui.moveTo(x_final, y_final)  

                ret, jpeg = cv2.imencode('.jpg', img_2)
                return jpeg.tobytes(), list_heatmap

        #end_time = time.time()
        print(list_heatmap)
        #print("durée :"+str(end_time-start_time))