from django.db import migrations

SEED = [
    (
        1,
        "از چه راه‌هایی می‌توانم با گیسو سنتر تماس بگیرم؟",
        "از طریق تماس تلفنی، واتساپ و ایمیل می‌توانید با تیم پشتیبانی در ارتباط باشید. اطلاعات هر بخش در همین صفحه آمده است.",
    ),
    (
        2,
        "ساعات پاسخ‌گویی تلفنی چه زمانی است؟",
        "پاسخ‌گویی تلفنی از ساعت ۹ تا ۱۸ انجام می‌شود.",
    ),
    (
        3,
        "آیا از واتساپ هم پاسخ می‌دهید؟",
        "بله؛ از طریق واتساپ می‌توانید برای مشاوره انتخاب محصول و پیگیری سفارش پیام بگذارید.",
    ),
    (
        4,
        "برای انتخاب محصول مناسب چه کار کنم؟",
        "اگر مطمئن نیستید کدام محصول برای نیاز موهایتان مناسب است، از صفحه مشاوره انتخاب محصول استفاده کنید یا با پشتیبانی تماس بگیرید.",
    ),
    (
        5,
        "سؤال من در این صفحه نبود. کجا بپرسم؟",
        "می‌توانید صفحه سوالات پرتکرار را ببینید یا از راه‌های تماس همین صفحه با پشتیبانی در ارتباط باشید.",
    ),
]


def seed_faqs(apps, schema_editor):
    ContactFAQ = apps.get_model("home", "ContactFAQ")
    if ContactFAQ.objects.exists():
        return
    ContactFAQ.objects.bulk_create(
        [
            ContactFAQ(
                ordering=order,
                question=question,
                answer=answer,
                is_active=True,
            )
            for order, question, answer in SEED
        ]
    )


def unseed_faqs(apps, schema_editor):
    ContactFAQ = apps.get_model("home", "ContactFAQ")
    questions = [row[1] for row in SEED]
    ContactFAQ.objects.filter(question__in=questions).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0012_contactfaq"),
    ]

    operations = [
        migrations.RunPython(seed_faqs, unseed_faqs),
    ]
