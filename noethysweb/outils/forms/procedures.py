# -*- coding: utf-8 -*-
#  Copyright (c) 2019-2021 Ivan LUCAS.
#  Noethysweb, application de gestion multi-activités.
#  Distribué sous licence GNU GPL.

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from crispy_forms.bootstrap import Field
from core.forms.base import FormulaireBase
from core.forms.select2 import Select2MultipleWidget
from core.models import Activite, Structure


class Formulaire(FormulaireBase, forms.Form):
    commande = forms.CharField(label="", required=True)
    activite = forms.ModelMultipleChoiceField(label="Activité", widget=Select2MultipleWidget(), queryset=Activite.objects.filter(visible=True), required=False)
    structure = forms.ModelMultipleChoiceField(label="Structure", widget=Select2MultipleWidget(), queryset=Structure.objects.filter(visible=True), required=False)

    def __init__(self, *args, **kwargs):
        super(Formulaire, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'form_procedures'
        self.helper.form_method = 'post'
        self.helper.form_tag = False

        self.helper.layout = Layout(
            Field("commande"),
            Field("activite"),
            Field("structure"),
        )
