from django.db import models
import reversion
from reversion.models import Version
from django.utils import timezone

difficulties = [
   (0, "Nothing new to find"),
   (1, "Needs minutes to find"),
   (2, "Needs hours to find"),
   (3, "Hard to find by yourself")
]

status_types = [
   ('blue', 'Validated'),
   ('orange', 'Waiting for validation'),
   ('red', 'Todo'),
]

status_types_dict = {
   'blue': 'Validated',
   'orange': 'Waiting for validation',
   'red': 'Todo',
}

class Folder(models.Model):
   name = models.CharField(max_length=256)

class Task(models.Model):
   name = models.CharField(max_length=256)
   
   parent = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True, blank=True)
   
   task_abstract = models.TextField(blank=True)
   solution_abstract = models.TextField(blank=True)
   path = models.CharField(max_length=4096, blank=True)
   source = models.CharField(max_length=4096, blank=True)
   
   difficulty = models.IntegerField(choices = difficulties, default=0)
   
   comments = models.TextField(blank=True)
   
   status = models.CharField(max_length=7, choices=status_types, default='red')
   
   def __str__(self):
      return self.name

@reversion.register()
class Skill(models.Model):
   name = models.CharField(max_length=256)
   parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, related_name='children', blank=True)
   prerequisites = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='applications')
   abstract = models.TextField(blank=True)
   
   difficulty = models.IntegerField(choices = difficulties, default=0)
   
   resources = models.TextField(blank=True)
   comments = models.TextField(blank=True)
   
   status = models.CharField(max_length=7, choices=status_types, default='red')
   
   introductory_tasks = models.ManyToManyField(Task, related_name='introduction_of', blank=True)
   tasks = models.ManyToManyField(Task, related_name='skills', blank=True)
   
   subskills = models.ManyToManyField('self', symmetrical=False, related_name='surskills', blank=True)
   validation = models.CharField(max_length=3, choices=[
      ('AND', 'And'),
      ('OR', 'Or'),
   ], default='AND')
   
   last_update = models.CharField(max_length=256)
   
   def __str__(self):
      if self.parent:
         return self.name + "      (" + self.parent.name + ")"
      return self.name
