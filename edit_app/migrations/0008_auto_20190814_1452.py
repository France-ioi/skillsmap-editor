# Generated by Django 2.2.1 on 2019-08-14 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edit_app', '0007_auto_20190814_0836'),
    ]

    operations = [
        migrations.AddField(
            model_name='skill',
            name='subskills',
            field=models.ManyToManyField(blank=True, related_name='surskills', to='edit_app.Skill'),
        ),
        migrations.AddField(
            model_name='skill',
            name='validation',
            field=models.CharField(choices=[('AND', 'And'), ('OR', 'Or')], default='AND', max_length=3),
        ),
    ]
