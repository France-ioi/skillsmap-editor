from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.forms import inlineformset_factory
from .models import *
from .forms import *
from datetime import datetime
from django.utils import timezone
from reversion.models import Version
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
import pytz

roots = Skill.objects.filter(name='root')
deleteds = Skill.objects.filter(name='deleted')

def generate_tree(request):
   json = "{"
   for skill in Skill.objects.all().prefetch_related('surskills', 'children', 'prerequisites', 'subskills'):
      json += str(skill.id) + ": {"
      json += skill.jsonify() + "modified: "
      if skill.last_update() > request.session.get('datetime', timezone.now().strftime('%Y-%m-%d %H:%M:%S.%f')):
         json += "true"
      else:
         json += "false"
      json += "},"
   json += "}"
   return json

def index(request):
   if not request.user.is_authenticated:
      username = ""
      password = ""
      if ('username' in request.POST) and ('password' in request.POST):
         username = request.POST['username']
         password = request.POST['password']
      user = authenticate(request, username=username, password=password)
      
      if user is None:
         return render(request, 'login_form.html', {})
      else:
         login(request, user)
   return render(request, 'index.html', {
      'root': roots[0],
      'json_tree': generate_tree(request)
   })

@login_required
def list_deleted(request):
   return render(request, 'index.html', {
      'root': deleteds[0],
      'json_tree': generate_tree(request)
   })

@login_required
def add_skill(request, num):
   if len(Skill.objects.filter(id=num)) == 0:
      return redirect('/')
   skill = Skill.objects.filter(id=num)[0]
   
   with reversion.create_revision():
      reversion.set_comment("New Skill")
      reversion.set_date_created(timezone.now())
      reversion.set_user(request.user)
      
      new_skill = Skill(parent = skill, name = 'new_skill')
      new_skill.save()
   
   return redirect('/edit_skill/' + str(new_skill.id))

