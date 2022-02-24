# Generated by Django 3.2.12 on 2022-02-24 06:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('all_time_high', '0012_auto_20220223_0041'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationsetting',
            name='email_list_notification_interval',
            field=models.PositiveSmallIntegerField(default=30, help_text='Dakika bazında', verbose_name="EPosta Listesi'ne Mesaj Gönderme Sıklığı"),
        ),
        migrations.AddField(
            model_name='notificationsetting',
            name='is_email_list_enabled',
            field=models.BooleanField(default=True, verbose_name='EPosta Listesi Bildirimi Açık'),
        ),
    ]
