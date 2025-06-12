# -*- coding: utf-8 -*-
#  Copyright (c) 2019-2021 Ivan LUCAS.
#  Noethysweb, application de gestion multi-activités.
#  Distribué sous licence GNU GPL.

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from crispy_forms.bootstrap import Field
from core.forms.base import FormulaireBase
from core.forms.select2 import Select2Widget
from core.models import Activite, Structure, Tarif

class TarifChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.activite.nom} - {obj.description}"
class Formulaire(FormulaireBase, forms.Form):
    commande = forms.CharField(label="", required=True)
    activite = forms.ModelChoiceField(label="Activité", widget=Select2Widget(), queryset=Activite.objects.none(), required=False)
    structure = forms.ModelChoiceField(label="Structure", widget=Select2Widget(), queryset=Structure.objects.filter(visible=True), required=False)
    tarif = TarifChoiceField(
        label="Tarif",
        queryset=Tarif.objects.all(),  # ou un filtre si besoin
        required=False,
        widget=Select2Widget()
    )
    def __init__(self, *args, **kwargs):
        super(Formulaire, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'form_procedures'
        self.helper.form_method = 'post'
        self.helper.form_tag = False
        user_structures = self.request.user.structures.all()
        activites_user = Activite.objects.filter(structure__in=user_structures)
        self.fields["activite"].queryset = Activite.objects.filter(structure__in=self.request.user.structures.all())
        condition = Activite.objects.filter(structure__in=self.request.user.structures.all())
        self.fields["tarif"].queryset = Tarif.objects.filter(activite__in=activites_user).select_related("activite")

        self.helper.layout = Layout(
            Field("commande"),
            Field("activite"),
            Field("structure"),
            Field("tarif"),
        )
