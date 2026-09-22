from django import forms


class PaymentApproveForm(forms.Form):
    bank_verified = forms.BooleanField(
        required=True,
        label="واریز بانکی را در صورتحساب مقصد بررسی کردم",
        help_text="قبل از تأیید، مبلغ و زمان را با رسید کاربر مطابقت دهید.",
    )

    bank_reference = forms.CharField(
        required=True,
        max_length=255,
        label="شماره پیگیری بانک (رفرنس)",
        help_text=(
            "شماره پیگیری / مرجع تراکنش که بانک یا اپ بانکی روی ردیف واریز نشان می‌دهد. "
            "برای حسابرسی و جلوگیری از تأیید دوبارهٔ یک رسید لازم است."
        ),
    )

    reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 4}),
        label="یادداشت (اختیاری)",
        help_text="توضیح داخلی برای تیم؛ برای مشتری نمایش داده نمی‌شود.",
    )


class PaymentRejectForm(forms.Form):
    reason = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={"rows": 5}),
        label="دلیل رد رسید",
        help_text="این متن برای مشتری قابل مشاهده است؛ واضح و مؤدبانه بنویسید.",
    )
