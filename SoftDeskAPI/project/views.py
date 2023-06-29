from django.shortcuts import render
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth.hashers import make_password
from django.db.models import Q

from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from . import models
from . import serializers
from . import permissions


class UserViewset(APIView):

    def post(self, request):
        """ Cette fonction permet de gerer la requete POST et de creer un compte utilisateur
            les parametre dans le body doivent etre : email, first_name, last_name et password """
        newUser = models.User()
        newUser.email = request.POST.get("email")
        newUser.first_name = request.POST.get("first_name")
        newUser.last_name = request.POST.get("last_name")
        newUser.password = make_password(request.POST.get("password"))
        print(newUser)
        # Verifie si tout les champs sont OK
        try:
            newUser.full_clean()
        except ValidationError as e:
            print(e)
            return Response({'error': 'dans les informations du body'}, status=status.HTTP_400_BAD_REQUEST)
        # Sauvegarde
        try:
            newUser.save()
        except IntegrityError:
            return Response({'error': 'username deja utilisé'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Utilisateur créé avec succès'}, status=status.HTTP_201_CREATED)


class ProjectListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """ Cette fonction permet de gerer la requete GET 
            et renvoie la liste de tout les projets ou le user est contributeur """
        projects = models.Projects.objects.filter(Q(author_user_id=request.user) | Q(contributors=request.user))
        serializer = serializers.ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    def post(self, request):
        """ Cette fonction permet de gerer la requete POST et permet de creer un projet.
            Il faut en body : title, description(optionnel) et type"""
        newProject = models.Projects()
        newProject.title = request.POST.get("title")
        newProject.description = request.POST.get("description")
        newProject.author_user_id = request.user
        newProject.type = choix_list(newProject.type_choice, request.data.get("type"))
        # Verifie si tout les champs sont OK
        try:
            newProject.full_clean()
        except ValidationError:
            return Response({'error': 'dans les informations du body'}, status=status.HTTP_400_BAD_REQUEST)
        # Sauvegarde
        try:
            newProject.save()
        except IntegrityError:
            return Response({'error': 'impossible de creer le project'}, status=status.HTTP_400_BAD_REQUEST)
        # ajout de l'auteur dans les contributor
        newProject.contributors.add(request.user, through_defaults={"role":models.Contributors.AUTHOR})
        # serialize le projet afin de le renvoier en reponse
        serializer = serializers.ProjectDetailSerializer(newProject)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProjectDetailView(APIView):
    
    permission_classes = [permissions.IsAuthorOrReadOnly]

    def get(self, request, id):
        """ Cette fonction permet de gerer la requete GET et renvoie la liste de tout les champs du projet """
        try:
            projects = models.Projects.objects.get(pk=id)
        except models.Projects.DoesNotExist:
            return Response({"message": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
        # Verifie si le user est contributeur du projet
        self.check_object_permissions(request, projects)
        serializer = serializers.ProjectDetailSerializer(projects)
        return Response(serializer.data)

    def put(self, request, id):
        """ Cette fonction permet de gerer la requete PUT et modifie le projet.
            Meme parametre que pour le POST de ProjectListView """
        try:
            projects = models.Projects.objects.get(pk=id)
        except models.Projects.DoesNotExist:
            return Response({"message": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
        # Verifie que le user est bien l'auteur du projet
        self.check_object_permissions(request, projects)
        if request.data.get("title"):
            projects.title = request.data.get("title")
        if request.data.get("description"):
            projects.description = request.data.get("description")
        if request.data.get("type"):
            projects.type = choix_list(projects.type_choice, request.data.get("type"), default=projects.type)
        try:
            projects.full_clean()
        except ValidationError:
            return Response({'error': 'dans les informations du body'}, status=status.HTTP_400_BAD_REQUEST)
        projects.save()
        serializer = serializers.ProjectDetailSerializer(projects)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, id):
        """ Cette fonction gere la requete DELETE. Uniquement si le user est l'auteur du projet"""
        try:
            projects = models.Projects.objects.get(pk=id)
        except models.Projects.DoesNotExist:
            return Response({"message": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
        # Verifie si le user est bien l'auteur du projet
        self.check_object_permissions(request, projects)
        projects.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class ContributorsListView(APIView):

    permission_classes = [permissions.IsAuthorOrReadOnlyForContributor]

    def get(self, request, id):
        """ Cette fonction gere la requete GET et retourne tout les contributeurs d'un projet """
        try:
            # Regarde l'id de projet dans contributeur
            contributors = models.Contributors.objects.filter(project__id=id)
        except models.Contributors.DoesNotExist:
            return Response({"message": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
        if contributors.exists():
            # Verifie si le user est bien contributeur du projet
            self.check_object_permissions(request, contributors[0])
            serializer = serializers.ContributorsSerializer(contributors, many=True)
            return Response(serializer.data)
        else:
            return Response({"message": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

    
    def post(self, request, id):
        """ Cette fonction gere la requete POST et ajoute un ou des contributeurs """
        try:
            project = models.Projects.objects.get(pk=id)
        except models.Projects.DoesNotExist:
            return Response({"message": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
        # Regarde si le user est auteur du projet
        self.check_object_permissions(request, project)
        userError = []
        if request.data.get('createur'):
            userlist = models.User.objects.filter(email__in=request.data.getlist('createur'))
            for user in userlist:
                # Erreur possible car peut pas avoir 2 fois le meme contributeur
                try:
                    project.contributors.add(user, through_defaults={"role":models.Contributors.CREATOR})
                except IntegrityError:
                    userError.add(user)
        if request.data.get('responsable'):
            userlist = models.User.objects.filter(email__in=request.data.getlist('createur'))
            for user in userlist:
                # Erreur possible car peut pas avoir 2 fois le meme contributeur
                try:
                    project.contributors.add(user, through_defaults={"role":models.Contributors.RESPONSABLE})
                except IntegrityError:
                    userError.add(user)
        if request.data.get('autres'):
            userlist = models.User.objects.filter(email__in=request.data.getlist('createur'))
            for user in userlist:
                # Erreur possible car peut pas avoir 2 fois le meme contributeur
                try:
                    project.contributors.add(user, through_defaults={"role":models.Contributors.AUTRE})
                except IntegrityError:
                    userError.add(user)
        serializerProjets = serializers.ProjectDetailSerializer(project)
        serializerList = serializers.ListeErrorSerializer(userError, many=True)
        result = {
            "projet" : serializerProjets.data,
            "erreur" : serializerList.data
        }
        return Response(result, status=status.HTTP_200_OK)


class DeleteContributorView(APIView):

    permission_classes = [permissions.IsAuthorOrReadOnlyForContributor]

    def delete(self, request, id, id_user):
        """ Cette fonction gere la requete DELETE et supprime un contributeur """
        try:
            # regarde l'id du projet et l'id du user
            contributor = models.Contributors.objects.get(project__id=id, user__id=id_user)
        except models.Contributors.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        # check si user est auteur
        self.check_object_permissions(request, contributor)
        # Attention on peut pas supprimer l'auteur
        if contributor.role != models.Contributors.AUTHOR:
            contributor.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error': "impossible de supprimer l'auteur"}, status=status.HTTP_400_BAD_REQUEST)
        

class IssuesListView(APIView):

    permission_classes = [permissions.IsAuthorOrReadOnly]

    def get(self, request, id):
        """ Cette fonction gere la requete GET et retourne la liste des issues """
        # Regarde l'id de project id
        issues = models.Issues.objects.filter(project_id__id=id)
        # si non vide
        if issues.exists():
            self.check_object_permissions(request, issues[0])
            serializer = serializers.IssuesSerializer(issues, many=True)
            return Response(serializer.data)
        else:
            return Response({"message": "Project not found or hasn't issue"}, status=status.HTTP_404_NOT_FOUND)
        
    def post(self, request, id):
        """ Cette fonction gere la requete POST et creer une issue 
            Body de la requete : title, description, tag, priority, status, assignee_user """
        # Regarde si le projet existe
        try:
            project = models.Projects.objects.get(pk=id)
        except models.Projects.DoesNotExist:
            return Response({"message": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
        # regarde si contributeur
        self.check_object_permissions(request, project)
        newIssues = models.Issues()
        newIssues.title = request.POST.get("title")
        newIssues.desc = request.POST.get("description")
        newIssues.author_user_id = request.user
        newIssues.tag = choix_list(models.Issues.tag_choice, request.POST.get("tag"))
        newIssues.priority = choix_list(models.Issues.priority_choice, request.POST.get("priority"))
        newIssues.status = choix_list(models.Issues.status_choice, request.POST.get("status"))
        newIssues.project_id = project
        if request.POST.get("assignee_user"):
            # Regarde si user existe
            try: 
                user_assigne = models.User.objects.get(email=request.POST.get("assignee_user"))
            except models.User.DoesNotExist:
                return Response({'error': "impossible de trouver l'utilisateur à assigner"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Regarde si c'est un contributeur sinon ne pourra jamais voir l'issue
                try:
                    cbon = models.Contributors.objects.get(project__id=id, user__id=user_assigne.pk)
                except models.Contributors.DoesNotExist:
                    return Response({'error': "user assignee pas dans les contributeurs"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    newIssues.assignee_user_id = user_assigne
        # Valide le model
        try:
            newIssues.full_clean()
        except ValidationError as e:
            print(e)
            return Response({'error': 'dans les informations du body'}, status=status.HTTP_400_BAD_REQUEST)
        # Sauvegarde
        try:
            newIssues.save()
        except IntegrityError:
            return Response({'error': "impossible de creer l'issue"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = serializers.IssuesSerializer(newIssues)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class IssuesDetailView(APIView):

    permission_classes = [permissions.IsAuthorOrReadOnly]

    def put(self, request, id, id_issue):
        """ Cette fonction gere la requete PUT et modifie l'issue 
            Body de la requete : title, description, tag, priority, status, assignee_user """
        # Regarde si projet a bien uneb issue avec cet id
        try:
            # check id de project_id et le pk
            issue = models.Issues.objects.get(project_id__id = id, pk=id_issue)
        except models.Issues.DoesNotExist:
            return Response({"message": "Issue not found"}, status=status.HTTP_404_NOT_FOUND)
        # Regarde si auteur de l'issue
        self.check_object_permissions(request, issue)
        if request.POST.get("title"):
            issue.title = request.POST.get("title")
        if request.POST.get("description"):
            issue.desc = request.POST.get("description")
        if request.POST.get("tag"):
            issue.tag = choix_list(models.Issues.tag_choice, request.POST.get("tag"), default=issue.tag)
        if request.POST.get("priority"):
            issue.priority = choix_list(models.Issues.priority_choice, request.POST.get("priority"), default=issue.priority)
        if request.POST.get("status"):
            issue.status = choix_list(models.Issues.status_choice, request.POST.get("status"), default=issue.status)
        if request.POST.get("assignee_user"):
            # regarde si user existe
            try: 
                user_assigne = models.User.objects.get(email=request.POST.get("assignee_user"))
            except models.User.DoesNotExist:
                # Si no alors valeur par defaut
                if request.POST.get("assignee_user") == "no":
                    issue.assignee_user_id = issue.author_user_id
            else:
                # Regarde si contributeur sinon ne peut avoir acces a cette information
                try:
                    cbon = models.Contributors.objects.get(project__id=id, user__id=user_assigne.pk)
                except models.Contributors.DoesNotExist:
                    return Response({'error': "user assignee pas dans les contributeurs"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    issue.assignee_user_id = user_assigne
        # Regarde model est OK
        try:
            issue.full_clean()
        except ValidationError as e:
            print(e)
            return Response({'error': 'dans les informations du body'}, status=status.HTTP_400_BAD_REQUEST)
        # Sauvegarde
        try:
            issue.save()
        except IntegrityError:
            return Response({'error': "impossible de creer l'issue"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = serializers.IssuesSerializer(issue)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, id, id_issue):
        """ Cette fonction gere la requete PUT et supprime une issue """
        # Regarde si projet a bien uneb issue avec cet id
        try:
            issue = models.Issues.objects.get(project_id__id = id, pk=id_issue)
        except models.Issues.DoesNotExist:
            return Response({"message": "Issues not found"}, status=status.HTTP_404_NOT_FOUND)
        # Regarde si auteur de l'issue
        self.check_object_permissions(request, issue)
        issue.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentsListView(APIView):

    permission_classes = [permissions.IsAuthorOrReadOnly]

    def get(self, request, id, id_issue):
        """ Cette fonction gere la requete GET et retourne tout les comments d'une issue"""
        # Regarde si l'id de project_id de issue_id est ok plus l'id de issue_id
        comments = models.Comments.objects.filter(issue_id__project_id__id=id, issue_id__id=id_issue)
        # Si non vide
        if comments.exists():
            self.check_object_permissions(request, comments[0])
            serializer = serializers.CommentsSerializer(comments, many=True)
            return Response(serializer.data)
        else:
            return Response({"message": "Issue not found or hasn't comment"}, status=status.HTTP_404_NOT_FOUND)
        
    def post(self, request, id, id_issue):
        """ Cette fonction gere la requete POST et creer un comment
            Body de la requete : description """
        # Regarde si l'issue existe
        try:
            # regarde id de project_id et le pk
            issue = models.Issues.objects.get(project_id__id = id, pk=id_issue)
        except models.Issues.DoesNotExist:
            return Response({"message": "Issue not found"}, status=status.HTTP_404_NOT_FOUND)
        # Regarde si contributeur du projet
        self.check_object_permissions(request, issue)
        newComment = models.Comments()
        newComment.description = request.POST.get("description")
        newComment.author_user_id = request.user
        newComment.issue_id = issue
        # Check model
        try:
            newComment.full_clean()
        except ValidationError as e:
            print(e)
            return Response({'error': 'dans les informations du body'}, status=status.HTTP_400_BAD_REQUEST)
        # Sauvegarde
        try:
            newComment.save()
        except IntegrityError:
            return Response({'error': "impossible de creer le comment"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = serializers.CommentsSerializer(newComment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class CommentsDetailView(APIView):

    permission_classes = [permissions.IsAuthorOrReadOnly]

    def get(self, request, id, id_issue, id_comment):
        """ Cette fonction gere la requete GET et retourne toutes les information d'un comment """
        # check si existe
        try:
            # Regarde si l'id de project_id de issue_id est ok plus l'id de issue_id et pk
            comment = models.Comments.objects.get(issue_id__project_id__id=id, issue_id__id=id_issue, pk=id_comment)
        except models.Comments.DoesNotExist:
            return Response({"message": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)
        # Regarde si contributeur
        self.check_object_permissions(request, comment)
        serializer = serializers.CommentsSerializer(comment)
        return Response(serializer.data)
    

    def put(self, request, id, id_issue, id_comment):
        """ Cette fonction gere la requete PUT et modifie le comment """
        # check si existe
        try:
            # Regarde si l'id de project_id de issue_id est ok plus l'id de issue_id et pk
            comment = models.Comments.objects.get(issue_id__project_id__id=id, issue_id__id=id_issue, pk=id_comment)
        except models.Comments.DoesNotExist:
            return Response({"message": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)
        # Regarde si auteur
        self.check_object_permissions(request, comment)
        if request.POST.get("description"):
            comment.description = request.POST.get("description")
        # Check model
        try:
            comment.full_clean()
        except ValidationError as e:
            print(e)
            return Response({'error': 'dans les informations du body'}, status=status.HTTP_400_BAD_REQUEST)
        # Sauvegarde
        try:
            comment.save()
        except IntegrityError:
            return Response({'error': "impossible de creer le comment"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = serializers.CommentsSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def delete(self, request, id, id_issue, id_comment):
        """ Cette fonction gere la requete DELETE et supprime le comment """
        # regarde si comment existe
        try:
            # Regarde si l'id de project_id de issue_id est ok plus l'id de issue_id et pk
            comment = models.Comments.objects.get(issue_id__project_id__id=id, issue_id__id=id_issue, pk=id_comment)
        except models.Comments.DoesNotExist:
            return Response({"message": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)
        # Regarde si auteur
        self.check_object_permissions(request, comment)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def choix_list(list, data, default=None):
    """ Cette fonction permet de regarde si la data est dans tout les choix pour le champ 
        si pas le cas retourne default """
    # default est la pour que la valeur ne change pas si deja setup avant
    pris = default
    for choice in list:
        if data == choice[0] or data == choice[1]:
            # le 0 est donnée car c'est la valeur que prendra le champ
            pris = choice[0]
    return pris