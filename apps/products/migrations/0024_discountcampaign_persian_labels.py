from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0023_productfaq"),
    ]

    operations = [
        migrations.AlterField(
            model_name="discountcampaign",
            name="title",
            field=models.CharField(max_length=255, verbose_name="عنوان"),
        ),
        migrations.AlterField(
            model_name="discountcampaign",
            name="starts_at",
            field=models.DateTimeField(verbose_name="زمان شروع"),
        ),
        migrations.AlterField(
            model_name="discountcampaign",
            name="ends_at",
            field=models.DateTimeField(verbose_name="زمان پایان"),
        ),
        migrations.AlterField(
            model_name="discountcampaign",
            name="is_active",
            field=models.BooleanField(default=True, verbose_name="فعال"),
        ),
    ]
