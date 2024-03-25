# Generated by Django 4.0.1 on 2024-03-17 09:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_initial'),
        ('notifications', '0003_notificationmodel_is_seen'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationmodel',
            name='notification_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notification_group', to='chat.groupchat'),
        ),
        migrations.AlterField(
            model_name='notificationmodel',
            name='type_notification',
            field=models.IntegerField(choices=[(0, 'LIKE'), (1, 'FOLLOWING'), (2, 'CHAT'), (3, 'COMMENT'), (4, 'STORY'), (5, 'GROUP')], default=0),
        ),
    ]
