# Generated by Django 4.1.7 on 2023-03-22 11:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('file_uploader', '0002_alter_uploadfile_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadfile',
            name='file',
            field=models.FileField(upload_to=''),
        ),
    ]