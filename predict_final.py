from PIL import Image, ImageTk
import tkinter as tk
import cv2
import os
import numpy as np
from keras.models import model_from_json
import operator
import time
import sys, os
import matplotlib.pyplot as plt
from string import ascii_uppercase
from gtts import gTTS
import playsound
import pygame


class sign_to_speech:
    def __init__(self):
        self.directory = ''
        self.vs = cv2.VideoCapture(0)
        self.current_image = None
        self.current_image2 = None
        
        self.saved_model = open(self.directory+"model-bw.json", "r")
        self.tmp_model = self.saved_model.read()
        self.saved_model.close()
        self.final_model = model_from_json(self.tmp_model)
        self.final_model.load_weights(self.directory+"model-bw.h5")

        self.ct = {}
        self.ct['blank'] = 0
        self.is_blank = 0
        for i in ascii_uppercase:
            self.ct[i] = 0
        print("Loaded model from disk")
        self.root = tk.Tk()
        self.root.title("Sign language to Speech Converter")
        self.root.protocol('WM_DELETE_WINDOW', self.destructor)
        self.root.geometry("800x800")
        self.panel = tk.Label(self.root)
        self.panel.place(x = 10, y = 10, width = 1500, height = 740)
        self.panel.config(bg="lightblue")
        self.panel2 = tk.Label(self.root) # initialize image panels
        self.panel2.place(x = 200, y = 100, width = 510, height = 510)
        self.panel2.config(bg="lightblue")
        
        self.T = tk.Label(self.root)
        self.T.place(x=31,y = 17)
        self.T.config(text = "Sign Language to Speech",font=("Georgia",20,"bold"))
        self.panel3 = tk.Label(self.root) # Current Symbol
        self.panel3.place(x = 880,y=400)
        self.panel3.config(bg="lightblue")
        self.T1 = tk.Label(self.root)
        self.T1.place(x = 700,y = 400)
        self.T1.config(text="Character :",font=("Georgia",20,"bold"))
        self.panel4 = tk.Label(self.root) # Word
        self.panel4.place(x = 800,y=460)
        self.panel4.config(bg="lightblue")
        self.T2 = tk.Label(self.root)
        self.T2.place(x = 700,y = 460)
        self.T2.config(text ="Word :",font=("Georgia",20,"bold"))
        self.panel5 = tk.Label(self.root) # Sentence
        self.panel5.place(x = 880,y=510)
        self.panel5.config(bg="lightblue")
        self.T3 = tk.Label(self.root)
        self.T3.place(x = 700,y = 510)
        self.T3.config(text ="Sentence :",font=("Georgia",20,"bold"))

        self.str=""
        self.word=""
        self.current_symbol="Empty"
        self.photo="Empty"
        self.video_loop()

    def video_loop(self):
        flag, frame = self.vs.read()
        if flag:
            cv2image = cv2.flip(frame, 1)
            x1 = int(0.5*frame.shape[1])
            y1 = 10
            x2 = frame.shape[1]-10
            y2 = int(0.5*frame.shape[1])
            cv2.rectangle(frame, (x1-1, y1-1), (x2+1, y2+1), (255,0,0) ,1)
            cv2image = cv2.cvtColor(cv2image, cv2.COLOR_BGR2RGBA)
        
            cv2image = cv2image[y1:y2, x1:x2] # crop
            gray = cv2.cvtColor(cv2image, cv2.COLOR_BGR2GRAY) # grayscaling 
            blur = cv2.GaussianBlur(gray,(5,5),2) # Gaussian blure 
            th3 = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,11,2)
            ret, res = cv2.threshold(th3, 70, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU) # Thresholding
            
            self.predict(res)
            self.current_image2 = Image.fromarray(res)
            imgtk = ImageTk.PhotoImage(image=self.current_image2)
            self.panel2.imgtk = imgtk
            self.panel2.config(image=imgtk)
            self.panel3.config(text=self.current_symbol,font=("Georgia",20))
            self.panel4.config(text=self.word,font=("Georgia",20))
            self.panel5.config(text=self.str,font=("Georgia",20))
                          
        self.root.after(30, self.video_loop)
    def predict(self,test_image):
        test_image = cv2.resize(test_image, (128,128)) # resize 
        test_image = test_image/255.0  # feature scaling 
        result = self.final_model.predict(test_image.reshape(1, 128, 128, 1)) 
        
        prediction={}
        prediction['blank'] = result[0][0]
        inde = 1
        for i in ascii_uppercase:
            prediction[i] = result[0][inde]
            inde += 1
        #LAYER 1
        prediction = sorted(prediction.items(), key=operator.itemgetter(1), reverse=True)
        self.current_symbol = prediction[0][0]
        
        if(self.current_symbol == 'blank'):
            for i in ascii_uppercase:
                self.ct[i] = 0
        self.ct[self.current_symbol] += 1
        if(self.ct[self.current_symbol] > 60):
            for i in ascii_uppercase:
                if i == self.current_symbol:
                    continue
                tmp = self.ct[self.current_symbol] - self.ct[i]
                if tmp < 0:
                    tmp *= -1
                if tmp <= 20:
                    self.ct['blank'] = 0
                    for i in ascii_uppercase:
                        self.ct[i] = 0
                    return
            self.ct['blank'] = 0
            for i in ascii_uppercase:
                self.ct[i] = 0
            if self.current_symbol == 'blank':
                if self.is_blank == 0:
                    self.is_blank = 1
                    if len(self.str) > 0:
                        self.str += " "
                    self.str += self.word
                    # self.speech(self.word)
                    self.word = ""
            else:
                if(len(self.str) > 16):    #can increase the length of sentence from here 
                    self.str = ""
                self.is_blank = 0
                self.word += self.current_symbol
    
    def destructor(self):
        if(len(self.str)>0): self.speech(self.str)
        elif(len(self.word)>0): self.speech(self.word)
        
        print("Thank You ....")
        self.root.destroy()
        self.vs.release()
        cv2.destroyAllWindows()
    
    def destructor1(self):
        self.speech(self.str)
        print("Closing ...")
        self.root1.destroy()

    def speech(self,text):
        tts = gTTS(text)
        print(text)
        tts.save("output.mp3")
        # playsound.playsound("output.mp3")
        # Initialize the pygame mixer
        pygame.mixer.init()

        # Load and play the audio
        pygame.mixer.music.load("output.mp3")
        pygame.mixer.music.play()

        # Keep the script running while the audio plays
        while pygame.mixer.music.get_busy():
            pass
        # pygame.time.wait(2000)
        # os.remove("output.mp3")

print("Welcome to sign to speech convertor ....")
pba = sign_to_speech()
pba.root.mainloop()
