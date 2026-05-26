from django import forms
from .models import Payment, Booking


class PhonePePaymentForm(forms.ModelForm):
    """
    Form for handling PhonePe UPI payments
    This form is mainly for backend processing, frontend uses PhonePe API
    """
    class Meta:
        model = Payment
        fields = ('phonepe_transaction_id', 'phonepe_response_code')
        widgets = {
            'phonepe_transaction_id': forms.HiddenInput(),
            'phonepe_response_code': forms.HiddenInput(),
        }


class PaymentVerificationForm(forms.Form):
    """
    Form to verify payment status from PhonePe
    """
    phonepe_order_id = forms.CharField(max_length=100)
    phonepe_transaction_id = forms.CharField(max_length=100)
