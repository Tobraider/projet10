Cette application est un site fait grace a django

Cette API permet de creer des projets, des issues et des comments ainsi que les parcourir.
La documentation de l'API est trouvable ici : 

Lors de la creation de compte pour le mot de passe il faut suivre ces deux regles :
 - le mot de passe ne doit pas etre que des chiffres
 - le mot de passe doit faire au moins 8 caractères

Vous trouverez ici un bouton pour acceder à la documentation :
https://documenter.getpostman.com/view/27764954/2s93zCZLSB

Pour mettre en place cette application il faut faire les etapes suivantes:

Dans un terminal
1. Allez dans le dossier de l'application

    `cd SoftDeskAPI`

2. Executez les commandes suivants

    Windows:

        python -m venv env

        .\env\Scripts\activate

        pip install -r ../requirements.txt

        python manage.py runserver

    
    Linux:

        python3 -m venv env

        source env/bin/activate

        pip install -r ../requirements.txt

        python manage.py runserver
