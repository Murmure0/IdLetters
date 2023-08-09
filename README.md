Projet de fin de formation : LettersReader

BUT : 
Réalisation d'une application utilisant l'IA pour la traduction de papiers administratifs pour facilité l'intégration de personnes en difficulté.
Extraction, reconnaissance et traduction de texte.
Resultat : 
Une traduction écrite & orale dans la langue choisie : entièreté ou résumé du contenu

Extraction : TesseractORC; 
Reconnaissance : OpenCV, Pytesseract;
OU
Extraction & reconnaissance : OpenVino // PaddleOCR

Traduction : T5-small entrainé sur Opus_book (fr-pl/fr-it/fr-ru/fr-nl/fr-pt/fr-en)();
Résumé du texte : langChain;
Lecture : pyttsx3, additionnal language : eSpeak,RHVoice;

Réflexions en cours:
Selection & installation de la langue dans laquelle interagir
Prise de photo/scan du doc : check si l'image est au bon format (jpg/jpeg) & exploitable => voir resolution & qualitée du document, test d'identification
Ne pas stocker les données personnelles : adresses, nom, tel ... => detecter pour flouter / ne pas enregistrer
Viser l'objet, le contenu & l'organisme de contact
Proposition de conserver en local la version traduite


Sources :
How to OCR with Tesseract, OpenCV and Python : https://nanonets.com/blog/ocr-with-tesseract/
Installation : https://codetoprosper.com/extract-text-python-opencv-tesseract-ocr/

OpenVino : 
    https://github.com/openvinotoolkit/openvino_notebooks/blob/9cd22e1bfa951f98c72c0118e2ccf823024ca399/notebooks/405-paddle-ocr-webcam/405-paddle-ocr-webcam.ipynb

Traduction :
    https://huggingface.co/docs/transformers/tasks/translation

pyttsx3, additionnal language:
    http://espeak.sourceforge.net/download.html
    https://github.com/Olga-Yakovleva/RHVoice


langChain : 
    https://python.langchain.com/docs/use_cases/summarization


Pourquoi utiliser des modèles pr-xistents :
    - Peu de temps
    - Ce sera la pratique demandée en entreprise
    - les modèles pré-existants et pé-entrainer polluent moins 

