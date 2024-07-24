import cv2
import os
import numpy
from picamera2 import Picamera2

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
    retour=False
    compteur=0
    
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
                    retour=True
                    pasReconnu=False
                    
            #cv2.putText(frame,'not recognized',(x-10, y-10), cv2.FONT_HERSHEY_PLAIN,1,(0, 0, 255))
            # Show the image and check for ESC being pressed
        cv2.imshow('OpenCV', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    picam2.stop_recording()
    cv2.destroyAllWindows()
    return retour

ReconnaissanceFacial('jeanne')