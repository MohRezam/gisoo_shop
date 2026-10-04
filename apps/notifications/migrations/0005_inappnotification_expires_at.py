from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0004_sync_persian_labels"),
    ]

    operations = [
        migrations.AddField(
            model_name="inappnotification",
            name="expires_at",
            field=models.DateTimeField(
                blank=True,
                help_text="اگر تنظیم شود، در اینباکس کاربر شمارندهٔ معکوس نشان داده می‌شود.",
                null=True,
                verbose_name="مهلت اقدام",
            ),
        ),
    ]
