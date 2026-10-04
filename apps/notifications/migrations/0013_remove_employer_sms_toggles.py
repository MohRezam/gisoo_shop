from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0012_remove_notification_type_new_image"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="smssettings",
            name="sms_new_consultation",
        ),
        migrations.RemoveField(
            model_name="smssettings",
            name="sms_new_comment",
        ),
    ]
