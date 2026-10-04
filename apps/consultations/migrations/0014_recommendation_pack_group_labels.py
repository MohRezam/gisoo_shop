from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("consultations", "0013_sync_admin_labels"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="consultationrecommendationpack",
            options={
                "ordering": ["display_order", "created_at"],
                "verbose_name": "گروه پیشنهاد محصول",
                "verbose_name_plural": "گروه‌های پیشنهاد محصول",
            },
        ),
        migrations.AlterModelOptions(
            name="consultationrecommendationpackitem",
            options={
                "ordering": ["display_order", "created_at"],
                "verbose_name": "محصول داخل گروه",
                "verbose_name_plural": "محصولات داخل گروه",
            },
        ),
        migrations.AlterField(
            model_name="consultationrecommendationpack",
            name="title",
            field=models.CharField(
                blank=True,
                default="",
                help_text="اختیاری — مثلاً «روتین روزانه»",
                max_length=255,
                verbose_name="عنوان گروه",
            ),
        ),
        migrations.AlterField(
            model_name="consultationrecommendationpack",
            name="description",
            field=models.TextField(
                blank=True,
                default="",
                help_text=(
                    "متن مشترک برای کل گروه محصولات — "
                    "مثلاً «این محصولات را به‌صورت روتین استفاده کنید»"
                ),
                verbose_name="متن کلی گروه",
            ),
        ),
        migrations.AlterField(
            model_name="consultationrecommendationpackitem",
            name="pack",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="items",
                to="consultations.consultationrecommendationpack",
                verbose_name="گروه",
            ),
        ),
        migrations.AlterField(
            model_name="consultationrecommendationpackitem",
            name="recommendation",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="pack_items",
                to="consultations.consultationrecommendation",
                verbose_name="پیشنهاد محصول",
            ),
        ),
    ]
