# Generated by Django 4.0.1 on 2024-03-19 08:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='message',
            options={'ordering': ['-created_at'], 'verbose_name': 'Message'},
        ),
    ]