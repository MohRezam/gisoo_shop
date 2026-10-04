from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0010_sms_settings"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="smssettings",
            name="sms_new_image",
        ),
    ]
