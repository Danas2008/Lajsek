from django import forms
from django.utils.translation import gettext_lazy as _

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']
        labels = {
            'name': _('Jméno'),
            'email': _('E-mail'),
            'message': _('Zpráva'),
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': _('Vaše jméno')}),
            'email': forms.EmailInput(attrs={'placeholder': _('Váš e-mail')}),
            'message': forms.Textarea(attrs={'placeholder': _('Vaše zpráva'), 'rows': 7}),
        }
