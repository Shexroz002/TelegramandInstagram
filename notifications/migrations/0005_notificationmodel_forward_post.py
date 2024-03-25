# Generated by Django 4.0.1 on 2024-03-23 16:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_initial'),
        ('notifications', '0004_notificationmodel_notification_group_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationmodel',
            name='forward_post',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notification_forward_post', to='posts.post'),
        ),
    ]
