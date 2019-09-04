from django.forms import *
from .models import *
from django.utils import timezone

class SkillForm(ModelForm):
   class Meta:
      model = Skill
      fields = ['name', 'validation', 'abstract', 'difficulty', 'resources', 'comments', 'status']

class TaskForm(ModelForm):
   class Meta:
      model = Task
      fields = ['name', 'path', 'source', 'task_abstract', 'solution_abstract', 'difficulty', 'comments', 'status']

class FolderForm(ModelForm):
   class Meta:
      model = Folder
      fields = ['name']

class DatetimeForm(forms.Form):
   datetime = DateTimeField(initial=timezone.now)
