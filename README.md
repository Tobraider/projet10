Cette application est un site fait grace a django

Cette API permet de creer des projets, des issues et des comments ainsi que les parcourir.
La documentation de l'API est trouvable ici : 

Lors de la creation de compte pour le mot de passe il faut suivre ces deux regles :
 - le mot de passe ne doit pas etre que des chiffres
 - le mot de passe doit faire au moins 8 caractères

Vous trouverez ici un bouton pour acceder a l'api et la doc sur postman :
[![Run in Postman](https://run.pstmn.io/button.svg)](https://app.getpostman.com/run-collection/27764954-ffc79fac-b005-4acf-a095-26dabcba075d?action=collection%2Ffork&source=rip_markdown&collection-url=entityId%3D27764954-ffc79fac-b005-4acf-a095-26dabcba075d%26entityType%3Dcollection%26workspaceId%3D71e4824e-29b7-455f-955c-af6c8c80e8e5)

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
