# Generated by Django 2.2.1 on 2019-08-12 15:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_abstract', models.TextField()),
                ('solution_abstract', models.TextField()),
                ('path', models.CharField(max_length=4096)),
                ('source', models.CharField(max_length=4096)),
            ],
        ),
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('abstract', models.TextField()),
                ('resources', models.TextField()),
                ('introductory_tasks', models.ManyToManyField(related_name='introduction_of', to='edit_app.Task')),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='edit_app.Skill')),
                ('prerequisites', models.ManyToManyField(related_name='_skill_prerequisites_+', to='edit_app.Skill')),
                ('tasks', models.ManyToManyField(related_name='skills', to='edit_app.Task')),
            ],
        ),
    ]
