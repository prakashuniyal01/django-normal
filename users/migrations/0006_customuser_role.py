# Generated by Django 5.1.1 on 2024-09-16 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_customuser_is_journalist'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('journalist', 'Journalist'), ('editor', 'Editor'), ('head', 'Head')], default='viewer', max_length=10),
        ),
    ]
