# -*- coding: utf-8 -*-
#  Copyright (c) 2019-2021 Ivan LUCAS.
#  Noethysweb, application de gestion multi-activités.
#  Distribué sous licence GNU GPL.

import datetime
from django import forms
from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from core.forms.base import FormulaireBase
from core.utils.utils_commandes import Commandes
from core.models import Depot, Reglement, Activite, ModeReglement
from core.widgets import DatePickerWidget, SelectionActivitesWidget
from core.forms.select2 import Select2Widget
from core.forms.base import FormulaireBase
from crispy_forms.layout import Layout, Hidden, Submit, HTML, Row, Column, Fieldset, Div, ButtonHolder,Field
from crispy_forms.bootstrap import Field
from core.forms.base import FormulaireBase
class Formulaire(FormulaireBase, forms.Form):
    activite = forms.ModelChoiceField(label="Activité", queryset=Activite.objects.none(), initial=None, required=False)
    mode_regl = forms.ModelChoiceField(label="Mode de règlement", queryset=ModeReglement.objects.all(), initial=None, required=False, widget=forms.Select(attrs={'id': 'id_mode_regl'}))
    export = forms.BooleanField(required=False,label="Affichage pour export compta", widget=forms.CheckboxInput(attrs={'id': 'id_export'}))


    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super(Formulaire, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'form_parametres'
        self.helper.form_method = 'post'
        user = request.user
        self.fields['activite'].queryset = Activite.objects.filter(structure__in=user.structures.all(), visible=1)
        # Affichage
        self.helper.layout = Layout(
            Field('export'),
            Field('activite'),
            Field('mode_regl'),
            HTML(EXTRA_SCRIPT),
        )


EXTRA_SCRIPT = """
<script>
    $(document).ready(function() {
        function toggleModeReglVisibility() {
            if ($('#id_export').is(':checked')) {
                $('#id_mode_regl').hide(); // Masquer le champ
                $('label[for="id_mode_regl"]').hide(); // Masquer le label
            } else {
                $('#id_mode_regl').show(); // Afficher le champ
                $('label[for="id_mode_regl"]').show(); // Afficher le label
            }
        }

        // Appeler la fonction au chargement de la page
        toggleModeReglVisibility();

        // Appeler la fonction lorsque la checkbox export change
        $('#id_export').change(function() {
            toggleModeReglVisibility();
        });
    });
</script>
"""