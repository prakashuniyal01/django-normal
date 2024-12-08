# Generated by Django 5.1.3 on 2024-12-04 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_customuser_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('journalist', 'Journalist'), ('editor', 'Editor'), ('head', 'Head')], default='journalist', max_length=10),
        ),
    ]
