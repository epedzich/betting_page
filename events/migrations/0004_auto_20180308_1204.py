# Generated by Django 2.0.2 on 2018-03-08 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_event_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventsparticipant',
            name='is_winner',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='event',
            name='status',
            field=models.CharField(choices=[('active', 'active'), ('finished', 'finished'), ('resolved', 'resolved')], default='active', max_length=1),
        ),
    ]
