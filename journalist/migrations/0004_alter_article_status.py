# Generated by Django 5.1.3 on 2024-12-04 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journalist', '0003_comment_like'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='status',
            field=models.CharField(choices=[('submitted', 'Submitted'), ('reviewed', 'Reviewed'), ('published', 'Published'), ('rejected', 'Rejected')], default='submitted', max_length=20),
        ),
    ]
