# Generated by Django 2.2.1 on 2019-08-12 15:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('edit_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='skill',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='edit_app.Skill'),
        ),
    ]
