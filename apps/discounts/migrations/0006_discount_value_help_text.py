from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("discounts", "0005_bugfixes_cart_discount_shipping"),
    ]

    operations = [
        migrations.AlterField(
            model_name="discount",
            name="value",
            field=models.PositiveBigIntegerField(
                default=0,
                help_text=(
                    "اگر نوع «درصدی» است عدد ۰ تا ۱۰۰ بگذارید "
                    "(مثلاً ۱۰ یعنی ۱۰٪). "
                    "اگر «مبلغ ثابت» است مبلغ به تومان "
                    "(مثلاً ۳۰۰۰۰۰)."
                ),
                verbose_name="مقدار",
            ),
        ),
    ]
