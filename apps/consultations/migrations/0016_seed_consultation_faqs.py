from django.db import migrations

SEED = [
    (
        1,
        "آیا دریافت مشاوره رایگان است؟",
        "بله؛ مشاوره انتخاب محصول در گیسو سنتر کاملاً رایگان است و فقط برای کمک به انتخاب درست طراحی شده.",
    ),
    (
        2,
        "چه مدت بعد پاسخ دریافت می‌کنم؟",
        "پس از بررسی اطلاعات، در اولین فرصت با شما تماس می‌گیریم؛ معمولاً در همان روز کاری.",
    ),
    (
        3,
        "آیا این مشاوره پزشکی است؟",
        "خیر؛ این صفحه جایگزین مشاوره پزشکی نیست و صرفاً برای پیشنهاد محصول متناسب با نیاز مو طراحی شده است.",
    ),
    (
        4,
        "اگر چند مشکل مو داشته باشم چه کار کنم؟",
        "نزدیک‌ترین گزینه به مشکل اصلی را انتخاب کنید و در تماس مشاوره جزئیات بیشتر را بگویید.",
    ),
    (
        5,
        "اگر بعد از خرید سؤال داشته باشم، دوباره می‌توانم مشاوره بگیرم؟",
        "بله؛ پشتیبانی گیسو سنتر قبل و بعد از خرید همراه شماست.",
    ),
]


def seed_faqs(apps, schema_editor):
    ConsultationFAQ = apps.get_model("consultations", "ConsultationFAQ")
    if ConsultationFAQ.objects.exists():
        return
    ConsultationFAQ.objects.bulk_create(
        [
            ConsultationFAQ(
                ordering=order,
                question=question,
                answer=answer,
                is_active=True,
            )
            for order, question, answer in SEED
        ]
    )


def unseed_faqs(apps, schema_editor):
    ConsultationFAQ = apps.get_model("consultations", "ConsultationFAQ")
    questions = [row[1] for row in SEED]
    ConsultationFAQ.objects.filter(question__in=questions).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("consultations", "0015_consultationfaq"),
    ]

    operations = [
        migrations.RunPython(seed_faqs, unseed_faqs),
    ]
