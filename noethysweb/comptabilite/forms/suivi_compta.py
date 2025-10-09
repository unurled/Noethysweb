# -*- coding: utf-8 -*-
#  Copyright (c) 2019-2021 Ivan LUCAS.
#  Noethysweb, application de gestion multi-activités.
#  Distribué sous licence GNU GPL.

from django import forms
from django.db.models import Q
from django_select2.forms import ModelSelect2Widget
from core.forms.select2 import Select2MultipleWidget
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from crispy_forms.bootstrap import Field
from core.models import ComptaBudget, CompteBancaire
from core.forms.base import FormulaireBase

class Formulaire(FormulaireBase, forms.Form):
    comptes = forms.ModelMultipleChoiceFieldCompte(
        label="Comptes bancaires",
        queryset=CompteBancaire.objects.all(),
        widget=Select2MultipleWidget(),
        required=True
        )


    def __init__(self, *args, **kwargs):
        super(Formulaire, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'form_parametres'
        self.helper.form_method = 'post'

        condition_structure = Q(structure__in=self.request.user.structures.all()) | Q(structure__isnull=True)
        self.fields["comptes"].queryset = CompteBancaire.objects.filter(condition_structure).order_by("nom")

        self.helper.layout = Layout(
            Field("comptes"),
        )
