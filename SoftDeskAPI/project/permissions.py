from rest_framework.permissions import BasePermission

from . import models
 
class IsAuthorOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        # Project a chercher pour savoir si contributeur
        if isinstance(obj, models.Issues):
            project = obj.project_id
        elif isinstance(obj, models.Comments):
            project = obj.issue_id.project_id
        else:
            project = obj
        
        # Vérifie si la méthode de requête est les suivante : GET, HEAD, OPTIONS POST
        if request.method in ['GET', 'HEAD', 'OPTIONS', 'POST']:
            # Regarde si contributeur
            return bool(request.user in project.contributors.all() and request.user.is_authenticated)
        
        # Vérifie si l'utilisateur connecté est l'auteur de l'objet
        return bool(obj.author_user_id == request.user and request.user.is_authenticated)
    
class IsAuthorOrReadOnlyForContributor(BasePermission):

    def has_object_permission(self, request, view, obj):
         # Project a chercher pour savoir si contributeur
        if isinstance(obj, models.Contributors):
            obj = obj.project
        
        # Vérifie si la méthode de requête est en lecture seule (GET, HEAD, OPTIONS)
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            # Regarde si contributeur
            return bool(request.user in obj.contributors.all() and request.user.is_authenticated)
        
        # Vérifie si l'utilisateur connecté est l'auteur de l'objet
        return bool(obj.author_user_id == request.user and request.user.is_authenticated)