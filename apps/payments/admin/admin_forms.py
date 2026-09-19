from django import forms


class PaymentApproveForm(forms.Form):
    bank_verified = forms.BooleanField(
        required=True,
        label="I verified the bank transaction",
    )

    bank_reference = forms.CharField(
        required=True,
        max_length=255,
        label="Bank reference",
        help_text="Transaction/reference number from the bank statement.",
    )

    reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 4}),
        label="Note",
    )


class PaymentRejectForm(forms.Form):
    reason = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={"rows": 5}),
        label="Rejection reason",
    )