@login_required
def edit_skill(request, num):
   if len(Skill.objects.filter(id=num)) == 0:
      return redirect('/')
   skill = Skill.objects.filter(id=num)[0]
   if request.method == 'POST':
      form = SkillForm(request.POST, request.FILES, instance=skill)
      
      if form.is_valid() and form.has_changed():
         with reversion.create_revision():
            reversion.set_comment("Edit Skill " + str(form.instance.name))
            reversion.set_date_created(timezone.now())
            reversion.set_user(request.user)
            
            form.save()
   form = SkillForm(instance=skill)
   return render(request, 'edit_skill.html', {
      'form' : form, 
      'skill' : skill, 
      'root': roots[0],
      'tasks': Task.objects.all(),
      'json_tree': generate_tree(request),
      'skills': Skill.objects.all(),
      'folders': Folder.objects.all(),
      'date': request.session.get('datetime', timezone.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
   })

@login_required
def del_skill(request, num):
   if len(Skill.objects.filter(id=num)) == 0:
      return redirect('/')
   skill = Skill.objects.filter(id=num)[0]
   
   if skill.name == "root":
      return redirect('/')
   
   with reversion.create_revision():
      reversion.set_comment("Delete Skill " + str(skill.name))
      reversion.set_date_created(timezone.now())
      reversion.set_user(request.user)
      
      skill.parent = deleteds[0]
      skill.save()
      
   return redirect('/')

@login_required
def list_task(request):
   return render(request, 'tasks_list.html', {
      'tasks': Task.objects.all(),
      'folders': Folder.objects.all()
   })
   
@login_required
def cre_task(request):
   new_task = Task(name = 'new_task', parent=Folder.objects.filter(name="unsorted")[0])
   new_task.save()
   return redirect('/edit_task/' + str(new_task.id))

@login_required
def edit_task(request, num):
   if len(Task.objects.filter(id=num)) == 0:
      return redirect('/list_task')
   task = Task.objects.filter(id=num)[0]
   if request.method == 'POST':
      form = TaskForm(request.POST, request.FILES, instance=task)
      
      if form.is_valid():
         form.save()
         return redirect('/edit_task/' + str(task.id))
   form = TaskForm(instance=task)
   return render(request, 'edit_task.html', {
      'form' : form,
      'task' : task, 
      'tasks': Task.objects.all(),
      'skills': Skill.objects.all(),
      'folders': Folder.objects.all()
   })

@login_required
def del_task(request, num):
   if len(Task.objects.filter(id=num)) == 0:
      return redirect('/')
   task = Task.objects.filter(id=num)[0]
   task.delete()
   return redirect('/list_task')

@login_required
def add_folder(request):
   new_folder = Folder(name = 'new_folder')
   new_folder.save()
   return redirect('/edit_folder/' + str(new_folder.id))

@login_required
def edit_folder(request, num):
   if len(Folder.objects.filter(id=num)) == 0:
      return redirect('/list_task')
   folder = Folder.objects.filter(id=num)[0]
   
   if folder.name == 'unsorted':
      return redirect('/list_task')
   
   if request.method == 'POST':
      form = FolderForm(request.POST, request.FILES, instance=folder)
      
      if form.is_valid():
         form.save()
         return redirect('/edit_folder/' + str(folder.id))
   form = FolderForm(instance=folder)
   return render(request, 'edit_folder.html', {
      'form' : form,
      'folder': folder,
      'tasks': Task.objects.all(),
      'skills': Skill.objects.all(),
      'folders': Folder.objects.all()
   })

@login_required
def del_folder(request, num):
   if len(Folder.objects.filter(id=num)) == 0:
      return redirect('/')
   folder = Folder.objects.filter(id=num)[0]
   folder.delete()
   return redirect('/list_task')

@login_required   
def rem_sub(request, table, num_skill, num_other):
   if len(Skill.objects.filter(id=num_skill)) == 0:
      return redirect('/')
   skill = Skill.objects.filter(id=num_skill)[0]
   
   objects = None
   if table == 'subskills':
      objects = skill.subskills
   elif table == 'prerequisites':
      objects = skill.prerequisites
   
   if not objects:
      return redirect('/edit_skill/' + str(num_skill))
   
   if len(objects.filter(id=num_other)) == 0:
      return redirect('/edit_skill/' + str(num_skill))
   other = objects.filter(id=num_other)[0]
   
   with reversion.create_revision():
      reversion.set_comment("Edit Skill (" + table + ") " + str(skill.name))
      reversion.set_date_created(timezone.now())
      reversion.set_user(request.user)
      
      objects.remove(other)
      skill.save()
   
   return redirect('/edit_skill/' + str(num_skill))

@login_required   
def add_sub(request, table, num_skill, num_other):
   if len(Skill.objects.filter(id=num_skill)) == 0:
      return redirect('/')
   skill = Skill.objects.filter(id=num_skill)[0]
   
   if len(Skill.objects.filter(id=num_other)) == 0:
      return redirect('/edit_skill/' + str(num_skill))
   other = Skill.objects.filter(id=num_other)[0]
   
   with reversion.create_revision():
      reversion.set_comment("Edit Skill (" + table + ") " + str(skill.name))
      reversion.set_date_created(timezone.now())
      reversion.set_user(request.user)
      
      if table == 'subskills':
         skill.subskills.add(other)
      elif table == 'prerequisites':
         skill.prerequisites.add(other)
      elif table == 'parent':
         if len(skill.surskills.filter(name=other.name)):
            skill.surskills.remove(other)
            skill.surskills.add(skill.parent)
            skill.parent = other
            
         else:
            skill.parent = other
      skill.save()
      
   return redirect('/edit_skill/' + str(num_skill))

@login_required   
def rem_task(request, table, num_skill, num_other):
   if len(Skill.objects.filter(id=num_skill)) == 0:
      return redirect('/')
   skill = Skill.objects.filter(id=num_skill)[0]
   
   objects = None
   if table == 'introductory_tasks':
      objects = skill.introductory_tasks
   elif table == 'tasks':
      objects = skill.tasks
   
   if not objects:
      return redirect('/edit_skill/' + str(num_skill))
   
   if len(Task.objects.filter(id=num_other)) == 0:
      return redirect('/edit_skill/' + str(num_skill))
   other = Task.objects.filter(id=num_other)[0]
   
   objects.remove(other)
   return redirect('/edit_task/' + str(num_other))
 
@login_required  
def add_task(request, table, num_skill, num_other):
   if len(Skill.objects.filter(id=num_skill)) == 0:
      return redirect('/')
   skill = Skill.objects.filter(id=num_skill)[0]
   
   objects = None
   if table == 'introductory_tasks':
      objects = skill.introductory_tasks
   elif table == 'tasks':
      objects = skill.tasks
   
   if not objects:
      return redirect('/edit_skill/' + str(num_skill))
   
   if len(Task.objects.filter(id=num_other)) == 0:
      return redirect('/edit_skill/' + str(num_skill))
   other = Task.objects.filter(id=num_other)[0]
   
   objects.add(other)
   return redirect('/edit_task/' + str(num_other))

@login_required
def change_folder(request, num_task, num_folder):
   if len(Task.objects.filter(id=num_task)) == 0:
      return redirect('/list_task')
   task = Task.objects.filter(id=num_task)[0]
   
   if len(Folder.objects.filter(id=num_folder)) == 0:
      return redirect('/edit_task/' + str(num_task))
   other = Folder.objects.filter(id=num_folder)[0]
   
   task.parent = other;
   task.save()
   return redirect('/edit_task/' + str(num_task))

@login_required
def view_versions(request, num_skill):
   if len(Skill.objects.filter(id=num_skill)) == 0:
      return redirect('/')
   skill = Skill.objects.filter(id=num_skill)[0]
   versions = Version.objects.get_for_object(skill)
   
   return render(request, 'view_versions.html', {
      'skill': skill,
      'versions': versions,
      'form': SkillForm(instance=skill),
      'tasks': Task.objects.all(),
      'skills': Skill.objects.all(),
      'root': roots[0],
      'date': request.session.get('datetime', timezone.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
   })

@login_required
def view_version(request, num_skill, num_version):
   if len(Skill.objects.filter(id=num_skill)) == 0:
      return redirect('/')
   skill = Skill.objects.filter(id=num_skill)[0]
   
   if num_version >= len(Version.objects.get_for_object(skill)):
      return redirect('/view_versions/' + str(num_skill))
   version = Version.objects.get_for_object(skill)[num_version]
   
   parent = None
   if len(Skill.objects.filter(id=version.field_dict["parent_id"])) != 0:
      parent = Skill.objects.filter(id=version.field_dict["parent_id"])[0]
   
   prerequisites = []
   for prerequisite_id in version.field_dict["prerequisites"]:
      prerequisites.append(Skill.objects.filter(id=prerequisite_id)[0])
   
   subskills = []
   for subskill_id in version.field_dict["subskills"]:
      subskills.append(Skill.objects.filter(id=subskill_id)[0])
   
   introductory_tasks = []
   for task_id in version.field_dict["introductory_tasks"]:
      if len(Task.objects.filter(id=task_id)) != 0:
         introductory_tasks.append(Task.objects.filter(id=task_id)[0])
   
   return render(request, 'version_viewer.html', {
      'skill': skill,
      'parent': parent,
      'prerequisites': prerequisites,
      'subskills': subskills,
      'introductory_tasks': introductory_tasks,
      'version': version,
      'version_id': num_version,
      'form': SkillForm(instance=skill),
      'tasks': Task.objects.all(),
      'skills': Skill.objects.all()
   })

@login_required
def restore_version(request, num_skill, num_version):
   if len(Skill.objects.filter(id=num_skill)) == 0:
      return redirect('/')
   skill = Skill.objects.filter(id=num_skill)[0]
   
   if num_version >= len(Version.objects.get_for_object(skill)):
      return redirect('/view_versions/' + str(num_skill))
   version = Version.objects.get_for_object(skill)[num_version]
   
   with reversion.create_revision():
      reversion.set_comment("Restoring Skill " + str(skill.name))
      reversion.set_date_created(timezone.now())
      reversion.set_user(request.user)
      
      skill.name = version.field_dict["name"]
      
      if len(Skill.objects.filter(id=version.field_dict["parent_id"])) != 0:
         skill.parent = Skill.objects.filter(id=version.field_dict["parent_id"])[0]
      else:
         skill.parent = None
      
      skill.prerequisites.clear()
      for prerequisite_id in version.field_dict["prerequisites"]:
         skill.prerequisites.add(Skill.objects.filter(id=prerequisite_id)[0])
      
      skill.subskills.clear()
      for subskill_id in version.field_dict["subskills"]:
         skill.subskills.add(Skill.objects.filter(id=subskill_id)[0])
      
      skill.validation = version.field_dict["validation"]
      skill.abstract = version.field_dict["abstract"]
      skill.difficulty = version.field_dict["difficulty"]
      skill.resources = version.field_dict["resources"]
      
      skill.introductory_tasks.clear()
      for task_id in version.field_dict["introductory_tasks"]:
         if len(Task.objects.filter(id=task_id)) != 0:
            skill.introductory_tasks.add(Task.objects.filter(id=task_id)[0])
      
      skill.save()
   
   return redirect('/edit_skill/' + str(num_skill))

@login_required
def change_datetime(request):
   if request.method == 'POST':
      form = DatetimeForm(request.POST)
      
      if form.is_valid():
         request.session['datetime'] = form.cleaned_data['datetime'].strftime('%Y-%m-%d %H:%M:%S.%f')
         return redirect('/')
   return render(request, 'change_datetime.html', {
      'form': DatetimeForm()
   })
