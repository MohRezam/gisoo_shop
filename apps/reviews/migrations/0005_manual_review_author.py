from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("reviews", "0004_remove_unique_user_product_review"),
    ]

    operations = [
        migrations.AddField(
            model_name="productreview",
            name="author_name",
            field=models.CharField(
                blank=True,
                default="",
                help_text=(
                    "برای نظر دستی این نام روی سایت دیده می‌شود و لازم نیست کاربر بسازید. "
                    "اگر خالی باشد، نام یا شماره همان کاربر نشان داده می‌شود."
                ),
                max_length=80,
                verbose_name="نام نویسنده",
            ),
        ),
        migrations.AlterField(
            model_name="productreview",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.deletion.CASCADE,
                related_name="product_reviews",
                to=settings.AUTH_USER_MODEL,
                verbose_name="کاربر",
            ),
        ),
    ]
