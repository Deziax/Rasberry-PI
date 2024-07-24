# Rasberry-PI
Voici un de mes projets réalisé lors de ma formation en BTS SIO.

Ce projet a été réalisé en autonomie. Celui-si a pour but l'authentification du personnels médical d'un laboratoire passant par 3 étapes : 
- Indentifiant / Mot de passe
- Scan de Badge
- Reconnaissance faciale

Chaque authentification est enregistrées dans une base de données SQLite dans une table LOG. Cette table répertorie les dates, identifiant, étape (en cas d'échec), ainsi qu'un message simple qui détermine le résultat de la procédure.

Le langage utilisé pour ce projet est Python. 

Le matériel utilisé est le suivant : 
- Raspberry
- Camera (PiCamera)
- RFID (Scanner de Badge)  
