# Generated by Django 2.2.1 on 2019-08-12 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edit_app', '0004_auto_20190812_1851'),
    ]

    operations = [
        migrations.AlterField(
            model_name='skill',
            name='introductory_tasks',
            field=models.ManyToManyField(blank=True, related_name='introduction_of', to='edit_app.Task'),
        ),
        migrations.AlterField(
            model_name='skill',
            name='prerequisites',
            field=models.ManyToManyField(blank=True, related_name='_skill_prerequisites_+', to='edit_app.Skill'),
        ),
        migrations.AlterField(
            model_name='skill',
            name='tasks',
            field=models.ManyToManyField(blank=True, related_name='skills', to='edit_app.Task'),
        ),
    ]
