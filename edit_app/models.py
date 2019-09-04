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
   
   def __str__(self):
      if self.parent:
         return self.name + "      (" + self.parent.name + ")"
      return self.name
   
   def last_update(self):
      versions = Version.objects.get_for_object(self)
      if len(versions) != 0:
         return timezone.localtime(versions[0].revision.date_created).strftime('%Y-%m-%d %H:%M:%S.%f')
      else:
         return ""
   
   def last_update_text(self):
      versions = Version.objects.get_for_object(self)
      if len(versions) != 0:
         if versions[0].revision.user:
            return timezone.localtime(versions[0].revision.date_created).strftime('%Y-%m-%d %H:%M:%S.%f') + " by " + versions[0].revision.user.username
         else:
            return timezone.localtime(versions[0].revision.date_created).strftime('%Y-%m-%d %H:%M:%S.%f')
      else:
         return ""
   
   def jsonify(self):
      json = 'name: "' + self.name + '",'
      json += 'children: ['
      for child in self.children.all():
         json += str(child.id) + ', '
      json += '],'
      json += 'status: "' + self.status + '",'
      json += 'surskills: ['
      for surskill in self.surskills.all():
         if not surskill.is_deleted():
            json += str(surskill.id) + ', '
      json += "],"
      json += 'prerequisites: ['
      for prereq in self.prerequisites.all():
         if not prereq.is_deleted():
            json += str(prereq.id) + ', '
      json += "],"
      json += 'subskills: ['
      for subskill in self.subskills.all():
         if not subskill.is_deleted():
            json += str(subskill.id) + ', '
      json += "],"
      json += 'title: "Last edit : ' + self.last_update_text() + '\\n'
      json += 'Status : ' + status_types_dict[self.status] + '\\n'
      json += '",'
      return json
   
   def is_deleted(self):
      curSkill = self
      while curSkill != None:
         if curSkill.name == 'deleted':
            return True
         curSkill = curSkill.parent
      return False
