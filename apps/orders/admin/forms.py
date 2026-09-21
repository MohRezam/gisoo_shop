from django import forms


class BulkTrackingUploadForm(forms.Form):
    file = forms.FileField(
        label="فایل اکسل",
        help_text="فقط فایل .xlsx — ستون‌ها: شماره سفارش، نام، نام خانوادگی، کد رهگیری",
    )

    def clean_file(self):
        uploaded = self.cleaned_data["file"]
        name = (uploaded.name or "").lower()
        if not name.endswith(".xlsx"):
            raise forms.ValidationError("فقط فایل با پسوند .xlsx پذیرفته می‌شود.")
        if uploaded.size and uploaded.size > 5 * 1024 * 1024:
            raise forms.ValidationError("حجم فایل نباید بیشتر از ۵ مگابایت باشد.")
        return uploaded
