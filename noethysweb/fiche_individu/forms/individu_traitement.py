from django import forms
from django.forms import ModelForm
from core.forms.base import FormulaireBase
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Hidden, Submit, HTML, Row, ButtonHolder, Fieldset
from crispy_forms.bootstrap import Field, FormActions, PrependedText, StrictButton
from core.utils.utils_commandes import Commandes
from core.models import Traitement, Activite, Individu
from core.widgets import Telephone, CodePostal, Ville
from fiche_individu.widgets import CarteOSM

from django import forms
from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Field, Submit
from core.models import Traitement, Individu, Activite, Utilisateur
from core.forms.select2 import Select2Widget
class Formulaire(FormulaireBase, ModelForm):
    activite = forms.ModelChoiceField(
        label="Activité",
        widget=Select2Widget(attrs={'class': 'form-control', 'data-url': '/activite/search/'}),
        queryset=Activite.objects.none().order_by("-date_fin"),
        required=True
    )

    class Meta:
        model = Traitement
        fields = "__all__"
        widgets = {
            'Description': forms.Textarea(attrs={'rows': 5, 'style': 'width: 100%;'}),  # Champ Description plus large
            'date': forms.DateInput(attrs={'type': 'date'}),  # Sélecteur de dates
            'individu': Select2Widget(attrs={'class': 'form-control', 'data-url': '/individu/search/'})  # Ajoutez l'URL pour la recherche
        }

    def __init__(self, *args, **kwargs):
        super(Formulaire, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'contacts_form'
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-2'
        self.helper.field_class = 'col-md-10'

        self.fields["activite"].queryset = Activite.objects.filter(structure__in=self.request.user.structures.all()).order_by("-date_fin")
        self.fields['individu'].queryset = Individu.objects.filter(statut=5)

        user = self.request.user.pk
        print(user)
        self.fields['auteur'].initial = user
        self.fields['auteur'].disabled = True


        # Layout du formulaire
        self.helper.layout = Layout(
            Commandes(annuler_url="{% url 'traitement_liste' %}"),

            Fieldset("Informations générales",
                     Field('date'),
                     Field('auteur'),
                     Field('individu'),
                     Field('activite'),
                     Field('titre'),
                     Field('typemaladie'),

            ),
            Fieldset("Informations sur le traitement",
                     Field('Description'),
            ),
        )