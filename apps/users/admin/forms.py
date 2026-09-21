from django.contrib.admin.forms import AdminPasswordChangeForm as AdminOwnPasswordChangeForm
from django.contrib.auth.forms import AdminPasswordChangeForm as UserAdminPasswordChangeForm


class GisooPasswordChangeForm(AdminOwnPasswordChangeForm):
    """Change password for the logged-in admin user — Persian labels."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["old_password"].label = "رمز فعلی"
        self.fields["new_password1"].label = "رمز جدید"
        self.fields["new_password2"].label = "تکرار رمز جدید"
        self.fields["old_password"].help_text = ""
        self.fields["new_password1"].help_text = (
            "رمز باید حداقل ۸ کاراکتر باشد و خیلی ساده/رایج نباشد."
        )
        self.fields["new_password2"].help_text = "رمز جدید را دوباره وارد کنید."


class GisooUserPasswordChangeForm(UserAdminPasswordChangeForm):
    """Change / set password for another user in admin — Persian labels."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "password1" in self.fields:
            self.fields["password1"].label = "رمز جدید"
            self.fields["password1"].help_text = (
                "رمز باید حداقل ۸ کاراکتر باشد و خیلی ساده/رایج نباشد."
            )
        if "password2" in self.fields:
            self.fields["password2"].label = "تکرار رمز جدید"
            self.fields["password2"].help_text = "رمز جدید را دوباره وارد کنید."
        if "usable_password" in self.fields:
            self.fields["usable_password"].label = "احراز هویت با رمز عبور"
