from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class Projects(models.Model):
    IOS = "IO"
    ANDROID = "AN"
    SITE_WEB = "SW"
    type_choice = (
        (IOS, "IOS"),
        (ANDROID, "Android"),
        (SITE_WEB, "Site web"),
    )
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2048, blank=True, null=True)
    author_user_id = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="auteur_project")
    type = models.CharField(max_length=2, choices=type_choice)
    contributors = models.ManyToManyField(to=User, through="Contributors", related_name="contributions")


class Issues(models.Model):
        
    BUG = "BG"
    AMELIORATION = "AM"
    TACHE = "TC"
    tag_choice = (
        (BUG,"BUG"),
        (AMELIORATION,"AMELIORATION"),
        (TACHE,"TACHE"),
    )
    FAIBLE = "FB"
    MOYENNE = "MO"
    ELEVEE = "EL"
    priority_choice = (
        (FAIBLE,"FAIBLE"),
        (MOYENNE,"MOYENNE"),
        (ELEVEE,"ELEVEE"),
    )
    A_FAIRE = "AF"
    EN_COURS = "EC"
    TERMINE = "TE"
    status_choice = (
        (A_FAIRE,"A faire"),
        (EN_COURS,"En cours"),
        (TERMINE,"Termine"),
    )
    title = models.CharField(max_length=128)
    desc = models.TextField(max_length=2048, blank=True)
    tag = models.CharField(max_length=2, choices=tag_choice)
    priority = models.CharField(max_length=2, choices=priority_choice)
    project_id = models.ForeignKey(to=Projects, on_delete=models.CASCADE, related_name="projectla")
    status = models.CharField(max_length=2, choices=status_choice)
    author_user_id = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="auteur_issue")
    assignee_user_id = models.ForeignKey(to=User, on_delete=models.SET_DEFAULT, default=0)
    time_created = models.DateTimeField(auto_now_add=True)

    def full_clean(self, *args, **kwargs):
        # permet de mettre une valeur par default qui soit un ForeignKey
        try:
            # existe pas de user avec un id de 0
            if not self.assignee_user_id:
                self.assignee_user_id = self.author_user_id
        except User.DoesNotExist:
            self.assignee_user_id = self.author_user_id
        super().full_clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        # permet de mettre une valeur par default qui soit un ForeignKey
        try:
            # existe pas de user avec un id de 0
            if not self.assignee_user_id:
                self.assignee_user_id = self.author_user_id
        except User.DoesNotExist:
            self.assignee_user_id = self.author_user_id
        super().save(*args, **kwargs)



class Comments(models.Model):
    description = models.TextField(max_length=2048)
    author_user_id = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="author")
    issue_id = models.ForeignKey(to=Issues, on_delete=models.CASCADE)
    time_created = models.DateTimeField(auto_now_add=True)


class Contributors(models.Model):
    CREATOR = 'CR'
    AUTHOR = 'AT'
    RESPONSABLE = 'RP'
    AUTRE = 'AU'
    ROLE_CHOICE = (
        (CREATOR, "Createur"),
        (AUTHOR, "Auteur"),
        (RESPONSABLE, "Responsable"),
        (AUTRE, "Autres")
    )
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="contributor")
    project = models.ForeignKey(to=Projects, on_delete=models.CASCADE, related_name="add_project")
    role=models.CharField(max_length=2, choices=ROLE_CHOICE)

    class Meta:
        unique_together = ('user_id', 'project_id')
