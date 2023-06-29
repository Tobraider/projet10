from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from . import models

class UserSerializer(ModelSerializer):

    class Meta:
        model=models.User
        fields=['id', 'last_name', 'first_name']


class ContributorsSerializer(ModelSerializer):

    role = serializers.CharField(source='get_role_display')
    user = UserSerializer()

    class Meta:
        model = models.Contributors
        fields = ['user', 'role']


class ProjectSerializer(ModelSerializer):
    
    author_user_id = UserSerializer()
    type = serializers.CharField(source='get_type_display')

    class Meta:
        model = models.Projects
        fields = ['id', 'title', 'author_user_id', 'type']


class ProjectDetailSerializer(ModelSerializer):
    
    type = serializers.CharField(source='get_type_display')
    author_user_id = UserSerializer()
    contributors = UserSerializer(many=True)

    class Meta:
        model = models.Projects
        fields = ['id', 'title', 'description', 'author_user_id', 'type', 'contributors']

class ListeErrorSerializer(ModelSerializer):
    
    class Meta:
        model = models.User
        fields = ['email']

class ProjectSimplifierSerializer(ModelSerializer):

    class Meta:
        model = models.Projects
        fields = ['id', 'title']


class IssuesSerializer(ModelSerializer):

    tag = serializers.CharField(source='get_tag_display')
    priority = serializers.CharField(source='get_priority_display')
    status = serializers.CharField(source='get_status_display')

    project_id = ProjectSimplifierSerializer()
    author_user_id = UserSerializer()
    assignee_user_id = UserSerializer()

    class Meta:
        model = models.Issues
        fields = '__all__'
        # fields = ['title', 'desc', 'tag', 'priority', 'project_id', 'status', 'author_user_id', 'assignee_user_id', 'time_created']


class IssueSimpleSerializer(ModelSerializer):

    class Meta:
        model = models.Issues
        fields = ['pk', 'title', 'desc']


class CommentsSerializer(ModelSerializer):

    author_user_id = UserSerializer()
    issue_id = IssueSimpleSerializer()

    class Meta:
        model = models.Comments
        fields = '__all__'