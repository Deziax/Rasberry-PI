import tkinter as tk
from tkinter import messagebox
import sqlite3
import time
import requests
import urllib.request
import json
from time import sleep
import sys
import cv2
import os
import numpy
from picamera2 import Picamera2
from mfrc522 import SimpleMFRC522
reader = SimpleMFRC522()

def insert_donnees(donnees):

    try:
        
        connexion = sqlite3.connect("LogCoffre.db")
        curseur = connexion.cursor()

        curseur.executemany("INSERT INTO LOGV2 (num_phase, identifiant, num_badge, commentaire) VALUES (?, ?, ?, ?)", donnees)

        connexion.commit()

    except sqlite3.Error as erreur:
        messagebox.showerror("Erreur", "Erreur lors de l'insertion des données :", erreur)

    finally:
        if connexion:
            connexion.close()

def valider_identification():
    global identifiant2
    identifiant2 = identifiant2_entry.get()
    mdp = mdp_entry.get()
    url_json = None
    url = urllib.request.urlopen(f"https://btssio-carcouet.fr/ppe4/public/connect2/{identifiant2}/{mdp}/infirmiere").read().decode('utf-8')
    if 'status' in url:
        insert = [(1, identifiant2, "NULL", "mdp ou identifiant incorrect")]
        insert_donnees(insert)
        messagebox.showerror("Erreur", "Identifiant ou mot de passe incorrect")
    else:
        url_json = json.loads(url)
        insert = [(1, identifiant2, "NULL", "Connexion par mdp réussi")]
        insert_donnees(insert)
        messagebox.showinfo("Connexion réussi, Bonjour " + url_json["nom"])
        fenetre.destroy()
        fenetre_open()
        
        
def valider_badge():
    global identifiant2
    global id_badge
    try:
        print("Hold a tag near the reader")
        id_badge, text = reader.read()
        sleep(5)
    except KeyboardInterrupt:
        GPIO.cleanup()
    url_json = None
    url = urllib.request.urlopen(f"https://btssio-carcouet.fr/ppe4/public/badge/{identifiant2}/{id_badge}").read().decode('utf-8')
    if 'satus' in url:
        insert = [(2, identifiant2, id_badge, "badge incorrect")]
        insert_donnees(insert)
        messagebox.showerror("Erreur", "badge incorrect")
    else:
        url_json = json.loads(url)
        insert = [(2, identifiant2, id_badge, "badge correct")]
        insert_donnees(insert)
        messagebox.showinfo("Le badge correspond")
        fenetre.fenetre2.destroy()
        fenetre_open_face()

def valider_face:
    global id_badge
    global identifiant2
    ReconnaissanceFacial(identifiant2)
    global retour
    if retour == false:
        insert = [(3, identifiant2, id_badge, "Le visage n'a pas été reconnu")]
        insert_donnees(insert)
        messagebox.showerror("Erreur", "Visage non reconnu")
    else:
        insert = [(3, identifiant2, id_badge, "Le visage à bien été reconnu")]
        insert_donnees(insert)
        messagebox.showerror("Erreur", "Bienvenue, {identifiant2}")

def fenetre_quit():
    fenetre.destroy()
    fenetre.fenetre2.destroy()
    
def fenetre_open():
    fenetre2 = tk.Tk()
    fenetre2.title("scan de badge")

    submit_button3 = tk.Button(fenetre2, text="Scan", command=valider_badge)
    submit_button3.grid(row=2, column=0)

    submit_button4 = tk.Button(fenetre2, text="Cancel")
    submit_button4.grid(row=2, column=1)
    fenetre2.mainloop()

def fenetre_open_face:
    fenetre3 = tk.Tk()
    fenetre3.title("reconnaissance facial")
    
    submit_button5 = tk.Button(fenetre3, text="commencer la reco facial", command=valider_face)
    submit_button5.grid(row=2, column=0)
    
    submit_button6 = tk.Button(fenetre3, text="Cancel")
    submit_button6.grid(row=2, column=1)
    fenetre3.mainloop()
    
def ReconnaissanceFacial(name):
    size = 4
    fn_haar = 'haarcascade_frontalface_default.xml'
    fn_dir = 'Photos'
    haar_cascade = cv2.CascadeClassifier(fn_haar)
    model = cv2.face.LBPHFaceRecognizer_create()
    model.read("model.yml")
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
    picam2.start()
    pasReconnu=True
    global retour
    retour=False
    compteur=0
    t1 = datetime.now()
    reco = 0
    
    id = 0
    names = {}
    for (subdirs, dirs, files) in os.walk(fn_dir):
        for subdir in dirs:
            names[id] = subdir
            id +=1
            
    
    while pasReconnu:
        (im_width, im_height) = (112, 92)
        
        frame = picam2.capture_array()

        # Flip the image (optional)
        #frame=cv2.flip(frame, 1,0)

        # Convert to grayscalel
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Resize to speed up detection (optinal, change size above)
        mini = cv2.resize(gray, (int(gray.shape[1] / size), int(gray.shape[0] / size)))

        # Detect faces and loop through each one
        faces = haar_cascade.detectMultiScale(mini)
        
        for i in range(len(faces)):
            face_i = faces[i]

            # Coordinates of face after scaling back by `size`
            (x, y, w, h) = [v * size for v in face_i]
            face = gray[y:y + h, x:x + w]
            face_resize = cv2.resize(face, (im_width, im_height))

            prediction = model.predict(face_resize)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
            
            # Try to recognize the face
            
            # [1]
            # Write the name of recognized face
            #cv2.putText(frame,'%s - %.0f' % (names[prediction[0]],prediction[1]),(x-10, y-10), cv2.FONT_HERSHEY_PLAIN,1,(0, 255, 0))
            if prediction[1]<85:
                cv2.putText(frame,'%s - %.0f' % (names[prediction[0]],prediction[1]),(x-10, y-10), cv2.FONT_HERSHEY_PLAIN,1,(0, 255, 0))
                #print(prediction[1])
                #print('%s - %.0f' % (names[prediction[0]],prediction[1]))
                if names[prediction[0]]==name:
                    reco += 1
                    if reco >= 5:
                        retour=True
                        pasReconnu=False
                else:
                    reco = 0
        t2 = datetime.now()
        delta = t2 - t1
        if(delta.total_seconds()>=30):
            retour = False
        
                    
            #cv2.putText(frame,'not recognized',(x-10, y-10), cv2.FONT_HERSHEY_PLAIN,1,(0, 0, 255))
            # Show the image and check for ESC being pressed
        cv2.imshow('OpenCV', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    picam2.stop_recording()
    cv2.destroyAllWindows()
    return retour



fenetre = tk.Tk()
fenetre.title("Formulaire Login")

tk.Label(fenetre, text="Identifiant :").grid(row=0, column=0)
identifiant2_entry = tk.Entry(fenetre)
identifiant2_entry.grid(row=0, column=1)

tk.Label(fenetre, text="Mot de Passe :").grid(row=1, column=0)
mdp_entry = tk.Entry(fenetre, show="*")
mdp_entry.grid(row=1, column=1)

submit_button = tk.Button(fenetre, text="Ok", command=valider_identification)
submit_button.grid(row=2, column=0)

submit_button2 = tk.Button(fenetre, text="Cancel", command=fenetre_quit)
submit_button2.grid(row=2, column=1)

fenetre.mainloop()