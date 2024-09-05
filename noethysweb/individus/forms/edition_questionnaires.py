# -*- coding: utf-8 -*-
#  Copyright (c) 2019-2021 Ivan LUCAS.
#  Noethysweb, application de gestion multi-activités.
#  Distribué sous licence GNU GPL.

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, HTML, Fieldset, Hidden
from crispy_forms.bootstrap import Field
from core.forms.select2 import Select2MultipleWidget, Select2Widget
from core.models import Rattachement, QuestionnaireQuestion, QuestionnaireReponse
from core.utils.utils_commandes import Commandes
from core.forms.base import FormulaireBase
from core.widgets import FormIntegreWidget


class UpdateResponseForm(forms.ModelForm):
    class Meta:
        model = QuestionnaireReponse
        fields = ['reponse']

class Formulaire(FormulaireBase, forms.Form):
    reponse = forms.BooleanField(required=False,label="Affichage pour export compta", widget=forms.CheckboxInput(attrs={'id': 'id_export'}))
    question = forms.ModelChoiceField(label="Question", widget=Select2Widget(), queryset=QuestionnaireQuestion.objects.filter(categorie="individu"),empty_label="Sélectionnez une question",required=True)

    def __init__(self, *args, **kwargs):
        idfamille = kwargs.pop("idfamille", None)
        super(Formulaire, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'form_parametres'
        self.helper.form_method = 'post'

        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-2'
        self.helper.field_class = 'col-md-10'

        self.helper.layout = Layout(
            Commandes(annuler_url="{% url 'individus_toc' %}", enregistrer=False, ajouter=False,
                      commandes_principales=[HTML(
                          """<a type='button' class="btn btn-primary margin-r-5" onclick="generer_pdf()" title="Modifier les réponse"></i>Modifier les réponses</a>"""),
                      ]),
            Fieldset("Options",
                Field("question"),
                Field("reponse"),
            ),
            Fieldset("Sélection des individus"),
        )