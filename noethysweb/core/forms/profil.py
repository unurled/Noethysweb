from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, HTML
from crispy_forms.bootstrap import Field
from core.forms.base import FormulaireBase
from core.models import Structure, Utilisateur

class FormSignature(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = ['signature']
        widgets = {
            'signature': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }
        labels = {
            'signature': 'Ajouter / Modifier votre signature',
        }
