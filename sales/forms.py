from django import forms


class CancelSaleForm(forms.Form):
    cancellation_reason = forms.CharField(max_length=1000, widget=forms.Textarea(attrs={"rows": 3}))
