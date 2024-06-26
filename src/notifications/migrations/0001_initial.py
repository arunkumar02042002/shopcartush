# Generated by Django 4.2.7 on 2024-01-03 04:00

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ScheduledNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('type', models.CharField(choices=[('PUBLIC', 'PUBLIC'), ('USER_SPECIFIC', 'USER_SPECIFIC')], max_length=16)),
                ('user_ids', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), blank=True, default=list, null=True, size=None)),
                ('event_type', models.CharField(choices=[('ORDER_UPDATE', 'ORDER_UPDATE'), ('PROMOTIONAL', 'PROMOTIONAL'), ('ANNOUNCEMENT', 'ANNOUNCEMENT')], max_length=20)),
                ('send_via', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('PHONE_SMS', 'PHONE_SMS'), ('EMAIL', 'EMAIL'), ('PUSH_NOTIFICATION', 'PUSH_NOTIFICATION'), ('APP_NOTIFICATION', 'APP_NOTIFICATION'), ('WHATSAPP', 'WHATSAPP')], max_length=20), default=list, size=None)),
                ('status', models.CharField(choices=[('PENDING', 'PENDING'), ('SUCCESS', 'SUCCESS')], max_length=16)),
                ('scheduled_at', models.DateTimeField()),
                ('extras', models.JSONField(default=dict)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('event_type', models.CharField(choices=[('ORDER_UPDATE', 'ORDER_UPDATE'), ('PROMOTIONAL', 'PROMOTIONAL'), ('ANNOUNCEMENT', 'ANNOUNCEMENT')], max_length=20)),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('medium', models.CharField(choices=[('PHONE_SMS', 'PHONE_SMS'), ('EMAIL', 'EMAIL'), ('PUSH_NOTIFICATION', 'PUSH_NOTIFICATION'), ('APP_NOTIFICATION', 'APP_NOTIFICATION'), ('WHATSAPP', 'WHATSAPP')], max_length=20)),
                ('extras', models.JSONField(default=dict)),
                ('status', models.CharField(choices=[('PENDING', 'PENDING'), ('SUCCESS', 'SUCCESS')], max_length=16)),
                ('reference', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='notifications.schedulednotification')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='notification',
            constraint=models.UniqueConstraint(fields=('user', 'reference', 'medium'), name='unique_user_notification'),
        ),
    ]
