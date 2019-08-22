from django.urls import path
from . import views

urlpatterns = [
   path('', views.index, name='index'),
   path('add_skill/<int:num>', views.add_skill, name='add_skill'),
   path('edit_skill/<int:num>', views.edit_skill, name='edit_skill'),
   path('del_skill/<int:num>', views.del_skill, name='del_skill'),
   path('cre_task', views.cre_task, name='cre_task'),
   path('edit_task/<int:num>', views.edit_task, name='edit_task'),
   path('list_task', views.list_task, name='list_task'),
   path('del_task/<int:num>', views.del_task, name='del_task'),
   path('rem_sub/<str:table>/<int:num_skill>/<int:num_other>', views.rem_sub, name='rem_sub'),
   path('add_sub/<str:table>/<int:num_skill>/<int:num_other>', views.add_sub, name='add_sub'),
   path('add_task/<str:table>/<int:num_skill>/<int:num_other>', views.add_task, name='add_task'),
   path('rem_task/<str:table>/<int:num_skill>/<int:num_other>', views.rem_task, name='rem_task'),
   path('add_folder', views.add_folder, name='add_folder'),
   path('edit_folder/<int:num>', views.edit_folder, name='edit_folder'),
   path('del_folder/<int:num>', views.del_folder, name='del_folder'),
   path('change_folder/<int:num_task>/<int:num_folder>', views.change_folder, name='change_folder'),
   path('view_versions/<int:num_skill>', views.view_versions, name='view_versions'),
   path('view_version/<int:num_skill>/<int:num_version>', views.view_version, name='view_version'),
   path('restore/<int:num_skill>/<int:num_version>', views.restore_version, name='restore_version'),
   path('list_deleted', views.list_deleted, name='list_deleted'),
   path('change_datetime', views.change_datetime, name='change_datetime'),
]
